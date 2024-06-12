import os
from urllib.parse import urljoin
from uuid import UUID

from email_validator import validate_email

from app import models
from app.constants import SYSTEM_EMAIL
from app.sendgrid import ready_to_send_email, send_email
from app.slack import create_slack_pteam_alert_blocks_for_new_topic, send_slack


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


def _pteam_tag_page_link(pteam_id: UUID | str, tag_id: UUID | str) -> str:
    return urljoin(
        os.getenv("WEBUI_URL", "http://localhost"),
        f"/tags/{str(tag_id)}?pteam_id={str(pteam_id)}",
    )


def create_mail_alert_for_new_topic(
    topic_title: str,
    threat_impact: int,
    pteam_name: str,
    pteam_id: UUID | str,
    tag_name: str,  # should be pteamtag, not topictag
    tag_id: UUID | str,  # should be pteamtag, not topictag
    services: list[str],
) -> tuple[str, str]:  # subject, body
    # TODO
    # this mail-spacific-method should be divided away from this file, but to where?
    threat_impact_label = {
        1: "Immediate",
        2: "Off-cycle",
        3: "Acceptable",
        4: "None",
    }.get(threat_impact) or "WrongThreatImpact"
    subject = f"[Tc Alert] {threat_impact_label}: {topic_title}"
    body = "<br>".join(
        [
            "A new topic created.",
            "",
            f"Title: {topic_title}",
            f"ThreatImpact: {threat_impact_label}",
            "",
            f"PTeam: {pteam_name}",
            f"Services: {', '.join(services)}",
            f"Artifact: {tag_name}",
            "",
            f"<a href={_pteam_tag_page_link(pteam_id, tag_id)}>Link to Artifact page</a>",
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

    tmp_threat_impact = {  # WORKAROUND
        models.SSVCDeployerPriorityEnum.IMMEDIATE: 1,
        models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE: 2,
        models.SSVCDeployerPriorityEnum.SCHEDULED: 3,
        models.SSVCDeployerPriorityEnum.DEFER: 4,
    }.get(ticket.ssvc_deployer_priority, 4)

    if alert_by_slack:
        try:
            slack_message_blocks = create_slack_pteam_alert_blocks_for_new_topic(
                pteam.pteam_id,
                pteam.pteam_name,
                tag.tag_id,
                tag.tag_name,
                topic.topic_id,
                topic.title,  # WORKAROUND
                tmp_threat_impact,  # WORKAROUND
                [service.service_name],  # WORKAROUND
            )
            send_slack(pteam.alert_slack.webhook_url, slack_message_blocks)
        except Exception:
            pass

    if alert_by_mail:
        try:
            mail_subject, mail_body = create_mail_alert_for_new_topic(
                topic.title,  # WORKAROUND
                tmp_threat_impact,  # WORKAROUND
                pteam.pteam_name,
                pteam.pteam_id,
                tag.tag_name,
                tag.tag_id,
                [service.service_name],  # WORKAROUND
            )
            send_email(pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
        except Exception:
            pass
