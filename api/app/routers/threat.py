from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas, ssvc
from app.alert import create_alert_from_ticket_if_meet_threshold, send_alert_to_pteam
from app.database import get_db

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatResponse])
def get_threats(
    tag_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
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
    threats = persistence.search_threats(db, tag_id, service_id, topic_id)
    return threats


@router.post("", response_model=schemas.ThreatResponse)
def create_threat(
    data: schemas.ThreatRequest,
    db: Session = Depends(get_db),
):
    tag = persistence.get_tag_by_id(db, data.tag_id)
    topic = persistence.get_topic_by_id(db, data.topic_id)
    service = persistence.get_service_by_id(db, data.service_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")

    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

    if topic.disabled is True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")

    threat = models.Threat(
        tag_id=str(data.tag_id),
        service_id=str(data.service_id),
        topic_id=str(data.topic_id),
    )
    persistence.create_threat(db, threat)

    actions = persistence.get_actions_by_topic_id(db, data.topic_id)
    now = datetime.now()
    action_tag_names_set: set = set()

    if actions:
        for action in actions:
            action_tag_names = action.ext.get("tags")
            if action_tag_names is None:
                continue
            action_tag_names_set |= set(action_tag_names)

        exist_related_action: bool = False
        for action_tag_name in action_tag_names_set:
            tag_by_action = persistence.get_tag_by_name(db, action_tag_name)
            if (
                threat.topic
                and tag_by_action
                and (tag_by_action.tag_id == tag.tag_id or tag_by_action.tag_id == tag.parent_id)
            ):
                exist_related_action = True
                break

        if exist_related_action:
            dependency = persistence.get_dependency_from_service_id_and_tag_id(
                db, service.service_id, tag.tag_id
            )
            ticket = models.Ticket(
                threat_id=str(threat.threat_id),
                created_at=now,
                updated_at=now,
                ssvc_deployer_priority=ssvc.calculate_ssvc_deployer_priority(threat, dependency),
            )
            persistence.create_ticket(db, ticket)

            if alert := create_alert_from_ticket_if_meet_threshold(ticket):
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
