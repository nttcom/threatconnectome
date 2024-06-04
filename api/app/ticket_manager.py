from datetime import datetime

from sqlalchemy.orm import Session

from app import models, persistence, schemas


def set_ticket_statuses(
    db: Session,
    current_user: models.Account,
    pteam: models.PTeam,
    topic: models.Topic,
    tag: models.Tag,  # should be PTeamTag, not TopicTag
    topicStatusRequest: schemas.TopicStatusRequest,
) -> None:
    for service in pteam.services:
        for dependency in service.dependencies:
            if dependency.tag_id != tag.tag_id:
                continue
            for threat in persistence.search_threats(db, dependency.dependency_id, topic.topic_id):
                if ticket := threat.ticket:
                    set_ticket_status(db, current_user, topic, ticket, topicStatusRequest)


def set_ticket_status(
    db: Session,
    current_user: models.Account,
    topic: models.Topic,
    ticket: models.Ticket,
    topicStatusRequest: schemas.TopicStatusRequest,
) -> None:
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
