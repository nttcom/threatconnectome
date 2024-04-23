from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.database import get_db

router = APIRouter(prefix="/threats", tags=["threats"])


@router.post("", response_model=schemas.ThreatResponse)
def create_threat(
    data: schemas.ThreatRequest,
    db: Session = Depends(get_db),
):
    tag_id = persistence.get_tag_by_id(db, data.tag_id)
    topic_id = persistence.get_topic_by_id(db, data.topic_id)
    service_id = persistence.get_service_by_id(db, data.service_id)
    if tag_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag_id")

    if topic_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic_id")

    if service_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service_id")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    persistence.delete_threat(db, threat)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
