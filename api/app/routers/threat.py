from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.database import get_db

router = APIRouter(prefix="/threats", tags=["threats"])

NO_SUCH_THREAT = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")


@router.post("", response_model=schemas.ThreatResponse)
def create_threat(
    data: schemas.ThreatRequest,
    db: Session = Depends(get_db),
):

    threat = models.Threat(**data.model_dump())
    persistence.create_threat(db, threat)
    db.commit()

    return threat


@router.delete("/{threat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_threat(
    threat_id: UUID,
    db: Session = Depends(get_db),
):
    threat = persistence.get_threat(db, threat_id)
    if threat is None:
        raise NO_SUCH_THREAT
    persistence.delete_threat(db, threat)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
