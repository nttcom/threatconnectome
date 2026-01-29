from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models, persistence
from app.detector import vulnerability_detector
from app.notification.alert import send_alert_to_pteam
from app.ssvc import ssvc_calculator


def fix_ticket_by_threat(db: Session, threat: models.Threat):
    need_ticket = _check_need_ticket(db, threat)
    for dependency in threat.package_version.dependencies:
        if ticket := persistence.get_ticket_by_threat_id_and_dependency_id(
            db, threat.threat_id, dependency.dependency_id
        ):
            if need_ticket:
                fix_ticket_ssvc_priority(db, ticket)
            else:
                persistence.delete_ticket(db, ticket)

        else:
            if need_ticket:
                create_ticket_internal(db, threat, dependency)


def _check_need_ticket(db: Session, threat: models.Threat) -> bool:
    for affect in threat.vuln.affects:
        matched_package_version_ids: set[str] = (
            vulnerability_detector.detect_vulnerability_by_affect(db, affect)
        )
        if threat.package_version.package_version_id in matched_package_version_ids:
            if len(affect.fixed_versions) > 0:
                return True
    return False


def ticket_meets_condition_to_create_alert(ticket: models.Ticket) -> bool:
    # abort if deployer_priofiry is not yet calculated
    if ticket.ssvc_deployer_priority is None:
        return False

    if ticket.ticket_status.ticket_handling_status == models.TicketHandlingStatusType.completed:
        return False

    pteam = ticket.dependency.service.pteam
    return ticket.ssvc_deployer_priority <= pteam.alert_ssvc_priority


def create_ticket_internal(
    db: Session,
    threat: models.Threat,
    dependency: models.Dependency,
) -> models.Ticket:
    now = datetime.now(timezone.utc)

    ticket = models.Ticket(
        threat_id=threat.threat_id,
        dependency_id=dependency.dependency_id,
        ssvc_deployer_priority=None,
        threat=threat,
        dependency=dependency,
    )
    ticket.ssvc_deployer_priority = ssvc_calculator.calculate_ssvc_priority_by_ticket(ticket)
    persistence.create_ticket(db, ticket)

    ticket_status = models.TicketStatus(
        status_id=None,
        ticket_id=ticket.ticket_id,
        user_id=None,
        ticket_handling_status=models.TicketHandlingStatusType.alerted,
        note=None,
        logging_ids=[],
        assignees=[],
        scheduled_at=None,
        created_at=now,
        updated_at=now,
    )
    persistence.create_ticket_status(db, ticket_status)

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


def fix_ticket_ssvc_priority(
    db: Session,
    ticket: models.Ticket | None,
    now: datetime | None = None,
):
    if not ticket:  # failsafe
        return
    fixed_priority = ssvc_calculator.calculate_ssvc_priority_by_ticket(ticket)
    if fixed_priority == ticket.ssvc_deployer_priority:
        return

    ticket.ssvc_deployer_priority = fixed_priority
    # omit flush -- should be flushed in create_alert
    if ticket_meets_condition_to_create_alert(ticket):
        now = now or datetime.now(timezone.utc)
        alert = models.Alert(
            ticket_id=ticket.ticket_id,
            alerted_at=now,
            alert_content="",  # not used currently
        )
        persistence.create_alert(db, alert)
        send_alert_to_pteam(alert)

    db.flush()
