from datetime import datetime
from typing import List, Optional, Set, Union
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ACTION3,
    ATEAM1,
    ATEAM2,
    GTEAM1,
    GTEAM2,
    MISPTAG1,
    MISPTAG2,
    MISPTAG3,
    PTEAM1,
    PTEAM2,
    SAMPLE_SLACK_WEBHOOK_URL,
    TAG1,
    TAG2,
    TAG3,
    TOPIC1,
    TOPIC2,
    TOPIC3,
    TOPIC4,
    USER1,
    USER2,
    USER3,
    ZONE1,
    ZONE2,
    ZONE3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_ateam_invitation,
    accept_gteam_invitation,
    accept_pteam_invitation,
    accept_watching_request,
    assert_200,
    assert_204,
    create_actionlog,
    create_ateam,
    create_gteam,
    create_misp_tag,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    create_watching_request,
    create_zone,
    headers,
    invite_to_ateam,
    invite_to_gteam,
    invite_to_pteam,
    random_string,
    search_topics,
    update_topic,
)

client = TestClient(app)


def _pick_zone(zones_: List[schemas.ZoneEntry], zone_name_: str) -> Optional[schemas.ZoneEntry]:
    for zone in zones_:
        if zone.zone_name == zone_name_:
            return zone
    return None


def test_create_topic():
    user1 = create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    topic1 = create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
        zone_names=[ZONE1["zone_name"], ZONE2["zone_name"]],
    )

    assert topic1.topic_id == TOPIC1["topic_id"]
    assert topic1.title == TOPIC1["title"]
    assert topic1.abstract == TOPIC1["abstract"]
    assert topic1.threat_impact == TOPIC1["threat_impact"]
    assert topic1.created_by == user1.user_id
    assert isinstance(topic1.created_at, datetime)
    assert isinstance(topic1.updated_at, datetime)
    assert TOPIC1["tags"][0] in [t.tag_name for t in topic1.tags]
    assert TOPIC1["misp_tags"][0] in [m.tag_name for m in topic1.misp_tags]
    assert ACTION1["action"] in [a.action for a in topic1.actions]
    assert ACTION2["action"] in [a.action for a in topic1.actions]
    assert (zone1 := _pick_zone(topic1.zones, ZONE1["zone_name"]))
    assert zone1.zone_name == ZONE1["zone_name"]
    assert zone1.zone_info == ZONE1["zone_info"]
    assert zone1.gteam_id == gteam1.gteam_id
    assert (zone2 := _pick_zone(topic1.zones, ZONE2["zone_name"]))
    assert zone2.zone_name == ZONE2["zone_name"]
    assert zone2.zone_info == ZONE2["zone_info"]
    assert zone2.gteam_id == gteam1.gteam_id


def test_create_topic__with_new_tags():
    create_user(USER1)
    tag_str1 = "testtag:alpha:one"
    tag_str2 = "testtag:bravo:one"

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}"):
        create_topic(USER1, {**TOPIC1, "tags": [tag_str1]}, auto_create_tags=False)

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}, {tag_str2}"):
        create_topic(USER1, {**TOPIC1, "tags": [tag_str2, tag_str1]}, auto_create_tags=False)


def test_create_topic_and_action__with_new_tags():
    create_user(USER1)
    tag_str1 = "testtag:alpha:one"
    tag_str2 = "testtag:bravo:one"
    tag_str3 = "testtag:charlie:one"

    # raise error with non-exist tag
    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}"):
        create_topic(
            USER1,
            {
                **TOPIC1,
                "tags": [],
                "actions": [
                    {
                        **ACTION1,
                        "ext": {
                            "tags": [tag_str1],
                        },
                    },
                ],
            },
            auto_create_tags=False,
        )

    # sorted tags CSV
    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}, {tag_str2}"):
        create_topic(
            USER1,
            {
                **TOPIC1,
                "tags": [],
                "actions": [
                    {
                        **ACTION1,
                        "ext": {
                            "tags": [tag_str2, tag_str1],
                        },
                    },
                ],
            },
            auto_create_tags=False,
        )

    # sorted through topic tags and action tags
    with pytest.raises(
        HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}, {tag_str2}, {tag_str3}"
    ):
        create_topic(
            USER1,
            {
                **TOPIC1,
                "tags": [tag_str2, tag_str1],
                "actions": [
                    {
                        **ACTION1,
                        "ext": {
                            "tags": [tag_str3, tag_str1],
                        },
                    },
                ],
            },
            auto_create_tags=False,
        )


def test_send_webhook_when_topic_creation(mocker):
    from app.slack import _create_blocks_for_pteam

    # use mock to test slack webhook
    # TODO: should check posted http requests
    m = mocker.patch("app.slack.post_message")

    PTEAM1_WITH_SLACK_WEBHOOK_URL = {
        **PTEAM1,
        "slack_webhook_url": SAMPLE_SLACK_WEBHOOK_URL,
    }
    create_user(USER1)
    pteam1 = create_pteam(
        USER1,
        PTEAM1_WITH_SLACK_WEBHOOK_URL,
    )
    topic1 = create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
    )

    blocks = _create_blocks_for_pteam(
        pteam1.pteam_id,
        pteam1.pteam_name,
        topic1.tags[0].tag_id,
        topic1.tags[0].tag_name,
        topic1.topic_id,
        topic1.title,
        topic1.threat_impact,
    )

    m.assert_has_calls(
        [
            mocker.call(PTEAM1_WITH_SLACK_WEBHOOK_URL["slack_webhook_url"], blocks),
        ]
    )


def test_create_wrong_threat_level_topic():
    create_user(USER1)
    _topic = TOPIC1.copy()
    _topic["threat_impact"] = -1
    with pytest.raises(HTTPError, match="422: Unprocessable Entity"):
        create_topic(USER1, _topic)


def test_create_too_long_action():
    create_user(USER1)
    _action = ACTION1.copy()
    _action["action"] = random_string(1025)
    with pytest.raises(HTTPError, match="422: Unprocessable Entity"):
        create_topic(USER1, TOPIC1, actions=[_action])


def test_get_topic():
    user1 = create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})
    topic1 = create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
        zone_names=[ZONE1["zone_name"], ZONE2["zone_name"]],
    )

    response = client.get(f"/topics/{topic1.topic_id}", headers=headers(USER1))
    assert response.status_code == 200
    responsed_topic = schemas.TopicResponse(**response.json())
    assert responsed_topic.topic_id == TOPIC1["topic_id"]
    assert responsed_topic.title == TOPIC1["title"]
    assert responsed_topic.abstract == TOPIC1["abstract"]
    assert responsed_topic.threat_impact == TOPIC1["threat_impact"]
    assert responsed_topic.created_by == user1.user_id
    assert responsed_topic.created_at == topic1.created_at
    assert responsed_topic.updated_at == topic1.updated_at
    assert TOPIC1["tags"][0] in [t.tag_name for t in responsed_topic.tags]
    assert TOPIC1["misp_tags"][0] in [m.tag_name for m in responsed_topic.misp_tags]
    assert (zone1 := _pick_zone(topic1.zones, ZONE1["zone_name"]))
    assert zone1.zone_name == ZONE1["zone_name"]
    assert zone1.zone_info == ZONE1["zone_info"]
    assert zone1.gteam_id == gteam1.gteam_id
    assert (zone2 := _pick_zone(topic1.zones, ZONE2["zone_name"]))
    assert zone2.zone_name == ZONE2["zone_name"]
    assert zone2.zone_info == ZONE2["zone_info"]
    assert zone2.gteam_id == gteam1.gteam_id
    # actions are removed from TopicResponse.
    # use 'GET /topics/{tid}/actions/pteam/{pid}' to get actions.


