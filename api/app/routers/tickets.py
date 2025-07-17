from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import command, database, models, persistence, schemas
from app.auth.account import get_current_user
from app.routers.validators.account_validator import check_pteam_membership

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
    assigned_to_me: bool = Query(False),
    pteam_ids: list[UUID] | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Get paginated tickets related to the pteams the current user belongs to.
    """

    if not pteam_ids:
        user_pteam_ids = {UUID(str(role.pteam_id)) for role in current_user.pteam_roles}
        pteam_ids = list(user_pteam_ids)

    db_pteams = persistence.get_pteams_by_ids(db, pteam_ids)
    found_pteam_ids = {str(pteam.pteam_id) for pteam in db_pteams}
    not_found = set(str(pid) for pid in pteam_ids) - found_pteam_ids
    if not_found:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specified pteam_ids do not exist: {not_found}",
        )

    not_belong = [
        pteam.pteam_id for pteam in db_pteams if not check_pteam_membership(pteam, current_user)
    ]
    if not_belong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specified pteam_ids not belonging to the user: {not_belong}",
        )

    assigned_user_id = (
        UUID(current_user.user_id) if assigned_to_me and current_user.user_id else None
    )

    total_count, tickets = command.get_sorted_paginated_tickets_for_pteams(
        db=db,
        pteam_ids=pteam_ids,
        assigned_user_id=assigned_user_id,
        offset=offset,
        limit=limit,
        order=order,
    )

    return schemas.TicketListResponse(
        total=total_count,
        tickets=[ticket_to_response(ticket) for ticket in tickets],
    )
