from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import (
    and_,
    delete,
    func,
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


def get_sorted_tickets_related_to_service_and_package_and_vuln(
    db: Session,
    service_id: UUID | str | None,
    package_id: UUID | str | None,
    vuln_id: UUID | str | None,
) -> Sequence[models.Ticket]:
    select_stmt = (
        select(models.Ticket)
        .options(
            joinedload(models.Ticket.ticket_status, innerjoin=True).joinedload(
                models.TicketStatus.action_logs, innerjoin=False
            ),
        )
        .join(
            models.Threat,
            models.Threat.threat_id == models.Ticket.threat_id,
        )
    )

    if vuln_id:
        select_stmt = select_stmt.where(models.Threat.vuln_id == str(vuln_id))
    if package_id:
        select_stmt = select_stmt.join(
            models.PackageVersion,
            and_(
                models.PackageVersion.package_version_id == models.Threat.package_version_id,
                models.PackageVersion.package_id == str(package_id),
            ),
        )
    if service_id:
        select_stmt = select_stmt.join(
            models.Dependency,
            and_(
                models.Dependency.dependency_id == models.Ticket.dependency_id,
                models.Dependency.service_id == str(service_id),
            ),
        )

    select_stmt = select_stmt.order_by(
        models.Ticket.ssvc_deployer_priority, models.Ticket.created_at
    )

    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading
    return db.scalars(select_stmt).unique().all()


def get_vulns(
    db: Session,
    offset: int,
    limit: int,
) -> Sequence[models.Vuln]:
    select_stmt = (
        select(models.Vuln)
        .options(joinedload(models.Vuln.affects))
        .order_by(models.Vuln.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return db.scalars(select_stmt).unique().all()


def get_packages_summary(
    db: Session, pteam_id: UUID | str, service_id: UUID | str | None
) -> list[dict]:
    unsolved_subq = (
        select(
            models.Ticket.dependency_id,
            models.Ticket.ssvc_deployer_priority,
            models.Vuln.updated_at,
        )
        .join(
            models.TicketStatus,
            and_(
                models.TicketStatus.ticket_id == models.Ticket.ticket_id,
                models.TicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .join(models.Threat)
        .join(models.Vuln)
        .subquery()
    )
    min_unsolved_ssvc_priority = func.min(unsolved_subq.c.ssvc_deployer_priority).label(
        "min_ssvc_priority"
    )
    max_unsolved_updated_at = func.max(unsolved_subq.c.updated_at).label("max_updated_at")
    service_ids = func.array_agg(models.Service.service_id.distinct()).label("service_ids")
    summarize_stmt = (
        select(
            models.Package.package_id,
            models.Package.name,
            models.Package.ecosystem,
            models.Dependency.package_manager,
            min_unsolved_ssvc_priority,
            max_unsolved_updated_at,
            service_ids,
        )
        .join(models.PackageVersion, models.PackageVersion.package_id == models.Package.package_id)
        .join(
            models.Dependency,
            models.Dependency.package_version_id == models.PackageVersion.package_version_id,
        )
        .join(
            models.Service,
            and_(
                models.Service.service_id == models.Dependency.service_id,
                models.Service.pteam_id == str(pteam_id),
            ),
        )
        .outerjoin(
            unsolved_subq,
            unsolved_subq.c.dependency_id == models.Dependency.dependency_id,
        )
        .group_by(models.Package.package_id)
        .order_by(
            min_unsolved_ssvc_priority.nullslast(),
            max_unsolved_updated_at.desc().nullslast(),
            models.Package.name,
            models.Package.ecosystem,
            models.Dependency.package_manager,
        )
    )

    if service_id is not None:
        summarize_stmt = summarize_stmt.where(models.Dependency.service_id == str(service_id))

    count_status_stmt = (
        select(
            models.Package.package_id,
            models.TicketStatus.topic_status,
            func.count(models.TicketStatus.topic_status).label("num_status"),
        )
        .join(models.PackageVersion)
        .join(models.Dependency)
        .join(
            models.Service,
            and_(
                models.Service.service_id == models.Dependency.service_id,
                models.Service.pteam_id == str(pteam_id),
            ),
        )
        .join(models.Ticket)
        .join(models.TicketStatus)
        .group_by(
            models.Package.package_id,
            models.TicketStatus.topic_status,
        )
    )

    if service_id is not None:
        count_status_stmt = count_status_stmt.where(models.Dependency.service_id == str(service_id))

    status_count_dict = {
        (row.package_id, row.topic_status): row.num_status
        for row in db.execute(count_status_stmt).all()
    }
    summary = [
        {
            "package_id": row.package_id,
            "name": row.name,
            "ecosystem": row.ecosystem,
            "package_manager": row.package_manager,
            "ssvc_priority": row.min_ssvc_priority,
            "updated_at": row.max_updated_at,
            "service_ids": row.service_ids,
            "status_count": {
                status_type.value: status_count_dict.get((row.package_id, status_type.value), 0)
                for status_type in list(models.TopicStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]

    return summary