def test_get_all_topics():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER2, GTEAM2)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    create_zone(USER1, gteam1.gteam_id, {"zone_name": "zoneA", "zone_info": "info a"})
    create_zone(USER2, gteam2.gteam_id, {"zone_name": "zoneB", "zone_info": "info b"})
    create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})

    create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2], zone_names=[ZONE1["zone_name"]])
    create_topic(USER1, TOPIC2, actions=[ACTION3], zone_names=[ZONE1["zone_name"]])
    create_topic(USER1, TOPIC3, zone_names=["zoneA"])
    create_topic(USER1, TOPIC4, zone_names=[])
    create_topic(USER2, {**TOPIC1, "topic_id": str(uuid4())}, zone_names=["zoneB"])

    response = client.get("/topics", headers=headers(USER1))
    assert response.status_code == 200
    responsed_topics = response.json()
    assert len(responsed_topics) == 4
    assert responsed_topics[0]["topic_id"] == str(TOPIC3["topic_id"])  # visible via gteam1
    assert responsed_topics[1]["topic_id"] == str(TOPIC1["topic_id"])
    assert responsed_topics[2]["topic_id"] == str(TOPIC4["topic_id"])
    assert responsed_topics[3]["topic_id"] == str(TOPIC2["topic_id"])


def test_update_topic():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})
    tag1 = create_tag(USER1, "omega")
    create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1],
        zone_names=[ZONE1["zone_name"]],
    )
    request = {
        "title": "topic one dash",
        "abstract": "abstract one dash",
        "threat_impact": 2,
        "tags": [tag1.tag_name],
        "misp_tags": ["tlp:white"],
        "zone_names": [ZONE2["zone_name"]],
    }
    response = client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1), json=request)

    assert response.status_code == 200
    responsed_topic = schemas.TopicResponse(**response.json())
    assert responsed_topic.title == request["title"]
    assert responsed_topic.title != TOPIC1["title"]
    assert responsed_topic.abstract == request["abstract"]
    assert responsed_topic.abstract != TOPIC1["abstract"]
    assert responsed_topic.threat_impact == request["threat_impact"]
    assert responsed_topic.threat_impact != TOPIC1["threat_impact"]
    assert request["tags"][0] in [tag.tag_name for tag in responsed_topic.tags]
    assert TOPIC1["tags"][0] not in [tag.tag_name for tag in responsed_topic.tags]
    assert request["misp_tags"][0] in [misp_tag.tag_name for misp_tag in responsed_topic.misp_tags]
    assert TOPIC1["misp_tags"][0] not in [
        misp_tag.tag_name for misp_tag in responsed_topic.misp_tags
    ]
    assert request["zone_names"][0] in [zone.zone_name for zone in responsed_topic.zones]
    assert ZONE1 not in [zone.zone_name for zone in responsed_topic.zones]


def test_update_topic__cannot_change_to_0_zones():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})
    create_topic(
        USER1,
        TOPIC1,
        actions=[{**ACTION1, "zone_names": [ZONE1["zone_name"]]}],  # 1 zone
        zone_names=[ZONE1["zone_name"]],  # 1 zone
    )
    request = {
        "title": "topic one dash",
        "zone_names": [],  # 0 zones
    }
    message = (
        "400: Bad Request: "
        "Once a topic has been zoned, it cannot be returned to public status. "
        "Consider deleting and recreating the topic."
    )
    with pytest.raises(HTTPError, match=message):
        assert_200(
            client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1), json=request)
        )


def test_update_topic__with_new_tags():
    create_user(USER1)
    tag1 = create_tag(USER1, "testtag:alphe:one")
    tag_str2 = "testtag:bravo:one"
    tag_str3 = "testtag:charlie:one"
    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name]})

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str2}"):
        assert_200(
            client.put(
                f"/topics/{topic1.topic_id}",
                headers=headers(USER1),
                json={"tags": [tag_str2]},  # change tags
            )
        )

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str2}"):
        assert_200(
            client.put(
                f"/topics/{topic1.topic_id}",
                headers=headers(USER1),
                json={"tags": [tag1.tag_name, tag_str2]},  # append tag
            )
        )

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str2}, {tag_str3}"):
        assert_200(
            client.put(
                f"/topics/{topic1.topic_id}",
                headers=headers(USER1),
                json={"tags": [tag_str3, tag1.tag_name, tag_str2]},  # append 2 tags unsorted
            )
        )


def test_update_topic_not_creater(testdb: Session):
    create_user(USER1)
    create_user(USER2)
    create_topic(USER1, TOPIC1, actions=[ACTION1])
    request = {"disabled": True}

    with pytest.raises(HTTPError, match=r"403: Forbidden: you are not topic creator"):
        assert_204(
            client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER2), json=request)
        )


def test_disable_topic():
    create_user(USER1)
    create_topic(USER1, TOPIC1, actions=[ACTION1])
    request = {"disabled": True}
    response = client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1), json=request)

    assert response.status_code == 200
    responsed_topic = schemas.TopicResponse(**response.json())
    assert responsed_topic.disabled is True


def test_delete_topic(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    tag1 = pteam1.tags[0]
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    create_actionlog(
        USER1,
        topic1.actions[0].action_id,
        topic1.topic_id,
        user1.user_id,
        pteam1.pteam_id,
        datetime.now(),
    )

    json_data = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": [str(user1.user_id)],
        "scheduled_at": str(datetime(2023, 6, 1)),
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
        json=json_data,
    )
    assert response.status_code == 200

    # delete topic
    response = client.delete(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1))
    assert response.status_code == 204

    topic = (
        testdb.query(models.Topic)
        .filter(models.Topic.topic_id == str(topic1.topic_id))
        .one_or_none()
    )
    assert topic is None

    assert (
        not testdb.query(models.TopicTag)
        .filter(models.TopicTag.topic_id == str(topic1.topic_id))
        .all()
    )

    assert (
        not testdb.query(models.TopicMispTag)
        .filter(models.TopicMispTag.topic_id == str(topic1.topic_id))
        .all()
    )

    assert (
        not testdb.query(models.PTeamTopicTagStatus)
        .filter(models.PTeamTopicTagStatus.topic_id == str(topic1.topic_id))
        .all()
    )

    assert (
        not testdb.query(models.TopicAction)
        .filter(models.TopicAction.topic_id == str(topic1.topic_id))
        .all()
    )

    # not delete ActionLog record
    assert (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.topic_id == str(topic1.topic_id))
        .all()
    )


def test_delete_topic_not_creater(testdb: Session):
    create_user(USER1)
    create_user(USER2)
    create_topic(USER1, TOPIC1, actions=[ACTION1])

    with pytest.raises(HTTPError, match=r"403: Forbidden: you are not topic creator"):
        assert_204(client.delete(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER2)))


def test_cannot_access_topic_without_related_zone():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER2, GTEAM2)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER2, gteam2.gteam_id, ZONE2)
    create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})
    create_topic(
        USER2,
        TOPIC1,
        actions=[ACTION1],
        zone_names=[ZONE2["zone_name"]],
    )
    error_message = "404: Not Found: You do not have related zone"
    with pytest.raises(HTTPError, match=error_message):
        assert_200(client.get(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1)))

    with pytest.raises(HTTPError, match=error_message):
        assert_200(client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1), json={}))

    with pytest.raises(HTTPError, match=error_message):
        assert_200(client.delete(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1)))


