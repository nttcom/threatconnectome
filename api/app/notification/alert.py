import os
from urllib.parse import urlencode, urljoin
from uuid import UUID

from email_validator import validate_email

from app import models
from app.constants import SYSTEM_EMAIL
from app.notification.sendgrid import (
    ready_to_send_email,
    send_email,
)
from app.notification.slack import (
    create_slack_blocks_to_notify_sbom_upload_failed,
    create_slack_blocks_to_notify_sbom_upload_succeeded,
    create_slack_pteam_alert_blocks_for_new_topic,
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


def _pteam_tag_page_link(pteam_id: UUID | str, tag_id: UUID | str, service_id: UUID | str) -> str:
    return urljoin(
        os.getenv("NOTIFICATION_WEBUI_URL", "http://localhost"),
        f"/tags/{str(tag_id)}?pteamId={str(pteam_id)}&serviceId={str(service_id)}",
    )


def _pteam_service_tab_link(pteam_id: UUID | str, service_id: UUID | str) -> str:
    baseurl = os.getenv("NOTIFICATION_WEBUI_URL", "http://localhost")
    baseurl += "" if baseurl.endswith("/") else "/"
    params = {"pteamId": str(pteam_id), "serviceId": str(service_id)}
    encoded_params = urlencode(params)
    return urljoin(baseurl, f"?{encoded_params}")


def create_mail_alert_for_new_topic(
    topic_title: str,
    ssvc_priority: models.SSVCDeployerPriorityEnum,
    pteam_name: str,
    pteam_id: UUID | str,
    tag_name: str,  # should be pteamtag, not topictag
    tag_id: UUID | str,  # should be pteamtag, not topictag
    service_id: UUID | str,
    services: list[str],
) -> tuple[str, str]:  # subject, body
    # TODO
    # this mail-spacific-method should be divided away from this file, but to where?
    ssvc_priority_label = {
        models.SSVCDeployerPriorityEnum.IMMEDIATE: "Immediate",
        models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE: "Out-of-cycle",
        models.SSVCDeployerPriorityEnum.SCHEDULED: "Scheduled",
        models.SSVCDeployerPriorityEnum.DEFER: "Defer",
    }.get(ssvc_priority) or "Defer"
    subject = f"[Tc Alert] {ssvc_priority_label}: {topic_title}"
    body = "<br>".join(
        [
            "A new topic created.",
            "",
            f"Title: {topic_title}",
            f"SSVC Priority: {ssvc_priority_label}",
            "",
            f"Team: {pteam_name}",
            f"Services: {', '.join(services)}",
            f"Artifact: {tag_name}",
            "",
            (
                f"<a href={_pteam_tag_page_link(pteam_id, tag_id, service_id)}>Link to"
                " Artifact page</a>"
            ),
        ]
    )
    return subject, body


def send_alert_to_pteam(alert: models.Alert) -> None:
    if not (ticket := alert.ticket):  # this alert is orphan, no info to send to.
        return
    threat = ticket.threat
    tag = threat.dependency.tag
    topic = threat.topic
    service = threat.dependency.service
    pteam = service.pteam

    # check alert settings
    alert_by_slack = pteam.alert_slack.enable and pteam.alert_slack.webhook_url
    alert_by_mail = _ready_alert_by_email() and pteam.alert_mail.enable and pteam.alert_mail.address
    if not alert_by_slack and not alert_by_mail:
        return None

    if alert_by_slack:
        try:
            slack_message_blocks = create_slack_pteam_alert_blocks_for_new_topic(
                pteam.pteam_id,
                pteam.pteam_name,
                tag.tag_id,
                tag.tag_name,
                topic.topic_id,
                topic.title,  # WORKAROUND
                ticket.ssvc_deployer_priority,
                service.service_id,
                [service.service_name],  # WORKAROUND
            )
            send_slack(pteam.alert_slack.webhook_url, slack_message_blocks)
        except Exception:
            pass

    if alert_by_mail:
        try:
            mail_subject, mail_body = create_mail_alert_for_new_topic(
                topic.title,  # WORKAROUND
                ticket.ssvc_deployer_priority,
                pteam.pteam_name,
                pteam.pteam_id,
                tag.tag_name,
                tag.tag_id,
                service.service_id,
                [service.service_name],  # WORKAROUND
            )
            send_email(pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
        except Exception:
            pass


def create_mail_to_notify_sbom_upload_succeeded(
    pteam_id: UUID | str,
    pteam_name: str,
    service_id: UUID | str,
    service_name: str,
    filename: str | None,
) -> tuple[str, str]:  # subject, body
    # TODO
    # this mail-spacific-method should be divided away from this file, but to where?
    subject = f"[Tc Info] SBOM uploaded as a service: {service_name}"
    body = "<br>".join(
        [
            "SBOM upload successfully ended.",
            "",
            f"PTeamName: {pteam_name}",
            f"ServiceName: {service_name}",
            "",
            f"<a href={_pteam_service_tab_link(pteam_id, service_id)}>Link to the service tab</a>",
            "",
            f"UploadedFilename: {filename or '(unknown)'}",
        ]
    )
    return subject, body


def create_mail_to_notify_sbom_upload_failed(
    service_name: str,
    filename: str | None,
) -> tuple[str, str]:  # subject, body
    # TODO
    # this mail-spacific-method should be divided away from this file, but to where?
    subject = f"[Tc Error] SBOM upload failed as a service: {service_name}"
    body = "<br>".join(
        [
            "SBOM upload failed.",
            "",
            f"ServiceName: {service_name}",
            f"UploadedFilename: {filename or '(unknown)'}",
        ]
    )
    return subject, body


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
