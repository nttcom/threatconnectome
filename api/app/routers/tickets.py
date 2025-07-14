from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth.account import get_current_user
from app.command import get_tickets_for_pteams
from app.database import get_db
from app.persistence import validate_pteam_ids

router = APIRouter(prefix="/tickets", tags=["tickets"])


def ticket_to_response(ticket: models.Ticket):
    dependency = ticket.dependency
    service = dependency.service
    pteam_id = service.pteam_id
    service_id = service.service_id
    return schemas.TicketResponse(
        ticket_id=UUID(ticket.ticket_id),
        vuln_id=UUID(ticket.threat.vuln_id),
        dependency_id=UUID(ticket.dependency_id),
        service_id=service_id,
        pteam_id=pteam_id,
        created_at=ticket.created_at,
        ssvc_deployer_priority=ticket.ssvc_deployer_priority,
        ticket_safety_impact=ticket.ticket_safety_impact,
        ticket_safety_impact_change_reason=ticket.ticket_safety_impact_change_reason,
        ticket_status=(schemas.TicketStatusResponse.model_validate(ticket.ticket_status)),
    )


@router.get("", response_model=schemas.TicketListResponse)
def get_tickets(
    assigned_to_me: bool = Query(False, alias="my_tasks"),
    pteam_ids: list[UUID] | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated tickets related to the pteams the current user belongs to.
    """

    user_pteam_ids = {UUID(str(role.pteam_id)) for role in current_user.pteam_roles}
    if not pteam_ids:
        pteam_ids = list(user_pteam_ids)

    try:
        validate_pteam_ids(db, pteam_ids, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total_count, tickets = get_tickets_for_pteams(
        db=db,
        pteam_ids=pteam_ids,
        assigned_to_me=assigned_to_me,
        user_id=UUID(current_user.user_id) if current_user.user_id else None,
        offset=offset,
        limit=limit,
        order=order,
    )

    return schemas.TicketListResponse(
        total=total_count,
        tickets=[ticket_to_response(ticket) for ticket in tickets],
    )
