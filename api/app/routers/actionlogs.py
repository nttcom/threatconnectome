from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.common import (
    check_pteam_membership,
)
from app.database import get_db
from app.models import ActionType

router = APIRouter(prefix="/actionlogs", tags=["actionlogs"])


@router.get("", response_model=List[schemas.ActionLogResponse])
def get_logs(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get actionlogs of pteams the user belongs to.
    """
    logs = persistence.get_action_logs(db, current_user.user_id)
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
        topic_action := persistence.get_action(db, data.action_id)
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
            pteam = persistence.get_pteam_by_id(db, pteam_id)
            if check_pteam_membership(db, pteam, current_user) is False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member"
                )

    rows = persistence.search_logs(
        db,
        topic_ids,
        action_words,
        action_types,
        user_ids,
        pteam_ids,
        emails,
        executed_before,
        executed_after,
        created_before,
        created_after,
    )
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)


@router.get("/topics/{topic_id}", response_model=List[schemas.ActionLogResponse])
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
    rows = persistence.get_topic_logs(db, topic_id, current_user.user_id)
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)
