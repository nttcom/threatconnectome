import os
from typing import Dict, List, Sequence, Union
from urllib.parse import quote_plus, urljoin

from fastapi import HTTPException, status
from slack_sdk.errors import SlackApiError
from slack_sdk.webhook import WebhookClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_, func

from app import models

WEBUI_URL = os.getenv("WEBUI_URL", "http://localhost")
TAG_URL = urljoin(WEBUI_URL, "/tags/")
ANALYSIS_URL = urljoin(WEBUI_URL, "/analysis")
THREAT_IMPACT_LABEL = {
    1: ":red_circle: Immediate",
    2: ":large_orange_circle: Off-cycle",
    3: ":large_yellow_circle: Acceptable",
    4: ":white_circle: None",
}


def validate_slack_webhook_url(url: str):
    hooks_url = "https://hooks.slack.com/services/"
    if not url.startswith(hooks_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid slack webhook url"
        )


def _block_header(text: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{text}*",
            },
        },
        {"type": "divider"},
    ]


def _create_blocks_for_pteam(
    pteam_id: str,
    pteam_name: str,
    tag_id: str,
    tag_name: str,
    topic_id: str,
    title: str,
    threat_impact: int,
):
    blocks: List[Dict[str, Union[str, Dict[str, str], List[Dict[str, str]]]]]
    blocks = _block_header(text=pteam_name)
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [
                            f"*<{TAG_URL}{str(tag_id)}?pteamId={pteam_id}|{tag_name}>*",
                            f"*{title}*",
                            THREAT_IMPACT_LABEL[threat_impact],
                        ]
                    ),
                },
            },
            {
                "type": "context",
                "elements": [{"type": "plain_text", "text": str(topic_id)}],
            },
            {"type": "divider"},
        ]
    )
    return blocks


def _pick_alert_targets_for_pteam(db: Session, topic: models.Topic) -> List[dict]:
    if topic.disabled:
        return []
    select_stmt = (
        select(
            models.PTeam.pteam_name,
            models.PTeam.slack_webhook_url,
            models.CurrentPTeamTopicTagStatus.pteam_id,
            models.CurrentPTeamTopicTagStatus.tag_id,
            models.Tag.tag_name,
        )
        .join(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.topic_id == topic.topic_id,
                models.CurrentPTeamTopicTagStatus.topic_status == models.TopicStatusType.alerted,
                models.CurrentPTeamTopicTagStatus.pteam_id == models.PTeam.pteam_id,
                models.PTeam.disabled.is_(False),
                func.length(models.PTeam.slack_webhook_url) > 0,
                models.PTeam.alert_threat_impact >= topic.threat_impact,
            ),
        )
        .join(
            models.Tag,
            models.Tag.tag_id == models.CurrentPTeamTopicTagStatus.tag_id,
        )
    )
    return [row._asdict() for row in db.execute(select_stmt).all()]


def alert_new_topic(db: Session, topic: models.Topic):
    alert_targets = _pick_alert_targets_for_pteam(db, topic)
    for target in alert_targets:
        webhook_url = target.pop("slack_webhook_url")
        blocks = _create_blocks_for_pteam(
            **target,
            topic_id=topic.topic_id,
            title=topic.title,
            threat_impact=topic.threat_impact,
        )
        post_message(webhook_url, blocks)


def _create_blocks_for_ateam(
    ateam_id: str,
    ateam_name: str,
    title: str,
    action: str,
    action_type: str,
):
    blocks: List[Dict[str, Union[str, Dict[str, str], List[Dict[str, str]]]]]
    blocks = _block_header(text=ateam_name)
    blocks.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [
                            f"*<{ANALYSIS_URL}?ateamId={ateam_id}&search={quote_plus(title)}|{title}>*",
                        ]
                    ),
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "\n".join(
                            [
                                "Linked action has been created.",
                                f"*action: {action}*",
                                f"*type: {action_type}*",
                            ]
                        ),
                    },
                ],
            },
            {"type": "divider"},
        ]
    )
    return blocks


def _pick_alert_targets_for_ateam(db: Session, action: models.TopicAction) -> List[dict]:
    if action.topic.disabled:
        return []
    select_stmt = (
        select(
            models.ATeamPTeam.ateam_id,
            models.ATeam.ateam_name,
            models.ATeam.slack_webhook_url,
        )
        .join(
            models.CurrentPTeamTopicTagStatus,
            and_(
                # Note: disabled pteam has no records on CurrentPTeamTopicTagStatus
                models.CurrentPTeamTopicTagStatus.topic_id == action.topic_id,
                models.CurrentPTeamTopicTagStatus.pteam_id == models.ATeamPTeam.pteam_id,
            ),
        )
        .join(
            models.ATeam,
            and_(
                func.length(models.ATeam.slack_webhook_url) > 0,
                # If you wanna filter notifications by topic threat impact, add conditions here.
                models.ATeam.ateam_id == models.ATeamPTeam.ateam_id,
            ),
        )
        .distinct()
    )
    return [row._asdict() for row in db.execute(select_stmt).all()]


def alert_to_ateam(db: Session, action: models.TopicAction):
    alert_targets = _pick_alert_targets_for_ateam(db, action)
    print(alert_targets)
    for target in alert_targets:
        webhook_url = target.pop("slack_webhook_url")
        blocks = _create_blocks_for_ateam(
            **target,
            title=action.topic.title,
            action=action.action,
            action_type=action.action_type,
        )
        post_message(webhook_url, blocks)


def post_message(url: str, blocks: Sequence[Dict]):
    try:
        webhook = WebhookClient(url)
        return webhook.send(text=blocks[0]["text"]["text"], blocks=blocks)
    except SlackApiError as error:
        print(f"Error posting message: {error}")
        return None
