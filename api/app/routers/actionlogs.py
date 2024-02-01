from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    check_pteam_membership,
    check_zone_accessible,
    create_actionlog_internal,
    create_secbadge_from_actionlog_internal,
    get_metadata_internal,
    validate_topic,
)
from app.database import get_db
from app.models import ActionType

router = APIRouter(prefix="/actionlogs", tags=["actionlogs"])


@router.get("/{logging_id}/metadata", response_model=schemas.BadgeRequest)
def get_metadata(
    logging_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get metadata from the specified actionlog to create secbadge.
    Secbadge can only be issued with actionlog that have action_type of elimination or mitigation.
    """
    return get_metadata_internal(logging_id, current_user, db)


@router.post("/{logging_id}/achievement", response_model=schemas.SecBadgeBody)
def create_secbadge_from_actionlog(
    logging_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create secbadge from the actionlog.
    Secbadge can only be issued with actionlog that have action_type of elimination or mitigation.
    """
    return create_secbadge_from_actionlog_internal(logging_id, current_user, db)


@router.get("", response_model=List[schemas.ActionLogResponse])
def get_logs(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get actionlogs of pteams the user belongs to.
    """
    logs = (
        db.query(models.ActionLog)
        .filter(
            models.ActionLog.pteam_id.in_(
                db.query(models.PTeamAccount.pteam_id).filter(
                    models.PTeamAccount.user_id == current_user.user_id
                )
            )
        )
        .order_by(desc(models.ActionLog.created_at))
        .all()
    )
    result = []
    for log in logs:
        if log.created_at:
            log.created_at = log.created_at.astimezone(timezone.utc)
        if log.executed_at:
            log.executed_at = log.executed_at.astimezone(timezone.utc)
        result.append(log.__dict__)
    return result


@router.post("", response_model=schemas.ActionLogResponse)
def create_log(
    data: schemas.ActionLogRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add an action log to the topic.

    `executed_at` is optional, the default is the current time in the server.

    The format of `executed_at` is ISO-8601.
    In linux, you can check it with `date --iso-8601=seconds`.
    """
    return create_actionlog_internal(data, current_user, db)


@router.get("/topics/{topic_id}", response_model=List[schemas.ActionLogResponse])
def get_topic_logs(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actionlogs associated with the specified topic.
    """
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)
    rows = (
        db.query(models.ActionLog)
        .filter(
            models.ActionLog.topic_id == str(topic_id),
            models.ActionLog.pteam_id.in_(
                db.query(models.PTeamAccount.pteam_id).filter(
                    models.PTeamAccount.user_id == current_user.user_id
                )
            ),
        )
        .all()
    )
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)


@router.get("/search", response_model=List[schemas.ActionLogResponse])
def search_logs(
    topic_ids: Optional[List[UUID]] = Query(None),
    action_words: Optional[List[str]] = Query(None),
    action_types: Optional[List[ActionType]] = Query(None),
    user_ids: Optional[List[UUID]] = Query(None),
    pteam_ids: Optional[List[UUID]] = Query(None),
    emails: Optional[List[str]] = Query(None),
    executed_before: Optional[datetime] = Query(None),
    executed_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    created_after: Optional[datetime] = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search actionlogs.
    """
    if pteam_ids is None:
        pteam_ids = [pteam.pteam_id for pteam in current_user.pteams]
    else:
        for pteam_id in pteam_ids:
            check_pteam_membership(
                db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN
            )
    rows = (
        db.query(models.ActionLog)
        .filter(
            (
                true()
                if topic_ids is None
                else models.ActionLog.topic_id.in_(list(map(str, topic_ids)))
            ),
            (
                true()
                if action_words is None
                else models.ActionLog.action.bool_op("@@")(func.to_tsquery("|".join(action_words)))
            ),
            true() if action_types is None else models.ActionLog.action_type.in_(action_types),
            true() if user_ids is None else models.ActionLog.user_id.in_(list(map(str, user_ids))),
            models.ActionLog.pteam_id.in_(list(map(str, pteam_ids))),
            true() if emails is None else models.ActionLog.email.in_(emails),
            true() if executed_before is None else models.ActionLog.executed_at < executed_before,
            true() if executed_after is None else models.ActionLog.executed_at >= executed_after,
            true() if created_before is None else models.ActionLog.created_at < created_before,
            true() if created_after is None else models.ActionLog.created_at >= created_after,
        )
        .all()
    )
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)