def test_get_pteam_topic_actions():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    create_zone(USER1, gteam1.gteam_id, ZONE3)
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})  # TAG1
    assert {zone.zone_name for zone in pteam1.zones} == {ZONE1["zone_name"]}
    action1_req = {**ACTION1, "zone_names": [ZONE1["zone_name"]]}
    action2_req = {**ACTION2, "zone_names": [ZONE2["zone_name"]]}
    action3_req = {**ACTION3, "zone_names": []}
    create_topic(
        USER1, TOPIC2, zone_names=[], actions=[action1_req, action2_req, action3_req]
    )  # noise
    topic1 = create_topic(
        USER1, TOPIC1, zone_names=[], actions=[action1_req, action2_req, action3_req]
    )

    def _find_action(resp_: dict, action_: str) -> dict:
        return next(filter(lambda x: x["action"] == action_, resp_["actions"]), {})

    data = assert_200(
        client.get(
            f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 2
    assert (act1 := _find_action(data, action1_req["action"]))  # zone matche
    assert {zone["zone_name"] for zone in act1["zones"]} == {ZONE1["zone_name"]}
    assert not _find_action(data, action2_req["action"])  # zone mismatche
    assert (act3 := _find_action(data, action3_req["action"]))  # no zonee
    assert {zone["zone_name"] for zone in act3["zones"]} == set()

    # multiple zones
    pteam2 = create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"], ZONE2["zone_name"]]})
    assert {zone.zone_name for zone in pteam2.zones} == {ZONE1["zone_name"], ZONE2["zone_name"]}
    action4_req = {**ACTION1, "zone_names": [ZONE1["zone_name"], ZONE2["zone_name"]]}
    action5_req = {**ACTION2, "zone_names": [ZONE1["zone_name"], ZONE3["zone_name"]]}
    action6_req = {**ACTION3, "zone_names": [ZONE3["zone_name"]]}
    topic3 = create_topic(
        USER1, TOPIC3, actions=[action4_req, action5_req, action6_req], zone_names=[]
    )
    data = assert_200(
        client.get(
            f"/topics/{topic3.topic_id}/actions/pteam/{pteam2.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 2
    assert (act4 := _find_action(data, action4_req["action"]))  # multiple match
    assert {zone["zone_name"] for zone in act4["zones"]} == {ZONE1["zone_name"], ZONE2["zone_name"]}
    assert (act5 := _find_action(data, action5_req["action"]))  # matche with mismatche
    assert {zone["zone_name"] for zone in act5["zones"]} == {ZONE1["zone_name"], ZONE3["zone_name"]}
    assert not _find_action(data, action6_req["action"])  # not match

    # no zoneed pteam
    pteam3 = create_pteam(USER1, {**PTEAM1, "zone_names": []})
    assert {zone.zone_name for zone in pteam3.zones} == set()
    data = assert_200(
        client.get(
            f"/topics/{topic1.topic_id}/actions/pteam/{pteam3.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 1
    assert not _find_action(data, action1_req["action"])
    assert not _find_action(data, action2_req["action"])
    assert (act3 := _find_action(data, action3_req["action"]))
    assert {zone["zone_name"] for zone in act3["zones"]} == set()  # not zoneed actions only
    data = assert_200(
        client.get(
            f"/topics/{topic3.topic_id}/actions/pteam/{pteam3.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 0

    # via ateam
    create_user(USER2)
    ateam1 = create_ateam(USER2, ATEAM1)
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(
            client.get(
                f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER2)
            )
        )

    watching_request1 = create_watching_request(USER2, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)
    assert_200(
        client.get(
            f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER2)
        )
    )


def test_get_pteam_topic_actions__errors():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [ZONE1["zone_name"]]})
    create_pteam(USER2, {**PTEAM2, "zone_names": [ZONE2["zone_name"]]})
    topic1 = create_topic(USER1, TOPIC1, zone_names=[ZONE2["zone_name"]])

    # wrong topic_id
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.get(
                f"/topics/{pteam1.pteam_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
            )
        )

    # pteam1 not having ZONE2
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic id"):
        assert_200(
            client.get(
                f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
            )
        )

    # user2 having ZONE2 but not a member of pteam1
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(
            client.get(
                f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER2)
            )
        )

    # wrong pteam_id (having ZONE2)
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam"):
        assert_200(
            client.get(
                f"/topics/{topic1.topic_id}/actions/pteam/{topic1.topic_id}", headers=headers(USER2)
            )
        )


class TestGetUserTopicActions:
    class _Common:
        tag1: schemas.TagResponse
        pteam1: schemas.PTeamInfo
        pteam2: schemas.PTeamInfo
        ateam1: schemas.ATeamInfo
        ateam2: schemas.ATeamInfo
        gteam1: schemas.GTeamInfo
        gteam2: schemas.GTeamInfo
        zone1: schemas.ZoneInfo
        zone2: schemas.ZoneInfo
        action_req1: dict = {**ACTION1, "zone_names": [ZONE1["zone_name"]]}
        action_req2: dict = {**ACTION2, "zone_names": [ZONE2["zone_name"]]}
        action_req3: dict = {**ACTION3, "zone_names": []}
        topic_base1: dict = {**TOPIC1, "tags": [TAG1], "zone_names": []}
        topic1: schemas.TopicResponse

        def _common_setup(self):
            create_user(USER1)  # super user
            create_user(USER2)  # account for test
            self.tag1 = create_tag(USER1, TAG1)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            self.pteam2 = create_pteam(USER1, PTEAM2)
            self.ateam1 = create_ateam(USER1, ATEAM1)
            self.ateam2 = create_ateam(USER1, ATEAM2)
            self.gteam1 = create_gteam(USER1, GTEAM1)
            self.gteam2 = create_gteam(USER1, GTEAM1)
            self.zone1 = create_zone(USER1, self.gteam1.gteam_id, ZONE1)
            self.zone2 = create_zone(USER1, self.gteam2.gteam_id, ZONE2)
            self.topic1 = create_topic(
                USER1,
                {
                    **self.topic_base1,
                    "actions": [self.action_req1, self.action_req2, self.action_req3],
                },
            )
            create_topic(  # noise
                USER1,
                {
                    **self.topic_base1,
                    "topic_id": uuid4(),
                    "actions": [self.action_req1, self.action_req2, self.action_req3],
                },
            )

        @staticmethod
        def find_action(
            actions: List[schemas.ActionResponse],
            target: dict,
        ):
            return next(filter(lambda x: x.action == target["action"], actions), None)

        def get_topic1_actions(self) -> List[schemas.ActionResponse]:
            data = assert_200(
                client.get(
                    f"/topics/{self.topic1.topic_id}/actions/user/me", headers=headers(USER2)
                )
            )
            return [schemas.ActionResponse(**action) for action in data]

        def set_pteam_zones(self, pteam: schemas.PTeamInfo, zones: List[schemas.ZoneInfo]):
            request = {"zone_names": [zone.zone_name for zone in zones]}
            assert_200(
                client.put(f"/pteams/{pteam.pteam_id}", headers=headers(USER1), json=request)
            )

    class TestWithoutTeams(_Common):
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self._common_setup()

        def test_without_teams(self):
            actions = self.get_topic1_actions()
            assert len(actions) == 1
            assert self.find_action(actions, self.action_req3)  # action3 is public

    class TestWithPTeam(_Common):
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self._common_setup()
            invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
            accept_pteam_invitation(USER2, invitation1.invitation_id)
            # USER2 is a member of pteam1

        def test_without_pteam_zone(self):
            actions = self.get_topic1_actions()
            assert len(actions) == 1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_pteam_zone(self):
            self.set_pteam_zones(self.pteam1, [self.zone1])
            self.set_pteam_zones(self.pteam2, [self.zone2])  # noise

            actions = self.get_topic1_actions()
            assert len(actions) == 2
            assert self.find_action(actions, self.action_req1)  # zone1 via pteam1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_multiple_pteam_zones(self):
            self.set_pteam_zones(self.pteam1, [self.zone1])
            self.set_pteam_zones(self.pteam2, [self.zone2])
            invitation2 = invite_to_pteam(USER1, self.pteam2.pteam_id)
            accept_pteam_invitation(USER2, invitation2.invitation_id)

            actions = self.get_topic1_actions()
            assert len(actions) == 3
            assert self.find_action(actions, self.action_req1)  # zone1 via pteam1
            assert self.find_action(actions, self.action_req2)  # zone2 via pteam2
            assert self.find_action(actions, self.action_req3)  # action3 is public

    class TestWithATeam(_Common):
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self._common_setup()
            invitation1 = invite_to_ateam(USER1, self.ateam1.ateam_id)
            accept_ateam_invitation(USER2, invitation1.invitation_id)
            # USER2 is a member of ateam1

        def test_without_pteam(self):
            actions = self.get_topic1_actions()
            assert len(actions) == 1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_pteam_without_zone(self):
            watching_request = create_watching_request(USER1, self.ateam1.ateam_id)
            accept_watching_request(USER1, watching_request.request_id, self.pteam1.pteam_id)

            actions = self.get_topic1_actions()
            assert len(actions) == 1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_zoned_pteam(self):
            watching_request = create_watching_request(USER1, self.ateam1.ateam_id)
            accept_watching_request(USER1, watching_request.request_id, self.pteam1.pteam_id)
            self.set_pteam_zones(self.pteam1, [self.zone1])
            self.set_pteam_zones(self.pteam2, [self.zone2])  # noise

            actions = self.get_topic1_actions()
            assert len(actions) == 2
            assert self.find_action(actions, self.action_req1)  # action1 via pteam1 via ateam1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_multiple_zoned_pteams(self):
            watching_request1 = create_watching_request(USER1, self.ateam1.ateam_id)
            accept_watching_request(USER1, watching_request1.request_id, self.pteam1.pteam_id)
            watching_request2 = create_watching_request(USER1, self.ateam1.ateam_id)
            accept_watching_request(USER1, watching_request2.request_id, self.pteam2.pteam_id)
            self.set_pteam_zones(self.pteam1, [self.zone1])
            self.set_pteam_zones(self.pteam2, [self.zone2])

            actions = self.get_topic1_actions()
            assert len(actions) == 3
            assert self.find_action(actions, self.action_req1)  # action1 via pteam1 via ateam1
            assert self.find_action(actions, self.action_req2)  # action2 via pteam1 via ateam1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_multiple_ateams(self):
            watching_request1 = create_watching_request(USER1, self.ateam1.ateam_id)
            accept_watching_request(USER1, watching_request1.request_id, self.pteam1.pteam_id)
            watching_request2 = create_watching_request(USER1, self.ateam2.ateam_id)
            accept_watching_request(USER1, watching_request2.request_id, self.pteam2.pteam_id)
            self.set_pteam_zones(self.pteam1, [self.zone1])
            self.set_pteam_zones(self.pteam2, [self.zone2])
            invitation2 = invite_to_ateam(USER1, self.ateam2.ateam_id)
            accept_ateam_invitation(USER2, invitation2.invitation_id)

            actions = self.get_topic1_actions()
            assert len(actions) == 3
            assert self.find_action(actions, self.action_req1)  # action1 via pteam1 via ateam1
            assert self.find_action(actions, self.action_req2)  # action2 via pteam2 via ateam2
            assert self.find_action(actions, self.action_req3)  # action3 is public

    class TestWithGTeam(_Common):
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self._common_setup()
            invitation1 = invite_to_gteam(USER1, self.gteam1.gteam_id)
            accept_gteam_invitation(USER2, invitation1.invitation_id)
            # USER2 is a member of gteam1

        def test_with_gteam(self):
            actions = self.get_topic1_actions()
            assert len(actions) == 2
            assert self.find_action(actions, self.action_req1)  # action1 via gteam1
            assert self.find_action(actions, self.action_req3)  # action3 is public

        def test_with_multiple_gteams(self):
            invitation2 = invite_to_gteam(USER1, self.gteam2.gteam_id)
            accept_gteam_invitation(USER2, invitation2.invitation_id)

            actions = self.get_topic1_actions()
            assert len(actions) == 3
            assert self.find_action(actions, self.action_req1)  # action1 via gteam1
            assert self.find_action(actions, self.action_req2)  # action2 via gteam2
            assert self.find_action(actions, self.action_req3)  # action3 is public

    class TestErrors(_Common):
        random_uuid: UUID

        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self._common_setup()
            self.random_uuid = uuid4()

        def set_topic1_zones(self, zones: List[schemas.ZoneInfo]):
            request = {"zone_names": [zone.zone_name for zone in zones]}
            assert_200(
                client.put(f"/topics/{self.topic1.topic_id}", headers=headers(USER1), json=request)
            )

        def test_wrong_topic_id(self):
            with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
                assert_200(
                    client.get(
                        f"/topics/{self.random_uuid}/actions/user/me", headers=headers(USER2)
                    )
                )

        def test_not_visible_topic(self):
            # pteam1 have zone1 only
            self.set_topic1_zones([self.zone2])  # set zone2 instead of zone1

            with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
                assert_200(
                    client.get(
                        f"/topics/{self.topic1.topic_id}/actions/user/me", headers=headers(USER2)
                    )
                )


def test_create_topic_actions():
    create_user(USER1)
    create_user(USER2)
    parent1 = create_tag(USER1, "alpha:alpha:")
    child11 = create_tag(USER1, "alpha:alpha:alpha1")
    child21 = create_tag(USER1, "bravo:bravo:bravo1")
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER2, GTEAM2)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER2, gteam2.gteam_id, ZONE2)

    def _gen_topic(tags: List[str], zone_names: List[str], actions: List[dict]) -> dict:
        return {
            **TOPIC1,
            "topic_id": str(uuid4()),
            "tags": tags,
            "zone_names": zone_names,
            "actions": actions,
        }

    def _gen_action(tags: List[str], zone_names: List[str]) -> dict:
        return {
            "action_id": None,
            "action": "action " + str(uuid4()),
            "action_type": "elimination",
            "recommended": True,
            "zone_names": zone_names,
            "ext": {
                "tags": tags,
                "vulnerable_versions": {},
            },
        }

    def _pick_action(topic: dict, action: dict) -> dict:
        return next(filter(lambda x: x["action"] == action["action"], topic["actions"]), {})

    def _zone_strs(zones: Union[List[str], List[dict]]) -> Set[str]:
        return {x["zone_name"] if isinstance(x, dict) else x for x in zones}

    def _cmp_actions(alpha: dict, bravo: dict) -> bool:
        for key in alpha.keys():
            if key == "topic_id":
                if (t_a := alpha.get(key)) and (t_b := bravo.get(key)) and t_a != t_b:
                    return False
                # ignore missing topic_id
            elif key == "action_id":
                if alpha[key] and bravo[key] and alpha[key] != bravo[key]:
                    return False
            elif key == "created_by" or key == "created_at":
                continue
            elif key == "zones":
                if _zone_strs(alpha[key]) != _zone_strs(bravo["zone_names"]):
                    return False
            elif key == "zone_names":
                if _zone_strs(alpha[key]) != _zone_strs(bravo["zones"]):
                    return False
            elif alpha[key] != bravo[key]:
                return False
        return True

    # ordinary topic and actions
    action1 = _gen_action([], [])
    action2 = _gen_action([child11.tag_name], [])
    action3 = _gen_action([parent1.tag_name], [])
    topic1 = _gen_topic([parent1.tag_name], [], [action1, action2, action3])
    data = assert_200(
        client.post(f"/topics/{topic1['topic_id']}", headers=headers(USER1), json=topic1)
    )
    assert data["topic_id"] == topic1["topic_id"]
    assert len(data["actions"]) == 3
    assert _cmp_actions((r_action1 := _pick_action(data, action1)), action1)
    assert _cmp_actions((r_action2 := _pick_action(data, action2)), action2)
    assert _cmp_actions((r_action3 := _pick_action(data, action3)), action3)
    assert UUID(r_action1["action_id"])
    assert UUID(r_action2["action_id"])
    assert UUID(r_action3["action_id"])

    # with wrong tagged action
    action4 = _gen_action([child21.tag_name], [])
    topic2 = _gen_topic([parent1.tag_name], [], [action4])
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        data = assert_200(
            client.post(f"/topics/{topic2['topic_id']}", headers=headers(USER1), json=topic2)
        )

    # with zones
    action5 = _gen_action([], [])
    action6 = _gen_action([], [zone1.zone_name])
    topic3 = _gen_topic([], [], [action5, action6])
    data = assert_200(
        client.post(f"/topics/{topic3['topic_id']}", headers=headers(USER1), json=topic3)
    )
    assert data["topic_id"] == topic3["topic_id"]
    assert len(data["actions"]) == 2
    assert _cmp_actions((r_action5 := _pick_action(data, action5)), action5)
    assert _cmp_actions((r_action6 := _pick_action(data, action6)), action6)
    assert UUID(r_action5["action_id"])
    assert UUID(r_action6["action_id"])

    # with wrong zone
    action7 = _gen_action([], [zone2.zone_name])
    topic4 = _gen_topic([], [], [action7])
    with pytest.raises(HTTPError, match=r"400: Bad Request: You do not have related zone"):
        data = assert_200(
            client.post(f"/topics/{topic4['topic_id']}", headers=headers(USER1), json=topic4)
        )


