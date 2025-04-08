from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import (
    and_,
    delete,
    or_,
    select,
)
from sqlalchemy.orm import Session, joinedload

from app import models


def missing_pteam_admin(db: Session, pteam: models.PTeam) -> bool:
    return (
        db.execute(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.pteam_id == pteam.pteam_id,
                models.PTeamAccountRole.is_admin.is_(True),
            )
        ).first()
        is None
    )


def search_threats(
    db: Session,
    service_id: UUID | str | None,
    dependency_id: UUID | str | None,
    topic_id: UUID | str | None,
    user_id: UUID | str | None = None,
) -> Sequence[models.Threat]:
    select_stmt = select(models.Threat)

    select_stmt = (
        select_stmt.join(models.Dependency)
        .join(models.Service)
        .join(models.PTeam)
        .join(models.PTeamAccountRole)
        .join(models.Account)
    )

    if user_id:
        select_stmt = select_stmt.where(models.Account.user_id == str(user_id))

    if service_id:
        select_stmt = select_stmt.where(models.Dependency.service_id == str(service_id))
    if dependency_id:
        select_stmt = select_stmt.where(models.Threat.dependency_id == str(dependency_id))
    if topic_id:
        select_stmt = select_stmt.where(models.Threat.topic_id == str(topic_id))

    return db.scalars(select_stmt).all()


def expire_pteam_invitations(db: Session) -> None:
    db.execute(
        delete(models.PTeamInvitation).where(
            or_(
                models.PTeamInvitation.expiration < datetime.now(),
                and_(
                    models.PTeamInvitation.limit_count.is_not(None),
                    models.PTeamInvitation.limit_count <= models.PTeamInvitation.used_count,
                ),
            ),
        )
    )
    db.flush()


def get_sorted_tickets_related_to_service_and_topic_and_tag(
    db: Session,
    service_id: UUID | str,
    topic_id: UUID | str,
    tag_id: UUID | str,
) -> Sequence[models.Ticket]:
    select_stmt = (
        select(models.Ticket)
        .options(
            joinedload(models.Ticket.ticket_status, innerjoin=True).joinedload(
                models.TicketStatus.action_logs, innerjoin=False
            ),
            joinedload(models.Ticket.threat, innerjoin=True),
        )
        .join(
            models.Threat,
            and_(
                models.Threat.threat_id == models.Ticket.threat_id,
                models.Threat.topic_id == str(topic_id),
            ),
        )
        .join(
            models.Dependency,
            and_(
                models.Dependency.dependency_id == models.Threat.dependency_id,
                models.Dependency.service_id == str(service_id),
                models.Dependency.tag_id == str(tag_id),
            ),
        )
        .order_by(models.Ticket.ssvc_deployer_priority, models.Dependency.target)
    )
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading
    return db.scalars(select_stmt).unique().all()
