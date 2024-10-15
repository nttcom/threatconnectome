from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence
from app.data_checker.pteam_checker import check_and_get_pteam


def check_and_get_service(
    db: Session,
    pteam_id: UUID,
    service_id: UUID,
) -> models.Service:
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
    if service.pteam_id != str(pteam_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
    return service


def check_and_get_pteam_and_service(
    db: Session,
    pteam_id: UUID,
    service_id: UUID,
) -> tuple[models.PTeam, models.Service]:
    pteam = check_and_get_pteam(db, pteam_id)
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
    return (pteam, service)
