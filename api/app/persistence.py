from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models

### Account


def get_account_by_uid(db: Session, uid: str) -> models.Account | None:
    return db.scalars(select(models.Account).where(models.Account.uid == uid)).one_or_none()


def get_account_by_id(db: Session, user_id: UUID | str) -> models.Account | None:
    return db.scalars(
        select(models.Account).where(models.Account.user_id == str(user_id))
    ).one_or_none()


def get_account_by_email(db: Session, email: str) -> models.Account | None:
    return db.scalars(select(models.Account).where(models.Account.email == email)).first()


def create_account(db: Session, account: models.Account) -> None:
    db.add(account)
    db.flush()


def delete_account(db: Session, account: models.Account) -> None:
    db.delete(account)
    db.flush()


### Action


def get_action_by_id(db: Session, action_id: UUID | str) -> models.TopicAction | None:
    return db.scalars(
        select(models.TopicAction).where(models.TopicAction.action_id == str(action_id))
    ).one_or_none()


def get_actions_by_topic_id(db: Session, topic_id: UUID | str) -> Sequence[models.TopicAction]:
    return db.scalars(
        select(models.TopicAction).where(models.TopicAction.topic_id == str(topic_id))
    ).all()


def delete_action(db: Session, action: models.TopicAction) -> None:
    db.delete(action)
    db.flush()


### ActionLog


def get_action_log_by_id(db: Session, logging_id: UUID | str) -> models.ActionLog | None:
    return db.scalars(
        select(models.ActionLog).where(models.ActionLog.logging_id == str(logging_id))
    ).one_or_none()


def get_action_logs_by_user_id(db: Session, user_id: UUID | str) -> Sequence[models.ActionLog]:
    return db.scalars(
        select(models.ActionLog).where(
            models.ActionLog.pteam_id.in_(
                db.scalars(
                    select(models.PTeamAccountRole.pteam_id).where(
                        models.PTeamAccountRole.user_id == str(user_id)
                    )
                )
            )
        )
    ).all()


def create_action_log(db: Session, action_log: models.ActionLog) -> None:
    db.add(action_log)
    db.flush()


def get_topic_logs_by_user_id(
    db: Session,
    topic_id: UUID | str,
    user_id: UUID | str,
) -> Sequence[models.ActionLog]:
    return db.scalars(
        select(models.ActionLog).where(
            models.ActionLog.topic_id == str(topic_id),
            models.ActionLog.pteam_id.in_(
                db.scalars(
                    select(models.PTeamAccountRole.pteam_id).where(
                        models.PTeamAccountRole.user_id == str(user_id)
                    )
                )
            ),
        )
    ).all()


### PTeam


def get_all_pteams(db: Session) -> Sequence[models.PTeam]:
    return db.scalars(select(models.PTeam)).all()


def get_pteam_by_id(db: Session, pteam_id: UUID | str) -> models.PTeam | None:
    return db.scalars(
        select(models.PTeam).where(models.PTeam.pteam_id == str(pteam_id))
    ).one_or_none()


def create_pteam(db: Session, pteam: models.PTeam) -> None:
    db.add(pteam)
    db.flush()


def delete_pteam(db: Session, pteam: models.PTeam) -> None:
    db.delete(pteam)
    db.flush()


### PTeamInvitation


def get_pteam_invitations(
    db: Session,
    pteam_id: UUID | str,
) -> Sequence[models.PTeamInvitation]:
    return db.scalars(
        select(models.PTeamInvitation).where(models.PTeamInvitation.pteam_id == str(pteam_id))
    ).all()


def get_pteam_invitation_by_id(
    db: Session,
    invitation_id: UUID | str,
) -> models.PTeamInvitation | None:
    return db.scalars(
        select(models.PTeamInvitation).where(
            models.PTeamInvitation.invitation_id == str(invitation_id)
        )
    ).one_or_none()


def create_pteam_invitation(db: Session, invitation: models.PTeamInvitation) -> None:
    db.add(invitation)
    db.flush()


def delete_pteam_invitation(db: Session, invitation: models.PTeamInvitation) -> None:
    db.delete(invitation)
    db.flush()


### PTeamAccountRole