def test_create_topic_actions__with_action_id():
    create_user(USER1)
    parent1 = create_tag(USER1, "alpha:alpha:")
    child11 = create_tag(USER1, "alpha:alpha:alpha1")

    def _gen_action(action_id: Optional[UUID]) -> dict:
        return {
            "action_id": str(action_id) if action_id else None,
            "action": f"action for {action_id}",
            "action_type": "elimination",
            "recommended": True,
            "zone_names": [],
            "ext": {"tags": [child11.tag_name]},
        }

    def _gen_topic(tags: List[str], actions: List[dict]) -> dict:
        return {
            **TOPIC1,
            "topic_id": str(uuid4()),
            "tags": tags,
            "actions": actions,
        }

    def _pick_action(topic: dict, action_id: UUID) -> dict:
        return next(filter(lambda x: x["action_id"] == str(action_id), topic["actions"]), {})

    def _zone_strs(zones: Union[List[str], List[dict]]) -> Set[str]:
        return {x["zone_name"] if isinstance(x, dict) else x for x in zones}

    def _cmp_actions(alpha: dict, bravo: dict) -> bool:
        for key in alpha.keys():
            if key == "topic_id":
                if (t_a := alpha.get(key)) and (t_b := bravo.get(key)) and t_a != t_b:
                    return False
                # ignore missing topic_id
            elif key == "created_by" or key == "created_at":
                continue
            elif key == "zones":
                if _zone_strs(alpha[key]) != _zone_strs(bravo["zone_names"]):
                    return False
            elif alpha[key] != bravo[key]:
                return False
        return True

    # ambiguous action id
    action1 = _gen_action(uuid4())
    topic1 = _gen_topic([parent1.tag_name], [action1, action1])
    with pytest.raises(HTTPError, match=r"400: Bad Request: Ambiguous action ids"):
        assert_200(
            client.post(f"/topics/{topic1['topic_id']}", headers=headers(USER1), json=topic1)
        )

    # with new action id
    topic1 = _gen_topic([parent1.tag_name], [action1])
    data = assert_200(
        client.post(f"/topics/{topic1['topic_id']}", headers=headers(USER1), json=topic1)
    )
    assert len(topic1["actions"]) == 1
    assert _cmp_actions(_pick_action(data, action1["action_id"]), action1)

    # reuse action id
    action2 = _gen_action(action1["action_id"])
    topic2 = _gen_topic([parent1.tag_name], [action2])
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action id already exists"):
        assert_200(
            client.post(f"/topics/{topic2['topic_id']}", headers=headers(USER1), json=topic2)
        )

    # with new action id
    action2 = _gen_action(uuid4())
    topic2 = _gen_topic([parent1.tag_name], [action2])
    data = assert_200(
        client.post(f"/topics/{topic2['topic_id']}", headers=headers(USER1), json=topic2)
    )
    assert len(topic2["actions"]) == 1
    assert _cmp_actions(_pick_action(data, action2["action_id"]), action2)


