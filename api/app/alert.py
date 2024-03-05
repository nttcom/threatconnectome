import os
from typing import List, Sequence, Tuple
from urllib.parse import urljoin
from uuid import UUID

from email_validator import validate_email
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func

from app import models
from app.constants import SYSTEM_EMAIL
from app.sendgrid import ready_to_send_email, send_email


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


def _pick_alert_targets_for_new_topic(
    db: Session,
    topic_id: UUID | str,
) -> Sequence[models.CurrentPTeamTopicTagStatus]:
    # Note:
    #   process auto-close and fix-current-status beforehand, and
    #   disabled topics and pteams are excluded from CurrentPTeamTopicTagStatus table.
    #   unvisible topics by zones are also excluded.
    return db.scalars(
        select(models.CurrentPTeamTopicTagStatus)
        .options(
            joinedload(models.CurrentPTeamTopicTagStatus.tag, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.topic, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.pteam, innerjoin=True).options(
                joinedload(models.PTeam.alert_slack, innerjoin=True),
                joinedload(models.PTeam.alert_mail, innerjoin=True),
            ),
        )
        .where(
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic_id),
            models.CurrentPTeamTopicTagStatus.topic_status == models.TopicStatusType.alerted,
        )
        .join(models.Topic)
        .join(
            models.PTeam,
            and_(
                models.PTeam.pteam_id == models.CurrentPTeamTopicTagStatus.pteam_id,
                or_(
                    models.PTeam.alert_threat_impact.is_(None),
                    models.PTeam.alert_threat_impact >= models.Topic.threat_impact,
                ),
            ),
        )
    ).all()


def alert_new_topic(db: Session, topic_id: UUID | str) -> None:
    targets_to_alert = _pick_alert_targets_for_new_topic(db, topic_id)
    for row in targets_to_alert:
        alert_by_slack = row.pteam.alert_slack.enable and row.pteam.alert_slack.webhook_url
        alert_by_mail = (
            _ready_alert_by_email() and row.pteam.alert_mail.enable and row.pteam.alert_mail.address
        )
        if not alert_by_slack and not alert_by_mail:
            continue  # no media enabled

        groups_to_alert = db.execute(
            select(
                models.PTeamTagReference.tag_id,
                func.array_agg(models.PTeamTagReference.group.distinct()).label("groups"),
            )
            .where(
                models.PTeamTagReference.pteam_id == row.pteam_id,
                models.PTeamTagReference.tag_id == row.tag_id,
            )
            .group_by(models.PTeamTagReference.tag_id)
        ).all()
        if not groups_to_alert:
            continue  # something went wrong
        groups = sorted(groups_to_alert[0].groups)

        if alert_by_slack:
            try:
                pass
                # slack_message = "xxx"
                #
                # send_to_slack(row.pteam.alert_slack.webhook_url, slack_message)
                #
            except Exception:
                pass

        if alert_by_mail:
            try:
                mail_subject, mail_body = create_mail_alert_for_new_topic(
                    row.pteam, row.tag, row.topic, groups
                )
                send_email(row.pteam.alert_mail.address, SYSTEM_EMAIL, mail_subject, mail_body)
            except Exception:
                pass


#
# TODO
#
# following mail-spacific-methods should be divided away from this file, but to where?


def _pteam_tag_page_link(pteam_id: UUID | str, tag_id: UUID | str) -> str:
    return urljoin(
        os.getenv("WEBUI_URL", "http://localhost"),
        f"/tags/{str(tag_id)}?pteam_id={str(pteam_id)}",
    )


def create_mail_alert_for_new_topic(
    pteam: models.PTeam,
    tag: models.Tag,
    topic: models.Topic,
    groups: List[str],
) -> Tuple[str, str]:  # subject, body
    threat_impact_label = {
        1: "Immediate",
        2: "Off-cycle",
        3: "Acceptable",
        4: "None",
    }.get(topic.threat_impact) or "WrongThreatImpact"
    subject = f"[Tc Alert] {threat_impact_label}: {topic.title}"
    body = "\n".join(
        [
            "A new topic created.",
            "",
            f"Title: {topic.title}",
            f"ThreatImpact: {threat_impact_label}",
            "",
            f"PTeam: {pteam.pteam_name}",
            f"Groups: {', '.join(groups)}",
            f"Artifact: {tag.tag_name}",
            "",
            f"Link to Artifact page: {_pteam_tag_page_link(pteam.pteam_id, tag.tag_id)}",
        ]
    )
    return subject, body
