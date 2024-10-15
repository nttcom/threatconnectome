from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth import get_current_user
from app.data_checker.account_checker import check_and_get_account
from app.data_checker.service_checker import check_and_get_pteam_and_service
from app.data_checker.ticket_checker import check_and_get_ticket
from app.data_checker.topic_checker import check_and_get_topic
from app.database import get_db
from app.routers.validators.account_validator import validate_pteam_membership

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
    pteam = check_and_get_pteam_and_service(db, data.pteam_id, data.service_id)[0]
    if not validate_pteam_membership(pteam, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")
    check_and_get_ticket(db, data.service_id, data.ticket_id)
    user = check_and_get_account(db, data.user_id)
    if not validate_pteam_membership(pteam, user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a pteam member")
    check_and_get_topic(db, data.topic_id)
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
        service_id=data.service_id,
        ticket_id=data.ticket_id,
        email=user.email,
        executed_at=data.executed_at or now,
        created_at=now,
    )
    persistence.create_action_log(db, log)

    db.commit()

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
    check_and_get_topic(db, topic_id)
    rows = persistence.get_topic_logs_by_user_id(db, topic_id, current_user.user_id)
    return sorted(rows, key=lambda x: x.executed_at, reverse=True)
