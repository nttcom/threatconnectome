from datetime import datetime

from sqlalchemy.orm import Session

from app import models, persistence
from app.alert import send_alert_to_pteam
from app.ssvc import ssvc_calculator


def ticket_meets_condition_to_create_alert(ticket: models.Ticket) -> bool:
    # abort if deployer_priofiry is not yet calclated
    if ticket.ssvc_deployer_priority is None:
        return False

    if ticket.current_ticket_status.topic_status == models.TopicStatusType.completed:
        return False

    pteam = ticket.threat.dependency.service.pteam
    return ticket.ssvc_deployer_priority <= pteam.alert_ssvc_priority


def create_ticket_internal(
    db: Session,
    threat: models.Threat,
    now: datetime | None = None,
) -> models.Ticket:
    if now is None:
        now = datetime.now()

    ticket = models.Ticket(
        threat_id=threat.threat_id,
        created_at=now,
        ssvc_deployer_priority=ssvc_calculator.calculate_ssvc_priority_by_threat(threat),
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

    # send alert if needed
    if ticket_meets_condition_to_create_alert(ticket):
        alert = models.Alert(
            ticket_id=ticket.ticket_id,
            alerted_at=now,
            alert_content="",  # alert_content is not used
        )
        persistence.create_alert(db, alert)
        send_alert_to_pteam(alert)

    return ticket


def fix_tickets_for_service(db: Session, service: models.Service):
    now = datetime.now()
    for ticket in service.tickets:
        fixed_priority = ssvc_calculator.calculate_ssvc_priority_by_threat(ticket.threat)
        if fixed_priority == ticket.ssvc_deployer_priority:
            continue
        ticket.ssvc_deployer_priority = fixed_priority
        # omit flush -- should be flushed in create_alert
        if ticket_meets_condition_to_create_alert(ticket):
            alert = models.Alert(
                ticket_id=ticket.ticket_id,
                alerted_at=now,
                alert_content="",  # not used currently
            )
            persistence.create_alert(db, alert)
            send_alert_to_pteam(alert)

    db.flush()