def get_pteam_account_role(
    db: Session, pteam_id: UUID | str, user_id: UUID | str
) -> models.PTeamAccountRole | None:
    return db.scalars(
        select(models.PTeamAccountRole).where(
            models.PTeamAccountRole.pteam_id == str(pteam_id),
            models.PTeamAccountRole.user_id == str(user_id),
        )
    ).one_or_none()


def create_pteam_account_role(db: Session, account_role: models.PTeamAccountRole) -> None:
    db.add(account_role)
    db.flush()


### Artifact Tag


def get_all_tags(db: Session) -> Sequence[models.Tag]:
    return db.scalars(select(models.Tag)).all()


def get_tag_by_id(db: Session, tag_id: UUID | str) -> models.Tag | None:
    return db.scalars(select(models.Tag).where(models.Tag.tag_id == str(tag_id))).one_or_none()


def get_tag_by_name(db: Session, tag_name: str) -> models.Tag | None:
    return db.scalars(select(models.Tag).where(models.Tag.tag_name == tag_name)).one_or_none()


def create_tag(db: Session, tag: models.Tag) -> None:
    db.add(tag)
    db.flush()


def delete_tag(db: Session, tag: models.Tag):
    db.delete(tag)
    db.flush()


### MispTag


def get_all_misp_tags(db: Session) -> Sequence[models.MispTag]:
    return db.scalars(select(models.MispTag)).all()


def get_misp_tag_by_name(db: Session, tag_name: str) -> models.MispTag | None:
    return db.scalars(
        select(models.MispTag).where(models.MispTag.tag_name == tag_name)
    ).one_or_none()


def create_misp_tag(db: Session, misptag: models.MispTag) -> None:
    db.add(misptag)
    db.flush()


### Topic


def get_all_topics(db: Session) -> Sequence[models.Topic]:
    return db.scalars(select(models.Topic)).all()


def get_topics_by_tag_ids(db: Session, tag_ids: Sequence[UUID | str]) -> Sequence[models.Topic]:
    return db.scalars(
        select(models.Topic)
        .join(models.TopicTag)
        .where(models.TopicTag.tag_id.in_(list(map(str, tag_ids))))
        .distinct()
    ).all()


def get_topic_by_id(db: Session, topic_id: UUID | str) -> models.Topic | None:
    return db.scalars(
        select(models.Topic).where(models.Topic.topic_id == str(topic_id))
    ).one_or_none()


def create_topic(db: Session, topic: models.Topic):
    db.add(topic)
    db.flush()


def delete_topic(db: Session, topic: models.Topic):
    db.delete(topic)
    db.flush()


### Threat


def create_threat(db: Session, threat: models.Threat) -> None:
    db.add(threat)
    db.flush()


def delete_threat(db: Session, threat: models.Threat) -> None:
    db.delete(threat)
    db.flush()


def get_threat_by_id(db: Session, threat_id: UUID | str) -> models.Threat | None:
    return db.scalars(
        select(models.Threat).where(models.Threat.threat_id == str(threat_id))
    ).one_or_none()


### Ticket


def create_ticket(db: Session, ticket: models.Ticket) -> None:
    db.add(ticket)
    db.flush()


def delete_ticket(db: Session, ticket: models.Ticket) -> None:
    db.delete(ticket)
    db.flush()


def get_ticket_by_id(db: Session, ticket_id: UUID | str) -> models.Ticket | None:
    return db.scalars(
        select(models.Ticket).where(models.Ticket.ticket_id == str(ticket_id))
    ).one_or_none()


### TicketStatus


def create_ticket_status(
    db: Session,
    status: models.TicketStatus,
) -> None:
    db.add(status)
    db.flush()


### Service


def get_service_by_id(db: Session, service_id: UUID | str) -> models.Service | None:
    return db.scalars(
        select(models.Service).where(models.Service.service_id == str(service_id))
    ).one_or_none()


### Dependency


def get_dependency_from_service_id_and_tag_id(
    db: Session, service_id: UUID | str, tag_id: UUID | str
) -> models.Dependency | None:
    return db.scalars(
        select(models.Dependency).where(
            models.Dependency.service_id == str(service_id),
            models.Dependency.tag_id == str(tag_id),
        )
    ).first()  # FIXME: WORKAROUND to avoid getting multiple row


### Alert


def create_alert(db: Session, alert: models.Alert) -> None:
    db.add(alert)
    db.flush()
