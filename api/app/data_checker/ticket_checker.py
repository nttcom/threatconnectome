from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence


def check_and_get_ticket(
    db: Session,
    service_id: UUID,
    ticket_id: UUID,
) -> models.Ticket:
    if not (ticket := persistence.get_ticket_by_id(db, ticket_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ticket")
    if ticket.threat.dependency.service_id != str(service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ticket")
    return ticket
