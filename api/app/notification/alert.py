from email_validator import validate_email

from app import models
from app.constants import SYSTEM_EMAIL
from app.notification.mail import (
    create_mail_alert_for_new_vuln,
    create_mail_to_notify_eol,
    create_mail_to_notify_sbom_upload_failed,
    create_mail_to_notify_sbom_upload_succeeded,
)
from app.notification.sendgrid import (
    ready_to_send_email,
    send_email,
)
from app.notification.slack import (
    create_slack_blocks_to_notify_eol,
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


def _send_eol_notifications(
    pteam: models.PTeam,
    notification_sent: bool,
    service_name: str,
    product_name: str,
    version: str,
    eol_from: str,
) -> bool:
    # check alert settings
    send_by_slack = pteam.alert_slack.enable and pteam.alert_slack.webhook_url
    send_by_mail = _ready_alert_by_email() and pteam.alert_mail.enable and pteam.alert_mail.address

    if (not send_by_slack and not send_by_mail) or notification_sent:
        return False

    success = False
    last_exc: Exception | None = None
    if send_by_slack:
        try:
            slack_message_blocks = create_slack_blocks_to_notify_eol(
                pteam.pteam_id,
                pteam.pteam_name,
                service_name,
                product_name,
                version,
                eol_from,
            )
            send_slack(pteam.alert_slack.webhook_url, slack_message_blocks)
            success = True
        except Exception as e:
            last_exc = e

    if send_by_mail:
        try:
            mail_subject, mail_body = create_mail_to_notify_eol(
                pteam.pteam_id,
                pteam.pteam_name,
                service_name,
                product_name,
                version,
                eol_from,
            )
            send_email(pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
            success = True
        except Exception as e:
            last_exc = e

    if success:
        return True

    if last_exc:
        raise last_exc

    return False


def notify_eol_ecosystem(
    ecosystem_eol_dependency: models.EcosystemEoLDependency,
) -> bool:
    service = ecosystem_eol_dependency.service
    pteam = service.pteam
    eol_version = ecosystem_eol_dependency.eol_version

    return _send_eol_notifications(
        pteam=pteam,
        notification_sent=ecosystem_eol_dependency.eol_notification_sent,
        service_name=service.service_name,
        product_name=eol_version.eol_product.name,
        version=eol_version.version,
        eol_from=eol_version.eol_from,
    )


def notify_eol_package(
    package_eol_dependency: models.PackageEoLDependency,
) -> bool:
    service = package_eol_dependency.dependency.service
    pteam = service.pteam
    eol_version = package_eol_dependency.eol_version

    return _send_eol_notifications(
        pteam=pteam,
        notification_sent=package_eol_dependency.eol_notification_sent,
        service_name=service.service_name,
        product_name=eol_version.eol_product.name,
        version=eol_version.version,
        eol_from=eol_version.eol_from,
    )
