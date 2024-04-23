from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.database import get_db

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=List[schemas.ThreatResponse])
def get_threats(
    tag_id: Union[UUID, None] = None,
    service_id: Union[UUID, None] = None,
    topic_id: Union[UUID, None] = None,
    db: Session = Depends(get_db),
):
    """
    Get all threats sorted by service_id.
    """
    threats = persistence.get_all_threats(tag_id, service_id, topic_id, db)
    return sorted(threats, key=lambda threat: threat.service_id)


@router.get("/{threat_id}", response_model=schemas.ThreatResponse)
def get_threat(
    threat_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a threat.
    """
    if not (threat := persistence.get_threat(db, threat_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    return threat


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
