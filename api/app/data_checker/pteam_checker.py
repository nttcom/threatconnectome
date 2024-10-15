from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence


def check_and_get_pteam(
    db: Session,
    pteam_id: UUID,
) -> models.PTeam:
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
    return pteam
