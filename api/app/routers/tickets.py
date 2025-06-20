from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth.account import get_current_user
from app.database import get_db

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
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated tickets related to the pteams the current user belongs to.
    """
    if not pteam_ids:
        pteam_ids = [role.pteam_id for role in current_user.pteam_roles]

    query = (
        db.query(models.Ticket)
        .options(joinedload(models.Ticket.ticket_status))
        .filter(
            models.Ticket.dependency.has(
                models.Dependency.service.has(models.Service.pteam_id.in_(pteam_ids))
            )
        )
    )

    if assigned_to_me:
        query = query.join(models.TicketStatus).filter(
            models.TicketStatus.assignees.contains([str(current_user.user_id)])
        )

    total_count = query.count()

    tickets = query.offset(offset).limit(limit).all()

    return schemas.TicketListResponse(
        total=total_count,
        tickets=[ticket_to_response(ticket) for ticket in tickets],
    )
