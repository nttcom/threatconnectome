from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.alert import send_alert_to_pteam
from app.common import (
    threat_meets_condition_to_create_ticket,
    ticket_meets_condition_to_create_alert,
)
from app.database import get_db
from app.ssvc import calculate_ssvc_deployer_priority

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatResponse])
def get_threats(
    dependency_id: UUID | None = Query(None),
    topic_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get all threats sorted by service_id.

    Query Params:
    - **tag_id** (Optional) filter by specified tag_id. Default is None.
    - **service_id** (Optional) filter by specified service_id. Default is None.
    - **topic_id** (Optional) filter by specified topic_id. Default is None.
    """
    threats = persistence.search_threats(db, dependency_id, topic_id)
    return threats


@router.post("", response_model=schemas.ThreatResponse)
def create_threat(
    data: schemas.ThreatRequest,
    db: Session = Depends(get_db),
):
    now = datetime.now()
    dependency = persistence.get_dependency_by_id(db, data.dependency_id)
    topic = persistence.get_topic_by_id(db, data.topic_id)

    if dependency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such dependency")

    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

    if topic.disabled is True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

    if persistence.search_threats(db, data.dependency_id, data.topic_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Threat already exists")

    threat = models.Threat(
        dependency_id=str(data.dependency_id),
        topic_id=str(data.topic_id),
    )
    persistence.create_threat(db, threat)

    if threat_meets_condition_to_create_ticket(db, threat):
        # dependency = persistence.get_dependency_from_service_id_and_tag_id(
        #     db, threat.dependency.service_id, threat.dependency.tag_id
        # )
        ticket = models.Ticket(
            threat_id=threat.threat_id,
            created_at=now,
            updated_at=now,
            ssvc_deployer_priority=calculate_ssvc_deployer_priority(threat, threat.dependency),
        )
        persistence.create_ticket(db, ticket)
        if ticket_meets_condition_to_create_alert(ticket):
            alert = models.Alert(
                ticket_id=ticket.ticket_id,
                alerted_at=now,
                alert_content=topic.hint_for_action,
            )
            persistence.create_alert(db, alert)
            send_alert_to_pteam(alert)

    db.commit()

    return threat


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


@router.delete("/{threat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_threat(
    threat_id: UUID,
    db: Session = Depends(get_db),
):
    threat = persistence.get_threat_by_id(db, threat_id)
    if threat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    persistence.delete_threat(db, threat)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
