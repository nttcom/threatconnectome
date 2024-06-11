import json

import httpretty

from app import models
from app.slack import (
    _create_blocks_for_ateam,
    alert_to_ateam,
)
from app.tests.medium.constants import (
    ACTION1,
    ATEAM1,
    PTEAM1,
    SAMPLE_SLACK_WEBHOOK_URL,
    SERVICE1,
    TAG1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    accept_watching_request,
    create_action,
    create_ateam,
    create_pteam,
    create_topic,
    create_user,
    create_watching_request,
    upload_pteam_tags,
)


def test_alert_ateam(testdb):
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)
    ATEAM1_WITH_SLACK_WEBHOOK_URL = {
        **ATEAM1,
        "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL},
    }
    ateam = create_ateam(USER1, ATEAM1_WITH_SLACK_WEBHOOK_URL)
    watching_request = create_watching_request(USER1, ateam.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam.pteam_id)
    upload_pteam_tags(
        USER1, pteam.pteam_id, SERVICE1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True
    )
    topic = create_topic(USER1, TOPIC1, actions=[])
    create_action(USER1, ACTION1, topic_id=topic.topic_id)
    action = testdb.query(models.TopicAction).first()
    with httpretty.enabled():
        httpretty.register_uri(
            httpretty.POST, ATEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"], body="OK"
        )
        alert_to_ateam(testdb, action)
        assert httpretty.last_request().method == "POST"
        assert (
            httpretty.last_request().url
            == ATEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"]
        )

        # assert posted data contains results of _create_blocks_for_ateam
        expected_blocks = _create_blocks_for_ateam(
            ateam_id=ateam.ateam_id,
            ateam_name=ateam.ateam_name,
            title=action.topic.title,
            action=action.action,
            action_type=action.action_type,
        )
        assert (
            json.loads(httpretty.last_request().body.decode("utf-8"))["blocks"] == expected_blocks
        )