class TestTopicContentFingerprint:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        create_tag(USER1, TAG1)
        create_tag(USER1, TAG2)
        create_tag(USER1, TAG3)

    def _get_topic(self, topic_id: UUID) -> schemas.TopicResponse:
        data = assert_200(client.get(f"/topics/{topic_id}", headers=headers(USER1)))
        return schemas.TopicResponse(**data)

    def _update_topic(self, topic_id: UUID, request: dict) -> schemas.TopicResponse:
        data = assert_200(client.put(f"/topics/{topic_id}", headers=headers(USER1), json=request))
        return schemas.TopicResponse(**data)

    def test_updated_on_title_changed(self):
        topic1 = create_topic(USER1, TOPIC1)
        content_fingerprint1 = topic1.content_fingerprint
        assert len(content_fingerprint1) > 0

        # update title
        topic1a = self._update_topic(topic1.topic_id, {"title": topic1.title + "x"})
        content_fingerprint1a = topic1a.content_fingerprint
        assert len(content_fingerprint1a) > 0
        assert content_fingerprint1a != content_fingerprint1

        # revert title update
        topic1b = self._update_topic(topic1.topic_id, {"title": TOPIC1["title"]})
        content_fingerprint1b = topic1b.content_fingerprint
        assert content_fingerprint1b == content_fingerprint1

    def test_updated_on_abstract_changed(self):
        topic1 = create_topic(USER1, TOPIC1)
        content_fingerprint1 = topic1.content_fingerprint
        assert len(content_fingerprint1) > 0

        # update abstract
        topic1a = self._update_topic(topic1.topic_id, {"abstract": topic1.abstract + "x"})
        content_fingerprint1a = topic1a.content_fingerprint
        assert len(content_fingerprint1a) > 0
        assert content_fingerprint1a != content_fingerprint1

        # revert abstract update
        topic1b = self._update_topic(topic1.topic_id, {"abstract": TOPIC1["abstract"]})
        content_fingerprint1b = topic1b.content_fingerprint
        assert content_fingerprint1b == content_fingerprint1

    def test_updated_on_threat_impact_changed(self):
        topic1 = create_topic(USER1, TOPIC1)
        content_fingerprint1 = topic1.content_fingerprint
        assert len(content_fingerprint1) > 0

        # update threat_impact
        new_threat_impact = (topic1.threat_impact + 1) % 4 + 1
        topic1a = self._update_topic(topic1.topic_id, {"threat_impact": new_threat_impact})
        content_fingerprint1a = topic1a.content_fingerprint
        assert len(content_fingerprint1a) > 0
        assert content_fingerprint1a != content_fingerprint1

        # revert threat_impact update
        topic1b = self._update_topic(topic1.topic_id, {"threat_impact": TOPIC1["threat_impact"]})
        content_fingerprint1b = topic1b.content_fingerprint
        assert content_fingerprint1b == content_fingerprint1

    def test_updated_on_tags_changed(self):
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [TAG1, TAG2]})
        content_fingerprint1 = topic1.content_fingerprint
        assert len(content_fingerprint1) > 0

        # update tags
        topic1a = self._update_topic(topic1.topic_id, {"tags": [TAG2, TAG3]})
        content_fingerprint1a = topic1a.content_fingerprint
        assert len(content_fingerprint1a) > 0
        assert content_fingerprint1a != content_fingerprint1

        # revert tags update
        topic1b = self._update_topic(topic1.topic_id, {"tags": [TAG2, TAG1]})
        content_fingerprint1b = topic1b.content_fingerprint
        assert content_fingerprint1b == content_fingerprint1

    def test_not_updated_on_misp_tags_changed(self):
        topic1 = create_topic(USER1, {**TOPIC1, "misp_tags": [MISPTAG1]})
        content_fingerprint1 = topic1.content_fingerprint
        assert len(content_fingerprint1) > 0

        # update misp_tags
        topic1a = self._update_topic(topic1.topic_id, {"misp_tags": [MISPTAG1, MISPTAG2]})
        content_fingerprint1a = topic1a.content_fingerprint
        assert content_fingerprint1a == content_fingerprint1

    # TODO: add the cases other attributes updated


