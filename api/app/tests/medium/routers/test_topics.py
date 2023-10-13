import re
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
    GTEAM1,
    GTEAM2,
    MISPTAG1,
    MISPTAG2,
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
    ZONE1,
    ZONE2,
    ZONE3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
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
    invite_to_gteam,
    invite_to_pteam,
    random_string,
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


def test_search_topic():
    create_user(USER1)
    create_pteam(USER1, PTEAM1)  # PTEAM1 has ZONE1
    create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    create_topic(USER1, TOPIC2, actions=[ACTION3])
    params = {
        "title_words": ["one", "zero"],
        "abstract_words": ["one", "abstract", "zero"],
        "threat_impacts": [1, 2],
    }
    response = client.get("/topics/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    responsed_topics = response.json()
    assert len(responsed_topics) == 1
    assert responsed_topics[0]["topic_id"] == str(TOPIC1["topic_id"])
    assert re.search("|".join(params["title_words"]), responsed_topics[0]["title"])


def test_search_topic_by_misptag():
    create_user(USER1)
    misptag1 = create_misp_tag(USER1, MISPTAG1)
    create_topic(USER1, TOPIC1)
    create_topic(USER1, TOPIC2)
    params = {"misp_tag_ids": [misptag1.tag_id]}
    response = client.get("/topics/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    responsed_topics = response.json()
    assert len(responsed_topics) == 1
    assert responsed_topics[0]["topic_id"] == str(TOPIC1["topic_id"])


def test_search_topic_by_tag():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    create_topic(USER1, TOPIC1)
    create_topic(USER1, TOPIC4)
    params = {"tag_ids": [tag1.tag_id]}
    response = client.get("/topics/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    responsed_topics = response.json()
    assert len(responsed_topics) == 1
    assert responsed_topics[0]["topic_id"] == str(TOPIC1["topic_id"])


def test_search_topics__with_zones():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER1, GTEAM2)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER1, gteam2.gteam_id, ZONE2)

    create_topic(USER1, TOPIC1, zone_names=[zone1.zone_name])
    create_topic(USER1, TOPIC2, zone_names=[zone2.zone_name])
    create_topic(USER1, TOPIC3, zone_names=[zone1.zone_name, zone2.zone_name])
    create_topic(USER1, TOPIC4, zone_names=[])

    def _pick_topic(topics_: List[dict], target_: dict) -> dict:
        return next(filter(lambda x: x["title"] == target_["title"], topics_), {})

    # USER1 has zone1 & zone2
    data = assert_200(client.get("/topics/search", headers=headers(USER1)))
    assert len(data) == 4
    assert _pick_topic(data, TOPIC1)
    assert _pick_topic(data, TOPIC2)
    assert _pick_topic(data, TOPIC3)
    assert _pick_topic(data, TOPIC4)

    # USER2 has no zones
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 1
    assert _pick_topic(data, TOPIC4)

    # pteam1 with zone1
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, p_invitation.invitation_id)

    # now USER2 has zone1 via pteam1
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 3
    assert _pick_topic(data, TOPIC1)
    assert _pick_topic(data, TOPIC3)
    assert _pick_topic(data, TOPIC4)

    # remove zone1 from pteam1
    assert_200(
        client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json={"zone_names": []})
    )

    # now USER2 has no zones
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 1
    assert _pick_topic(data, TOPIC4)

    # ateam1 and pteam2 with zone2
    pteam2 = create_pteam(USER1, {**PTEAM2, "zone_names": [zone2.zone_name]})
    ateam1 = create_ateam(USER2, ATEAM1)

    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 1
    assert _pick_topic(data, TOPIC4)

    # ateam1 watch pteam2(zone2)
    watching_request = create_watching_request(USER2, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam2.pteam_id)

    # now USER2 has zone2 via pteam2 via ateam1
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 3
    assert _pick_topic(data, TOPIC2)
    assert _pick_topic(data, TOPIC3)
    assert _pick_topic(data, TOPIC4)

    # ateam1 stop watching pteam2
    assert_204(
        client.delete(
            f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam2.pteam_id}", headers=headers(USER2)
        )
    )

    # now USER2 has no zones
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 1
    assert _pick_topic(data, TOPIC4)

    # USER2 join to gteam1
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)

    # now USER2 has zone1 via gteam1
    data = assert_200(client.get("/topics/search", headers=headers(USER2)))
    assert len(data) == 3
    assert _pick_topic(data, TOPIC1)
    assert _pick_topic(data, TOPIC3)
    assert _pick_topic(data, TOPIC4)


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


def test_get_topic_actions():
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


def test_get_topic_actions__errors():
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
