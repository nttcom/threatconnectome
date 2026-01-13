from email_validator import validate_email

from app import models
from app.constants import SYSTEM_EMAIL
from app.notification.mail import (
    create_mail_alert_for_new_vuln,
    create_mail_to_notify_sbom_upload_failed,
    create_mail_to_notify_sbom_upload_succeeded,
)
from app.notification.sendgrid import (
    ready_to_send_email,
    send_email,
)
from app.notification.slack import (
    create_slack_blocks_to_notify_sbom_upload_failed,
    create_slack_blocks_to_notify_sbom_upload_succeeded,
    create_slack_pteam_alert_blocks_for_new_vuln,
    send_slack,
)


def _ready_alert_by_email() -> bool:
    # check sendgrid is ready
    if not ready_to_send_email():
        return False
    # check if SYSTEM_EMAIL can be used as from address
    try:
        validate_email(SYSTEM_EMAIL, check_deliverability=False)
    except ValueError:
        return False

    return True


def send_alert_to_pteam(alert: models.Alert) -> None:
    if not (ticket := alert.ticket):  # this alert is orphan, no info to send to.
        return
    threat = ticket.threat
    package = threat.package_version.package
    vuln = threat.vuln
    service = ticket.dependency.service
    pteam = service.pteam

    # check alert settings
    alert_by_slack = pteam.alert_slack.enable and pteam.alert_slack.webhook_url
    alert_by_mail = _ready_alert_by_email() and pteam.alert_mail.enable and pteam.alert_mail.address
    if not alert_by_slack and not alert_by_mail:
        return None

    if alert_by_slack:
        try:
            slack_message_blocks = create_slack_pteam_alert_blocks_for_new_vuln(
                pteam.pteam_id,
                pteam.pteam_name,
                package.package_id,
                package.name,
                vuln.vuln_id,
                vuln.title,  # WORKAROUND
                ticket.ssvc_deployer_priority,
                service.service_id,
                [service.service_name],  # WORKAROUND
            )
            send_slack(pteam.alert_slack.webhook_url, slack_message_blocks)
        except Exception:
            pass

    if alert_by_mail:
        try:
            mail_subject, mail_body = create_mail_alert_for_new_vuln(
                vuln.title,  # WORKAROUND
                ticket.ssvc_deployer_priority,
                pteam.pteam_name,
                pteam.pteam_id,
                package.name,
                package.ecosystem,
                ticket.dependency.package_manager,
                package.package_id,
                service.service_id,
                [service.service_name],  # WORKAROUND
            )
            send_email(pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
        except Exception:
            pass


def notify_sbom_upload_ended(
    service: models.Service,
    filename: str | None,
    succeeded: bool,
) -> None:
    pteam = service.pteam

    # check alert settings
    send_by_slack = pteam.alert_slack.enable and pteam.alert_slack.webhook_url
    send_by_mail = _ready_alert_by_email() and pteam.alert_mail.enable and pteam.alert_mail.address
    if not send_by_slack and not send_by_mail:
        return None

    if send_by_slack:
        try:
            slack_message_blocks = (
                create_slack_blocks_to_notify_sbom_upload_succeeded(
                    pteam.pteam_id,
                    pteam.pteam_name,
                    service.service_id,
                    service.service_name,
                    filename,
                )
                if succeeded
                else create_slack_blocks_to_notify_sbom_upload_failed(
                    service.service_name, filename
                )
            )
            send_slack(pteam.alert_slack.webhook_url, slack_message_blocks)
        except Exception:
            pass

    if send_by_mail:
        try:
            mail_subject, mail_body = (
                create_mail_to_notify_sbom_upload_succeeded(
                    pteam.pteam_id,
                    pteam.pteam_name,
                    service.service_id,
                    service.service_name,
                    filename,
                )
                if succeeded
                else create_mail_to_notify_sbom_upload_failed(service.service_name, filename)
            )
            send_email(pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
        except Exception:
            pass
