from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import command, persistence, schemas
from app.database import get_db

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatResponse])
def get_threats(
    service_id: UUID | None = Query(None),
    dependency_id: UUID | None = Query(None),
    topic_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get all threats.

    Query Params:
    - **service_id** (Optional) filter by specified service_id. Default is None.
    - **dependency_id** (Optional) filter by specified service_id. Default is None.
    - **topic_id** (Optional) filter by specified topic_id. Default is None.
    """
    threats = command.search_threats(db, service_id, dependency_id, topic_id)
    return threats


@router.get("/{threat_id}", response_model=schemas.ThreatResponse)
def get_threat(
    threat_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a threat.
    """
    if not (threat := persistence.get_threat_by_id(db, threat_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    return threat