@pytest.mark.skip(reason="TODO: should be tested with flashsense")  # TODO
def test_fetch_data_from_flashsense():
    pass


class TestSearchTopics:
    class Common_:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self.user1 = create_user(USER1)
            self.user2 = create_user(USER2)
            self.user3 = create_user(USER3)
            self.tag1 = create_tag(USER1, TAG1)
            self.tag2 = create_tag(USER1, TAG2)
            self.tag3 = create_tag(USER1, TAG3)
            self.misp_tag1 = create_misp_tag(USER1, MISPTAG1)
            self.misp_tag2 = create_misp_tag(USER1, MISPTAG2)
            self.misp_tag3 = create_misp_tag(USER1, MISPTAG3)
            self.gteam1 = create_gteam(USER1, GTEAM1)
            self.gteam2 = create_gteam(USER2, GTEAM2)
            self.zone1 = create_zone(USER1, self.gteam1.gteam_id, ZONE1)
            self.zone2 = create_zone(USER2, self.gteam2.gteam_id, ZONE2)
            self.zone3 = create_zone(USER1, self.gteam1.gteam_id, ZONE3)

        @staticmethod
        def create_minimal_topic(user: dict, params: dict) -> schemas.TopicCreateResponse:
            minimal_topic = {
                "topic_id": uuid4(),
                "title": "",
                "abstract": "",
                "threat_impact": 1,
                **params,
            }
            return create_topic(user, minimal_topic)

        @staticmethod
        def try_search_topics(user, topics_dict, search_params, expected):
            if isinstance(expected, str):
                with pytest.raises(HTTPError, match=expected):
                    search_topics(user, search_params)
                return
            result = search_topics(user, search_params)
            assert {topic.topic_id for topic in result.topics} == {
                topics_dict[idx].topic_id for idx in expected
            }

    class TestSearchByThreatImpact(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_threat_impact(self):
            self.topic1 = self.create_minimal_topic(USER1, {"threat_impact": 1})
            self.topic2 = self.create_minimal_topic(USER1, {"threat_impact": 2})
            self.topic3 = self.create_minimal_topic(USER1, {"threat_impact": 3})
            self.topic4 = self.create_minimal_topic(USER1, {"threat_impact": 4})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3, 4}),
                ("0", set()),
                ("1", {1}),
                ("2", {2}),
                ("3", {3}),
                ("4", {4}),
                ("5", set()),
                ("x", set()),
                ("1|2", {1, 2}),
                ("", set()),  # reserved keyword for empty does not make sense
                ("1|x", {1}),  # wrong params are just ignored
            ],
        )
        def test_search_by_threat_impact(self, search_words, expected):
            search_params = {} if search_words is None else {"threat_impacts": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByTitle(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_title(self):
            self.topic1 = self.create_minimal_topic(USER1, {"title": "topic one"})
            self.topic2 = self.create_minimal_topic(USER1, {"title": "TOPIC TWO"})
            self.topic3 = self.create_minimal_topic(USER1, {"title": "topic three"})
            self.topic4 = self.create_minimal_topic(USER1, {"title": "Topic Four"})
            self.topic5 = self.create_minimal_topic(USER1, {"title": ""})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
                5: self.topic5,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3, 4, 5}),
                ("one", {1}),
                ("topic", {1, 2, 3, 4}),  # case-insensitive
                (" t", {2, 3}),  # spaces also considered
                ("x", set()),
                ("", {5}),  # "" is the reserved keyword means empty
                ("|w", {2, 5}),
            ],
        )
        def test_search_by_title(self, search_words, expected):
            search_params = {} if search_words is None else {"title_words": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByAbstract(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_abstract(self):
            self.topic1 = self.create_minimal_topic(USER1, {"abstract": "abstract one"})
            self.topic2 = self.create_minimal_topic(USER1, {"abstract": "Abstract TWO"})
            self.topic3 = self.create_minimal_topic(USER1, {"abstract": "abstract three"})
            self.topic4 = self.create_minimal_topic(USER1, {"abstract": "Abstract Four"})
            self.topic5 = self.create_minimal_topic(USER1, {"abstract": ""})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
                5: self.topic5,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3, 4, 5}),
                ("one", {1}),
                ("abstract", {1, 2, 3, 4}),  # case-insensitive
                (" t", {2, 3}),  # spaces also considered
                ("x", set()),
                ("", {5}),  # "" is the reserved keyword means empty
                ("|w", {2, 5}),
            ],
        )
        def test_search_by_abstract(self, search_words, expected):
            search_params = {} if search_words is None else {"abstract_words": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByTag(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_tag(self):
            self.topic1 = self.create_minimal_topic(USER1, {"tags": [TAG1]})
            self.topic2 = self.create_minimal_topic(USER1, {"tags": [TAG2]})
            self.topic3 = self.create_minimal_topic(USER1, {"tags": [TAG1, TAG2]})
            self.topic4 = self.create_minimal_topic(USER1, {"tags": []})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3, 4}),
                (TAG1, {1, 3}),
                (TAG2, {2, 3}),
                (TAG3, set()),  # unused tag
                ("xxx", set()),  # not existed tag
                ("", {4}),  # "" is the reserved keyword means empty
                (f"|{TAG1}", {1, 3, 4}),
            ],
        )
        def test_search_by_tag(self, search_words, expected):
            search_params = {} if search_words is None else {"tag_names": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

        def test_search_by_parent_tag(self):
            assert self.tag1.parent_name
            assert self.tag1.parent_name != self.tag1.tag_name  # TAG1 is a child tag
            search_params = {"tag_names": self.tag1.parent_name}
            # currently searching by parent does not return matched with child
            self.try_search_topics(USER1, self.topics, search_params, set())

    class TestSearchByMispTag(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_misp_tag(self):
            self.topic1 = self.create_minimal_topic(USER1, {"misp_tags": [MISPTAG1]})
            self.topic2 = self.create_minimal_topic(USER1, {"misp_tags": [MISPTAG2]})
            self.topic3 = self.create_minimal_topic(USER1, {"misp_tags": [MISPTAG1, MISPTAG2]})
            self.topic4 = self.create_minimal_topic(USER1, {"misp_tags": []})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3, 4}),
                (MISPTAG1, {1, 3}),
                (MISPTAG2, {2, 3}),
                (MISPTAG3, set()),  # unused misp_tag
                ("xxx", set()),  # not existed misp_tag
                ("", {4}),  # "" is the reserved keyword means empty
                (f"|{MISPTAG1}", {1, 3, 4}),
            ],
        )
        def test_search_by_misp_tag(self, search_words, expected):
            search_params = {} if search_words is None else {"misp_tag_names": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByZone(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_zone(self):
            self.topic1 = self.create_minimal_topic(USER1, {"zone_names": [ZONE1["zone_name"]]})
            self.topic2 = self.create_minimal_topic(USER2, {"zone_names": [ZONE2["zone_name"]]})
            self.topic3 = self.create_minimal_topic(
                USER1, {"zone_names": [ZONE1["zone_name"], ZONE3["zone_name"]]}
            )
            self.topic4 = self.create_minimal_topic(USER1, {"zone_names": []})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 3, 4}),  # USER1 cannot access to ZONE2(topic2)
                (ZONE1["zone_name"], {1, 3}),
                (ZONE2["zone_name"], "403: Forbidden: You do not have related zone"),
                ("xxx", set()),  # not existed zone_name
                ("", {4}),  # "" is the reserved keyword means empty|public
                (f"|{ZONE3['zone_name']}", {3, 4}),
            ],
        )
        def test_search_by_zone(self, search_words, expected):
            search_params = {} if search_words is None else {"zone_names": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {2, 4}),  # USER2 cannot access to ZONE1, ZONE3
                (ZONE1["zone_name"], "403: Forbidden: You do not have related zone"),
                (ZONE2["zone_name"], {2}),
                ("xxx", set()),  # not existed zone_name
                ("", {4}),  # "" is the reserved keyword means empty|public
                (f"|{ZONE3['zone_name']}", "403: Forbidden: You do not have related zone"),
            ],
        )
        def test_search_by_zone_by_another(self, search_words, expected):
            search_params = {} if search_words is None else {"zone_names": search_words}
            self.try_search_topics(USER2, self.topics, search_params, expected)  # by USER2

        @pytest.fixture(scope="function", autouse=False)
        def setup_for_complexed_topic5(self):
            # user1 join to gteam2
            g_invitation = invite_to_gteam(USER2, self.gteam2.gteam_id)
            accept_gteam_invitation(USER1, g_invitation.invitation_id)
            self.topic5 = self.create_minimal_topic(
                USER1, {"zone_names": [ZONE1["zone_name"], ZONE2["zone_name"]]}
            )
            self.topics[5] = self.topic5
            # user1 leave gteam2
            assert_204(
                client.delete(
                    f"/gteams/{self.gteam2.gteam_id}/members/{self.user1.user_id}",
                    headers=headers(USER1),
                )
            )
            # now topic5 has accessible ZONE1 and inaccessible ZONE2 (from USER1)

        @pytest.mark.parametrize(
            "search_words, user1_expected, user2_expected",
            [
                (None, {1, 3, 4, 5}, {2, 4, 5}),
                (ZONE1["zone_name"], {1, 3, 5}, "403: Forbidden: You do not have related zone"),
                (ZONE2["zone_name"], "403: Forbidden: You do not have related zone", {2, 5}),
                ("xxx", set(), set()),
                ("", {4}, {4}),
                (f"|{ZONE3['zone_name']}", {3, 4}, "403: Forbidden: You do not have"),
            ],
        )
        def test_search_by_zone_complex(
            self,
            setup_for_complexed_topic5,
            search_words,
            user1_expected,
            user2_expected,
        ):
            search_params = {} if search_words is None else {"zone_names": search_words}
            self.try_search_topics(USER1, self.topics, search_params, user1_expected)
            self.try_search_topics(USER2, self.topics, search_params, user2_expected)

    class TestSearchByTopicId(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_topic_id(self):
            self.topic1 = self.create_minimal_topic(USER1, {})
            self.topic2 = self.create_minimal_topic(USER1, {})
            self.topic3 = self.create_minimal_topic(USER1, {})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3}),
                ("TOPIC1", {1}),
                ("TOPIC1|TOPIC2", {1, 2}),
                ("x", set()),  # wrong uuid
                (str(uuid4()), set()),  # uuid4 but not a valid topic_id
                ("", set()),  # reserved keyword for empty does not make sense
                ("|TOPIC1", {1}),
            ],
        )
        def test_search_by_topic_id(self, search_words, expected):
            search_params = (
                {}
                if search_words is None
                else {
                    "topic_ids": search_words.replace("TOPIC1", str(self.topic1.topic_id)).replace(
                        "TOPIC2", str(self.topic2.topic_id)
                    )
                }
            )
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByCreator(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_creator(self):
            self.topic1 = self.create_minimal_topic(USER1, {})
            self.topic2 = self.create_minimal_topic(USER2, {})
            self.topic3 = self.create_minimal_topic(USER3, {})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3}),
                ("USER1", {1}),
                ("USER1|USER2", {1, 2}),
                ("x", set()),  # wrong uuid
                (str(uuid4()), set()),  # uuid4 but not a valid user_id
                ("", set()),  # reserved keyword for empty does not make sense
                ("|USER1", {1}),
            ],
        )
        def test_search_by_creator(self, search_words, expected):
            search_params = (
                {}
                if search_words is None
                else {
                    "creator_ids": search_words.replace("USER1", str(self.user1.user_id)).replace(
                        "USER2", str(self.user2.user_id)
                    )
                }
            )
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByCreatedTime(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_createdtime(self):
            self.timestamp0 = datetime.now()
            self.topic1 = self.create_minimal_topic(USER1, {})
            self.timestamp1 = datetime.now()
            self.topic2 = self.create_minimal_topic(USER1, {})
            self.timestamp2 = datetime.now()
            self.topic3 = self.create_minimal_topic(USER1, {})
            self.timestamp3 = datetime.now()
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
            }
            self.timestamps = {
                "TS0": self.timestamp0,
                "TS1": self.timestamp1,
                "TS2": self.timestamp2,
                "TS3": self.timestamp3,
            }

        @pytest.mark.parametrize(
            "after, before, expected",
            [
                (None, None, {1, 2, 3}),
                ("xxx", None, "422: Unprocessable Entity:"),  # wrong datetime string
                (None, "xxx", "422: Unprocessable Entity:"),  # wrong datetime string
                ("", None, {1, 2, 3}),  # reserved keyword does not make sense
                (None, "", {1, 2, 3}),  # reserved keyword does not make sense
                ("TS0", None, {1, 2, 3}),
                ("TS1", None, {2, 3}),
                ("TS3", None, set()),
                (None, "TS0", set()),
                (None, "TS1", {1}),
                (None, "TS2", {1, 2}),
                ("TS0", "TS3", {1, 2, 3}),
                ("TS1", "TS3", {2, 3}),
                ("TS1", "TS2", {2}),
                ("TS2", "TS2", set()),
                ("TS2", "TS1", set()),  # ambiguous (after > before) does not cause error
            ],
        )
        def test_search_by_createdtime(self, after, before, expected):
            fixed_after = self.timestamps.get(after, after)
            fixed_before = self.timestamps.get(before, before)
            search_params = {}
            if fixed_after:
                search_params["created_after"] = fixed_after
            if fixed_before:
                search_params["created_before"] = fixed_before
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class TestSearchByUpdatedTime(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_updatedtime(self):
            self.topic1 = self.create_minimal_topic(USER1, {})
            self.topic2 = self.create_minimal_topic(USER1, {})
            self.timestamp0 = datetime.now()
            self.topic3 = self.create_minimal_topic(USER1, {})
            self.timestamp1 = datetime.now()
            update_topic(USER1, self.topic2, {"threat_impact": 3})
            self.timestamp2 = datetime.now()
            update_topic(USER1, self.topic1, {"threat_impact": 2})
            self.timestamp3 = datetime.now()
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
            }
            self.timestamps = {
                "TS0": self.timestamp0,
                # topic3 created
                "TS1": self.timestamp1,
                # topic2 updated
                "TS2": self.timestamp2,
                # topic1 updated
                "TS3": self.timestamp3,
            }

        @pytest.mark.parametrize(
            "after, before, expected",
            [
                (None, None, {1, 2, 3}),
                ("xxx", None, "422: Unprocessable Entity:"),  # wrong datetime string
                (None, "xxx", "422: Unprocessable Entity:"),  # wrong datetime string
                ("", None, {1, 2, 3}),  # reserved keyword does not make sense
                (None, "", {1, 2, 3}),  # reserved keyword does not make sense
                ("TS0", None, {1, 2, 3}),
                ("TS1", None, {1, 2}),
                ("TS3", None, set()),
                (None, "TS0", set()),
                (None, "TS1", {3}),
                (None, "TS2", {2, 3}),
                ("TS0", "TS3", {1, 2, 3}),
                ("TS1", "TS3", {1, 2}),
                ("TS1", "TS2", {2}),
                ("TS2", "TS2", set()),
                ("TS2", "TS1", set()),  # ambiguous (after > before) does not cause error
            ],
        )
        def test_search_by_updatedtime(self, after, before, expected):
            fixed_after = self.timestamps.get(after, after)
            fixed_before = self.timestamps.get(before, before)
            search_params = {}
            if fixed_after:
                search_params["updated_after"] = fixed_after
            if fixed_before:
                search_params["updated_before"] = fixed_before
            self.try_search_topics(USER1, self.topics, search_params, expected)

    class ExtCommonForResultSlice_(Common_):
        @staticmethod
        def try_search_topics(user, topics_dict, search_params, expected):
            # expected: ([ordered topics], num_topics, offset, limit, sortkey) or str
            if isinstance(expected, str):
                with pytest.raises(HTTPError, match=expected):
                    search_topics(user, search_params)
                return
            [
                expected_topics,
                expected_num_topics,
                expected_offset,
                expected_limit,
                expected_sort_key,
            ] = expected
            result = search_topics(user, search_params)
            assert result.num_topics == expected_num_topics
            assert result.offset == expected_offset
            assert result.limit == expected_limit
            assert result.sort_key == expected_sort_key
            assert [topic.topic_id for topic in result.topics] == [
                topics_dict[idx].topic_id for idx in expected_topics
            ]

    class TestSearchResultSlice(ExtCommonForResultSlice_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_result_slice(self):
            self.topic1 = self.create_minimal_topic(USER1, {"threat_impact": 1})
            self.topic2 = self.create_minimal_topic(USER1, {"threat_impact": 2})
            self.topic3 = self.create_minimal_topic(USER1, {"threat_impact": 3})
            self.topic4 = self.create_minimal_topic(USER1, {"threat_impact": 4})
            self.topic5 = self.create_minimal_topic(USER1, {"threat_impact": 1})
            self.topic6 = self.create_minimal_topic(USER1, {"threat_impact": 2})
            self.topic7 = self.create_minimal_topic(USER1, {"threat_impact": 3})
            update_topic(USER1, self.topic5, {"threat_impact": 2})
            update_topic(USER1, self.topic2, {"threat_impact": 1})
            update_topic(USER1, self.topic6, {"threat_impact": 3})
            self.topics = {
                1: self.topic1,
                2: self.topic2,
                3: self.topic3,
                4: self.topic4,
                5: self.topic5,
                6: self.topic6,
                7: self.topic7,
            }
            # Memo:
            # created asc order: [1, 2, 3, 4, 5, 6, 7]
            # updated asc order: [1, 3, 4, 7, 5, 2, 6]
            # threat impact: {1: (1, 2), 2: (5), 3: (3, 6, 7), 4: (4)}

        @pytest.mark.parametrize(
            "search_params, expected",
            # search_params: (offset, limit, sort_key)
            # expected: ([ordered topics], num_topics, offset, limit, sortkey) or str of exception
            [
                # sort_key
                (
                    (None, None, None),  # check defaults
                    ([2, 1, 5, 6, 7, 3, 4], 7, 0, 10, "threat_impact"),
                ),
                ((None, None, "my_sort_key"), "422: Unprocessable Entity: "),
                (
                    (None, None, "threat_impact"),  # implicit 2nd key is updated_at_desc
                    ([2, 1, 5, 6, 7, 3, 4], 7, 0, 10, "threat_impact"),
                ),
                (
                    (None, None, "threat_impact_desc"),  # implicit 2nd key is updated_at_desc
                    ([4, 6, 7, 3, 5, 2, 1], 7, 0, 10, "threat_impact_desc"),
                ),
                (
                    (None, None, "updated_at"),  # implicit 2nd key is threat_impact
                    ([1, 3, 4, 7, 5, 2, 6], 7, 0, 10, "updated_at"),
                ),
                (
                    (None, None, "updated_at_desc"),  # implicit 2nd key is threat_impact
                    ([6, 2, 5, 7, 4, 3, 1], 7, 0, 10, "updated_at_desc"),
                ),
                # offset
                (
                    (0, None, None),
                    ([2, 1, 5, 6, 7, 3, 4], 7, 0, 10, "threat_impact"),
                ),
                (("x", None, None), "422: Unprocessable Entity: "),
                ((-1, None, None), "422: Unprocessable Entity: "),  # offset should be >=0
                (
                    (5, None, None),
                    ([3, 4], 7, 5, 10, "threat_impact"),
                ),
                (
                    (10, None, None),
                    ([], 7, 10, 10, "threat_impact"),
                ),
                # limit
                (
                    (None, 10, None),
                    ([2, 1, 5, 6, 7, 3, 4], 7, 0, 10, "threat_impact"),
                ),
                ((None, "x", None), "422: Unprocessable Entity: "),
                ((None, 0, None), "422: Unprocessable Entity: "),  # limit should be >= 1
                ((None, 101, None), "422: Unprocessable Entity: "),  # limit should be <= 100
                (
                    (None, 5, None),
                    ([2, 1, 5, 6, 7], 7, 0, 5, "threat_impact"),
                ),
                # complex
                (
                    (2, 3, "updated_at_desc"),
                    ([5, 7, 4], 7, 2, 3, "updated_at_desc"),
                ),
            ],
        )
        def test_search_result_slice(self, search_params, expected):
            [offset, limit, sort_key] = search_params
            fixed_search_params = {
                **({} if offset is None else {"offset": offset}),
                **({} if limit is None else {"limit": limit}),
                **({} if sort_key is None else {"sort_key": sort_key}),
            }
            self.try_search_topics(USER1, self.topics, fixed_search_params, expected)
