from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.database import get_db
from app.routers.validators.account_validator import check_pteam_membership

router = APIRouter(prefix="/actionlogs", tags=["actionlogs"])


@router.get("", response_model=list[schemas.ActionLogResponse])
def get_logs(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get actionlogs of pteams the user belongs to.
    """
    logs = persistence.get_action_logs_by_user_id(db, current_user.user_id)

    return sorted(logs, key=lambda l: l.executed_at, reverse=True)


@router.post("", response_model=schemas.ActionLogResponse)
def create_log(
    data: schemas.ActionLogRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add an action log to the vuln.

    `executed_at` is optional, the default is the current time in the server.

    The format of `executed_at` is ISO-8601.
    In linux, you can check it with `date --iso-8601=seconds`.
    """
    if not (pteam := persistence.get_pteam_by_id(db, data.pteam_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such pteam")
    if not next(filter(lambda x: x.service_id == str(data.service_id), pteam.services), None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
    if not check_pteam_membership(pteam, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")
    if not (
        ticket := persistence.get_ticket_by_id(db, data.ticket_id)
    ) or ticket.dependency.service_id != str(data.service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ticket")
    if not (user := persistence.get_account_by_id(db, data.user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    if not check_pteam_membership(pteam, user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a pteam member")
    if not (persistence.get_vuln_by_id(db, data.vuln_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such vuln")

    now = datetime.now(timezone.utc)
    log = models.ActionLog(
        vuln_id=data.vuln_id,
        action=data.action,
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


@router.get("/vulns/{vuln_id}", response_model=list[schemas.ActionLogResponse])
def get_vuln_logs(
    vuln_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actionlogs associated with the specified vuln.
    """
    vuln = persistence.get_vuln_by_id(db, vuln_id)
    if vuln is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such vuln")
    rows = persistence.get_vuln_logs_by_user_id(db, vuln_id, current_user.user_id)
    result = []
    for log in sorted(rows, key=lambda l: l.executed_at, reverse=True):
        original_log = log.__dict__.copy()
        if log.created_at:
            original_log["created_at"] = log.created_at
        if log.executed_at:
            original_log["executed_at"] = log.executed_at
        result.append(original_log)
    return result
