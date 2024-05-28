import json

import httpretty

from app import models
from app.alert import alert_new_topic
from app.slack import (
    _create_blocks_for_ateam,
    alert_to_ateam,
)
from app.tests.medium.constants import (
    ACTION1,
    ATEAM1,
    GROUP1,
    PTEAM1,
    SAMPLE_SLACK_WEBHOOK_URL,
    TAG1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    accept_watching_request,
    create_action,
    create_ateam,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    create_watching_request,
    upload_pteam_tags,
)


def test_alert_new_topics__auto_closed(testdb):
    create_user(USER1)
    tag1 = create_tag(USER1, "testpkg:testinfo:testmgr")

    pteam1 = create_pteam(
        USER1, {**PTEAM1, "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL}}
    )
    refs0 = {tag1.tag_name: [("test/target1", "1.0")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, "test group", refs0)

    action1 = {
        "action": "update testpkg to version 1.0",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">0 <1.0"],
            },
        },
    }
    create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name], "actions": [action1]})
    db_topic1 = testdb.query(models.Topic).one()

    current_status = (
        testdb.query(models.CurrentPTeamTopicTagStatus.topic_status)
        .filter(
            models.CurrentPTeamTopicTagStatus.topic_id == db_topic1.topic_id,
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag1.tag_id),
        )
        .scalar()
    )
    assert current_status == models.TopicStatusType.completed  # auto closed

    with httpretty.enabled():
        httpretty.register_uri(httpretty.POST, pteam1.alert_slack.webhook_url, body="OK")
        alert_new_topic(testdb, db_topic1)
        assert not httpretty.has_request()


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
    upload_pteam_tags(USER1, pteam.pteam_id, GROUP1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True)
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
