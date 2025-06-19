from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth.account import get_current_user
from app.database import get_db

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=schemas.TicketListResponse)
def get_tickets(
    my_tasks: bool = Query(False),
    pteam_ids: list[str] | None = Query(None),
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

    if my_tasks:
        query = query.join(models.TicketStatus).filter(
            models.TicketStatus.assignees.contains([str(current_user.user_id)])
        )

    total_count = query.count()

    tickets = query.offset(offset).limit(limit).all()

    return schemas.TicketListResponse(
        total=total_count,
        offset=offset,
        limit=limit,
        tickets=[
            schemas.TicketResponse.model_validate(
                {
                    **ticket.__dict__,
                    "vuln_id": str(ticket.threat.vuln_id) if ticket.threat else None,
                },
                from_attributes=True,
            )
            for ticket in tickets
        ],
    )
