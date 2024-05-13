from datetime import datetime

from sqlalchemy.orm import Session

from app import models, persistence


def create_ticket(db: Session, threat: models.Threat) -> None:

    if (
        not (topic := persistence.get_topic_by_id(db, threat.topic_id))
        or topic.hint_for_action is None
    ):
        # No need to create a ticket.
        return

    now = datetime.now()
    ticket = models.Ticket(
        threat_id=str(threat.threat_id),
        created_at=now,
        updated_at=now,
        ssvc_deployer_priority=calculate_ssvc_deployer_priority(db, threat),
    )
    persistence.create_ticket(db, ticket)

    # TODO create_alert()呼び出し


def calculate_ssvc_deployer_priority(
    db: Session, threat: models.Threat
) -> models.SSVCDeployerPriorityEnum | None:

    if not (topic := persistence.get_topic_by_id(db, threat.topic_id)):
        return None
    if not (service := persistence.get_service_by_id(db, threat.service_id)):
        return None

    exploitation = topic.exploitation
    exposure = service.exposure
    automatable = topic.automatable
    mission_impact = persistence.get_mission_impact(db, threat.tag_id, threat.service_id)
    safety_impact = topic.safety_impact

    # TODO Calculation not implemented.
    return (
        models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE
        if exploitation and exposure and automatable and mission_impact and safety_impact
        else models.SSVCDeployerPriorityEnum.DEFER
    )
