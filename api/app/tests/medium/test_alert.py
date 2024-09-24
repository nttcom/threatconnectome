from uuid import uuid4

from fastapi.testclient import TestClient

from app import models, persistence, schemas
from app.alert import create_mail_alert_for_new_topic
from app.constants import DEFAULT_ALERT_SSVC_PRIORITY, SYSTEM_EMAIL
from app.main import app
from app.ssvc import ssvc_calculator
from app.tests.medium.constants import (
    SAMPLE_SLACK_WEBHOOK_URL,
    SERVICE1,
    USER1,
)
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    headers,
    upload_pteam_tags,
)

client = TestClient(app)


def test_alert_by_mail_if_vulnerabilities_are_found_when_creating_topic(testdb, mocker) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_mail": {
                "enable": True,
                "address": f"account{idx}@example.com",
            },
            "alert_ssvc_priority": DEFAULT_ALERT_SSVC_PRIORITY,
        }

    def _gen_topic_params(tags: list[schemas.TagResponse]) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "actions": [
                {
                    "topic_id": topic_id,
                    "action": "update to 999.9.9",
                    "action_type": models.ActionType.elimination,
                    "recommended": True,
                    "ext": {
                        "tags": [tag.tag_name for tag in tags],
                        "vulnerable_versions": {tag.tag_name: ["< 999.9.9"] for tag in tags},
                    },
                },
            ],
            "exploitation": "active",
            "automatable": "yes",
        }

    pteam0 = create_pteam(USER1, _gen_pteam_params(0))
    ext_tags = {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]}
    upload_pteam_tags(USER1, pteam0.pteam_id, SERVICE1, ext_tags)

    # topic0: no tags
    send_email = mocker.patch("app.alert.send_email")
    create_topic(USER1, _gen_topic_params([]))
    send_email.assert_not_called()

    # topic1: parent_tag1
    send_email = mocker.patch("app.alert.send_email")  # reset
    topic1 = create_topic(USER1, _gen_topic_params([parent_tag1]))
    threats1 = persistence.search_threats(testdb, None, topic1.topic_id)
    ssvc_priority1 = ssvc_calculator.calculate_ssvc_priority_by_threat(threats1[0])
    assert ssvc_priority1
    exp_to_email = pteam0.alert_mail.address
    exp_from_email = SYSTEM_EMAIL
    exp_subject, exp_body = create_mail_alert_for_new_topic(
        topic1.title,
        ssvc_priority1,
        pteam0.pteam_name,
        pteam0.pteam_id,
        child_tag11.tag_name,  # pteamtag, not topictag
        child_tag11.tag_id,  # pteamtag, not topictag
        [SERVICE1],
    )
    send_email.assert_called_once()
    send_email.assert_called_with(exp_to_email, exp_from_email, exp_subject, exp_body)

    # disable alert_mail
    request = {"alert_mail": {"enable": False, "address": pteam0.alert_mail.address}}
    assert_200(client.put(f"/pteams/{pteam0.pteam_id}", headers=headers(USER1), json=request))
    send_email = mocker.patch("app.alert.send_email")  # reset
    create_topic(USER1, _gen_topic_params([parent_tag1]))
    send_email.assert_not_called()

    # enable alert_mail again
    request = {"alert_mail": {"enable": True, "address": pteam0.alert_mail.address}}
    assert_200(client.put(f"/pteams/{pteam0.pteam_id}", headers=headers(USER1), json=request))
    send_email = mocker.patch("app.alert.send_email")  # reset
    topic3 = create_topic(USER1, _gen_topic_params([parent_tag1]))
    threats2 = persistence.search_threats(testdb, None, topic3.topic_id)
    ssvc_priority2 = ssvc_calculator.calculate_ssvc_priority_by_threat(threats2[0])
    assert ssvc_priority2
    exp_to_email = pteam0.alert_mail.address
    exp_from_email = SYSTEM_EMAIL
    exp_subject, exp_body = create_mail_alert_for_new_topic(
        topic3.title,
        ssvc_priority2,
        pteam0.pteam_name,
        pteam0.pteam_id,
        child_tag11.tag_name,  # pteamtag, not topictag
        child_tag11.tag_id,  # pteamtag, not topictag
        [SERVICE1],
    )
    send_email.assert_called_once()
    send_email.assert_called_with(exp_to_email, exp_from_email, exp_subject, exp_body)
