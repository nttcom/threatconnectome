from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.constants import SYSTEM_UUID

### Account


def get_account_by_firebase_uid(db: Session, uid: str) -> models.Account | None:
    return db.scalars(select(models.Account).where(models.Account.uid == uid)).one_or_none()


def get_account_by_id(db: Session, user_id: UUID | str) -> models.Account | None:
    return db.scalars(
        select(models.Account).where(models.Account.user_id == str(user_id))
    ).one_or_none()


def get_account_by_email(db: Session, email: str) -> models.Account | None:
    return db.scalars(select(models.Account).where(models.Account.email == email)).first()


def get_system_account(db: Session) -> models.Account:
    return db.scalars(
        select(models.Account).where(models.Account.user_id == str(SYSTEM_UUID))
    ).one()


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


def create_action(db: Session, action: models.TopicAction) -> None:
    db.add(action)
    db.flush()


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
                    select(models.PTeamAccount.pteam_id).where(
                        models.PTeamAccount.user_id == str(user_id)
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
                    select(models.PTeamAccount.pteam_id).where(
                        models.PTeamAccount.user_id == str(user_id)
                    )
                )
            ),
        )
    ).all()


### ATeam


def get_ateam_by_id(db: Session, ateam_id: UUID | str) -> models.ATeam | None:
    return db.scalars(
        select(models.ATeam).where(models.ATeam.ateam_id == str(ateam_id))
    ).one_or_none()


def get_all_ateams(db: Session) -> Sequence[models.ATeam]:
    return db.scalars(select(models.ATeam)).all()


def create_ateam(db: Session, ateam: models.ATeam) -> None:
    db.add(ateam)
    db.flush()


def get_ateam_invitation_by_id(
    db: Session,
    invitation_id: UUID | str,
) -> models.ATeamInvitation | None:
    return db.scalars(
        select(models.ATeamInvitation).where(
            models.ATeamInvitation.invitation_id == str(invitation_id)
        )
    ).one_or_none()


def create_ateam_invitation(db: Session, invitation: models.ATeamInvitation) -> None:
    db.add(invitation)
    db.flush()


def delete_ateam_invitation(db: Session, invitation: models.ATeamInvitation) -> None:
    db.delete(invitation)
    db.flush()


def get_ateam_watching_request_by_id(
    db: Session,
    request_id: UUID | str,
) -> models.ATeamWatchingRequest | None:
    return db.scalars(
        select(models.ATeamWatchingRequest).where(
            models.ATeamWatchingRequest.request_id == str(request_id)
        )
    ).one_or_none()


def create_ateam_watching_request(db: Session, request: models.ATeamWatchingRequest) -> None:
    db.add(request)
    db.flush()


def delete_ateam_watching_request(db: Session, request: models.ATeamWatchingRequest) -> None:
    db.delete(request)
    db.flush()


### ATeamAuthority


def get_ateam_authority(
    db: Session,
    ateam_id: UUID | str,
    user_id: UUID | str,
) -> models.ATeamAuthority | None:
    return db.scalars(
        select(models.ATeamAuthority).where(
            models.ATeamAuthority.ateam_id == str(ateam_id),
            models.ATeamAuthority.user_id == str(user_id),
        )
    ).one_or_none()


def get_ateam_all_authorities(db: Session, ateam_id: UUID | str) -> Sequence[models.ATeamAuthority]:
    return db.scalars(
        select(models.ATeamAuthority).where(models.ATeamAuthority.ateam_id == str(ateam_id))
    ).all()


def create_ateam_authority(db: Session, auth: models.ATeamAuthority) -> None:
    db.add(auth)
    db.flush()


### ATeamTopicComment


def create_ateam_topic_comment(db: Session, comment: models.ATeamTopicComment) -> None:
    db.add(comment)
    db.flush()


def delete_ateam_topic_comment(db: Session, comment: models.ATeamTopicComment) -> None:
    db.delete(comment)
    db.flush()


def get_ateam_topic_comment_by_id(
    db: Session, comment_id: UUID | str
) -> models.ATeamTopicComment | None:
    return db.scalars(
        select(models.ATeamTopicComment).where(
            models.ATeamTopicComment.comment_id == str(comment_id)
        )
    ).one_or_none()


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


### PTeamAuthority # TODO: should obsolete direct access?


def get_pteam_authority(
    db: Session,
    pteam_id: UUID | str,
    user_id: UUID | str,
) -> models.PTeamAuthority | None:
    return db.scalars(
        select(models.PTeamAuthority).where(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            models.PTeamAuthority.user_id == str(user_id),
        )
    ).one_or_none()


def get_pteam_all_authorities(db: Session, pteam_id: UUID | str) -> Sequence[models.PTeamAuthority]:
    return db.scalars(
        select(models.PTeamAuthority).where(models.PTeamAuthority.pteam_id == str(pteam_id))
    ).all()


def create_pteam_authority(db: Session, auth: models.PTeamAuthority) -> None:
    db.add(auth)
    db.flush()


### PTeamTopicTagStatus


def create_pteam_topic_tag_status(db: Session, status: models.PTeamTopicTagStatus) -> None:
    db.add(status)
    db.flush()


def get_pteam_topic_tag_status_by_id(
    db: Session,
    status_id: UUID | str,
) -> models.PTeamTopicTagStatus | None:
    return db.scalars(
        select(models.PTeamTopicTagStatus).where(
            models.PTeamTopicTagStatus.status_id == str(status_id)
        )
    ).one_or_none()


### CurrentPTeamTopicTagStatus


def create_current_pteam_topic_tag_status(
    db: Session,
    status: models.CurrentPTeamTopicTagStatus,
) -> None:
    db.add(status)
    db.flush()


def get_current_pteam_topic_tag_status(
    db: Session,
    pteam_id: UUID | str,
    topic_id: UUID | str,
    tag_id: UUID | str,  # should be PTeamTag, not TopicTag
) -> models.CurrentPTeamTopicTagStatus | None:
    return db.scalars(
        select(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
        )
    ).one_or_none()


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
