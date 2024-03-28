from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.common import (
    check_pteam_membership,
)
from app.database import get_db

router = APIRouter(prefix="/actionlogs", tags=["actionlogs"])


@router.get("", response_model=list[schemas.ActionLogResponse])
def get_logs(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get actionlogs of pteams the user belongs to.
    """
    logs = persistence.get_action_logs_by_user_id(db, current_user.user_id)
    result = []
    for log in sorted(logs, key=lambda l: l.executed_at, reverse=True):
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
    if not (pteam := persistence.get_pteam_by_id(db, data.pteam_id)) or pteam.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such pteam")
    if not check_pteam_membership(db, pteam, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")
    if not (user := persistence.get_account_by_id(db, data.user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    if not check_pteam_membership(db, pteam, user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a pteam member")
    if not (topic := persistence.get_topic_by_id(db, data.topic_id)) or topic.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such topic")
    if str(data.topic_id) not in command.get_pteam_topic_ids(db, data.pteam_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a pteam topic")
    if not (
        topic_action := persistence.get_action_by_id(db, data.action_id)
    ) or topic_action.topic_id != str(data.topic_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action id")

    now = datetime.now()
    log = models.ActionLog(
        action_id=data.action_id,
        topic_id=data.topic_id,
        action=topic_action.action,
        action_type=topic_action.action_type,
        recommended=topic_action.recommended,
        user_id=data.user_id,
        pteam_id=data.pteam_id,
        email=user.email,
        executed_at=data.executed_at or now,
        created_at=now,
    )
    persistence.create_action_log(db, log)

    db.commit()
    db.refresh(log)

    return log


@router.get("/topics/{topic_id}", response_model=list[schemas.ActionLogResponse])
def get_topic_logs(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actionlogs associated with the specified topic.
    """
    topic = persistence.get_topic_by_id(db, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
    assert topic
    rows = persistence.get_topic_logs_by_user_id(db, topic_id, current_user.user_id)
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)
