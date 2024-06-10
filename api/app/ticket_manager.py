from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.alert import send_alert_to_pteam
from app.common import (
    threat_meets_condition_to_create_ticket,
    ticket_meets_condition_to_create_alert,
)
from app.ssvc import calculate_ssvc_deployer_priority


def create_ticket(db: Session, threat: models.Threat):
    if not threat_meets_condition_to_create_ticket(db, threat):
        return

    # create Ticket
    dependency = persistence.get_dependency_from_service_id_and_tag_id(
        db, threat.dependency.service_id, threat.dependency.tag.tag_id
    )
    now = datetime.now()
    ticket = models.Ticket(
        threat_id=threat.threat_id,
        created_at=now,
        updated_at=now,
        ssvc_deployer_priority=calculate_ssvc_deployer_priority(threat, dependency),
    )
    persistence.create_ticket(db, ticket)

    # create CurrentTicketStatus without TicketStatus
    current_status = models.CurrentTicketStatus(
        ticket_id=ticket.ticket_id,
        status_id=None,
        topic_status=models.TopicStatusType.alerted,
        threat_impact=threat.topic.threat_impact,
        updated_at=threat.topic.updated_at,
    )
    persistence.create_current_ticket_status(db, current_status)

    if ticket_meets_condition_to_create_alert(ticket):
        alert = models.Alert(
            ticket_id=ticket.ticket_id,
            alerted_at=now,
            alert_content=threat.topic.hint_for_action,
        )
        persistence.create_alert(db, alert)
        send_alert_to_pteam(alert)


def set_ticket_statuses_in_pteam(
    db: Session,
    current_user: models.Account,
    pteam: models.PTeam,
    topic: models.Topic,
    tag: models.Tag,  # should be PTeamTag, not TopicTag
    topicStatusRequest: schemas.TopicStatusRequest,
) -> None:
    for service in pteam.services:
        set_ticket_statuses_in_service(db, current_user, service, topic, tag, topicStatusRequest)


def set_ticket_statuses_in_service(
    db: Session,
    current_user: models.Account,
    service: models.Service,
    topic: models.Topic,
    tag: models.Tag,  # should be PTeamTag, not TopicTag
    topicStatusRequest: schemas.TopicStatusRequest,
) -> schemas.TopicStatusResponse | None:
    firstest_updated_at: datetime | None = None
    firstest_status: models.TicketStatus | None = None

    for dependency in service.dependencies:
        if dependency.tag_id != tag.tag_id:
            continue
        for threat in persistence.search_threats(db, dependency.dependency_id, topic.topic_id):
            if ticket := threat.ticket:
                updated_at, ticket_status = set_ticket_status(
                    db, current_user, topic, ticket, topicStatusRequest
                )
                if firstest_status is None or (
                    firstest_updated_at is not None
                    and updated_at is not None
                    and updated_at < firstest_updated_at
                ):
                    firstest_status = ticket_status

    return ticket_status_to_response(db, firstest_status) if firstest_status is not None else None


def set_ticket_status(
    db: Session,
    current_user: models.Account,
    topic: models.Topic,
    ticket: models.Ticket,
    topicStatusRequest: schemas.TopicStatusRequest,
) -> tuple[datetime | None, models.TicketStatus]:
    current_status = persistence.get_current_ticket_status(db, ticket.ticket_id)
    if (
        (current_status is None or current_status.topic_status == models.TopicStatusType.alerted)
        and topicStatusRequest.topic_status == models.TopicStatusType.acknowledged
        and not topicStatusRequest.assignees  # first ack without assignees
    ):
        assignees = [current_user.user_id]  # force assign current_user
    else:
        assignees = list(map(str, topicStatusRequest.assignees))
    new_status = models.TicketStatus(
        ticket_id=ticket.ticket_id,
        user_id=current_user.user_id,
        topic_status=topicStatusRequest.topic_status,
        note=topicStatusRequest.note,
        logging_ids=list(map(str, set(topicStatusRequest.logging_ids))),
        assignees=list(set(assignees)),
        scheduled_at=topicStatusRequest.scheduled_at,
        created_at=datetime.now(),
    )
    persistence.create_ticket_status(db, new_status)

    if not current_status:
        current_status = models.CurrentTicketStatus(
            ticket_id=ticket.ticket_id,
            status_id=None,  # fill later
            topic_status=None,  # fill later
            threat_impact=None,  # fill later
            updated_at=None,  # fill later
        )
        persistence.create_current_ticket_status(db, current_status)

    current_status.status_id = new_status.status_id
    current_status.topic_status = new_status.topic_status
    current_status.threat_impact = topic.threat_impact
    current_status.updated_at = (
        None if new_status.topic_status == models.TopicStatusType.completed else topic.updated_at
    )

    db.flush()

    return current_status.updated_at, new_status


def ticket_status_to_response(
    db: Session,
    status: models.TicketStatus,
) -> schemas.TopicStatusResponse:
    threat = status.ticket.threat
    dependency = threat.dependency
    service = dependency.service
    actionlogs = db.scalars(
        select(models.ActionLog)
        .where(func.array_position(status.logging_ids, models.ActionLog.logging_id).is_not(None))
        .order_by(models.ActionLog.executed_at.desc())
    ).all()
    return schemas.TopicStatusResponse(
        status_id=UUID(status.status_id),
        topic_id=UUID(threat.topic.topic_id),
        pteam_id=UUID(service.pteam.pteam_id),
        service_id=UUID(service.service_id),
        tag_id=UUID(dependency.tag.tag_id),
        user_id=UUID(status.user_id),
        topic_status=status.topic_status,
        created_at=status.created_at,
        assignees=list(map(UUID, status.assignees)),
        note=status.note,
        scheduled_at=status.scheduled_at,
        action_logs=[schemas.ActionLogResponse(**log.__dict__) for log in actionlogs],
    )
