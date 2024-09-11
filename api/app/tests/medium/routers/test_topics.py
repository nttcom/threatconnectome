from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import (
    DEFAULT_ALERT_SSVC_PRIORITY,
)
from app.main import app
from app.models import (
    AutomatableEnum,
    ExploitationEnum,
)
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ACTION3,
    ATEAM1,
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
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_watching_request,
    assert_200,
    assert_204,
    create_ateam,
    create_misp_tag,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    create_watching_request,
    file_upload_headers,
    get_service_by_service_name,
    headers,
    random_string,
    search_topics,
    update_topic,
    upload_pteam_tags,
)

client = TestClient(app)


def test_create_topic():
    user1 = create_user(USER1)
    topic1 = create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
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
    assert topic1.exploitation == TOPIC1["exploitation"]
    assert topic1.automatable == TOPIC1["automatable"]


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


def test_create_wrong_threat_level_topic():
    create_user(USER1)
    _topic = TOPIC1.copy()
    _topic["threat_impact"] = -1
    with pytest.raises(HTTPError, match="422: Unprocessable Entity"):
        create_topic(USER1, _topic)


def test_it_should_return_422_when_use_try_to_create_wrong_exploitation_topic():
    create_user(USER1)
    create_tag(USER1, TAG1)
    _topic = TOPIC1.copy()
    _topic["exploitation"] = "test"

    request = {**_topic}
    del request["topic_id"]

    response = client.post(f'/topics/{_topic["topic_id"]}', headers=headers(USER1), json=request)
    assert response.status_code == 422


def test_default_value_is_set_when_ssvc_related_value_is_empty_in_creation():
    create_user(USER1)
    create_tag(USER1, TAG1)
    _topic = TOPIC1.copy()
    del _topic["exploitation"]
    del _topic["automatable"]

    request = {**_topic}
    del request["topic_id"]

    response = client.post(f'/topics/{_topic["topic_id"]}', headers=headers(USER1), json=request)
    assert response.status_code == 200

    responsed_topic = schemas.TopicCreateResponse(**response.json())
    assert responsed_topic.exploitation == ExploitationEnum.ACTIVE
    assert responsed_topic.automatable == AutomatableEnum.YES


def test_create_too_long_action():
    create_user(USER1)
    _action = ACTION1.copy()
    _action["action"] = random_string(1025)
    with pytest.raises(HTTPError, match="422: Unprocessable Entity"):
        create_topic(USER1, TOPIC1, actions=[_action])


def test_get_topic():
    user1 = create_user(USER1)
    create_pteam(USER1, PTEAM1)
    topic1 = create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
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
    assert responsed_topic.exploitation == TOPIC1["exploitation"]
    assert responsed_topic.automatable == TOPIC1["automatable"]
    # actions are removed from TopicResponse.
    # use 'GET /topics/{tid}/actions/pteam/{pid}' to get actions.


def test_get_all_topics():
    create_user(USER1)
    create_user(USER2)
    create_pteam(USER1, PTEAM1)

    topic1 = create_topic(USER1, {**TOPIC1, "threat_impact": 1}, actions=[ACTION1, ACTION2])
    topic2 = create_topic(USER1, {**TOPIC2, "threat_impact": 2}, actions=[ACTION3])
    topic3 = create_topic(USER1, {**TOPIC3, "threat_impact": 3})
    topic4 = create_topic(USER1, {**TOPIC4, "threat_impact": 2})
    topic5 = create_topic(USER2, {**TOPIC1, "threat_impact": 1, "topic_id": str(uuid4())})

    data = assert_200(client.get("/topics", headers=headers(USER1)))
    assert len(data) == 5
    # sorted orders are [threat_impact, updated_at(desc)]
    assert data[0]["topic_id"] == str(topic5.topic_id)
    assert data[1]["topic_id"] == str(topic1.topic_id)
    assert data[2]["topic_id"] == str(topic4.topic_id)
    assert data[3]["topic_id"] == str(topic2.topic_id)
    assert data[4]["topic_id"] == str(topic3.topic_id)


def test_update_topic():
    create_user(USER1)
    create_pteam(USER1, PTEAM1)
    tag1 = create_tag(USER1, "omega")
    create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1],
    )
    request = {
        "title": "topic one dash",
        "abstract": "abstract one dash",
        "threat_impact": 2,
        "tags": [tag1.tag_name],
        "misp_tags": ["tlp:white"],
        "exploitation": "public_poc",
        "automatable": "no",
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
    assert responsed_topic.exploitation == request["exploitation"]
    assert responsed_topic.exploitation != TOPIC1["exploitation"]
    assert responsed_topic.automatable == request["automatable"]
    assert responsed_topic.automatable != TOPIC1["automatable"]


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


def test_update_topic_not_creater():
    create_user(USER1)
    create_user(USER2)
    create_topic(USER1, TOPIC1, actions=[ACTION1])
    request = {}

    with pytest.raises(HTTPError, match=r"403: Forbidden: you are not topic creator"):
        assert_204(
            client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER2), json=request)
        )


class TestUpdateTopic:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
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

        self.user1 = create_user(USER1)
        self.pteam0 = create_pteam(USER1, _gen_pteam_params(0))
        self.tag1 = create_tag(USER1, TAG1)
        test_service = "test_service"
        test_target = "test target"
        test_version = "1.2.3"
        refs0 = {self.tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, self.pteam0.pteam_id, test_service, refs0)
        self.service_id = get_service_by_service_name(USER1, self.pteam0.pteam_id, test_service)[
            "service_id"
        ]
        self.topic = create_topic(USER1, _gen_topic_params([self.tag1]))

    def test_alert_by_mail_if_vulnerabilities_are_found_when_updating_topic(self, mocker, testdb):
        ## ssvc_deployer_priority is immediate
        request = {
            "exploitation": ExploitationEnum.ACTIVE.value,
            "automatable": AutomatableEnum.NO.value,
        }

        send_alert_to_pteam = mocker.patch("app.routers.topics.send_alert_to_pteam")
        response = client.put(
            f"/topics/{self.topic.topic_id}",
            headers=headers(USER1),
            json=request,
        )
        assert response.status_code == 200

        ## get ticket_id
        response_ticket = client.get(
            f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id}/topics/{self.topic.topic_id}/tags/{self.tag1.tag_id}/tickets",
            headers=headers(USER1),
        )
        ticket_id = response_ticket.json()[0]["ticket_id"]

        alerts = testdb.scalars(
            select(models.Alert).where(models.Alert.ticket_id == str(ticket_id))
        ).all()

        assert alerts

        if alerts[0].alerted_at > alerts[1].alerted_at:
            alert = alerts[0]
        else:
            alert = alerts[1]

        assert alert.ticket.threat.topic_id == str(self.topic.topic_id)

        send_alert_to_pteam.assert_called_once()
        send_alert_to_pteam.assert_called_with(alert)

    def test_not_alert_when_ssvc_deployer_priority_is_lower_than_alert_ssvc_priority_in_pteam(
        self, mocker
    ):
        ## ssvc_deployer_priority is out_of_cycle
        request = {
            "exploitation": ExploitationEnum.PUBLIC_POC.value,
            "automatable": AutomatableEnum.YES.value,
        }

        send_alert_to_pteam = mocker.patch("app.routers.topics.send_alert_to_pteam")
        response = client.put(
            f"/topics/{self.topic.topic_id}",
            headers=headers(USER1),
            json=request,
        )
        assert response.status_code == 200
        send_alert_to_pteam.assert_not_called()

    def test_alert_once_when_ticket_is_created_by_topic_update(self, mocker):
        # delete ticket by different tag
        tag2 = create_tag(USER1, TAG2)
        request1 = {
            "tags": [tag2.tag_name],
        }

        client.put(
            f"/topics/{self.topic.topic_id}",
            headers=headers(USER1),
            json=request1,
        )

        # create ticket by matching tag
        request2 = {
            "exploitation": ExploitationEnum.ACTIVE.value,
            "automatable": AutomatableEnum.YES.value,
            "tags": [self.tag1.tag_name],
        }

        send_alert_to_pteam_in_common = mocker.patch("app.common.send_alert_to_pteam")
        send_alert_to_pteam_in_topics = mocker.patch("app.routers.topics.send_alert_to_pteam")
        response = client.put(
            f"/topics/{self.topic.topic_id}",
            headers=headers(USER1),
            json=request2,
        )
        assert response.status_code == 200
        # alert once
        send_alert_to_pteam_in_common.assert_called_once()
        send_alert_to_pteam_in_topics.assert_not_called()


def test_delete_topic(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    now = datetime.now()

    # create service
    service_name = "service_x"
    service_id = str(uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service_id, pteam_id=pteam1.pteam_id, service_name=service_name
        )
    )

    tag_id = "da54de37-308e-40a7-a5ba-aab594796992"
    # create tag
    testdb.execute(
        insert(models.Tag).values(
            tag_id=tag_id,
            tag_name="",
        )
    )

    # create dependency
    dependency1_id = "dependency1_id"
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency1_id,
            service_id=service_id,
            tag_id=tag_id,
            version="",
            target="1",
            dependency_mission_impact=models.MissionImpactEnum.MISSION_FAILURE,
        )
    )
    # create threat
    threat1_id = "threat1_id"
    testdb.execute(
        insert(models.Threat).values(
            threat_id=threat1_id,
            dependency_id=dependency1_id,
            topic_id=topic1.topic_id,
        )
    )
    # create ticket
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    testdb.execute(
        insert(models.Ticket).values(
            ticket_id=ticket1_id,
            threat_id=threat1_id,
            created_at="2033-06-26 15:00:00",
            ssvc_deployer_priority=models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        )
    )

    request = {
        "action_id": str(topic1.actions[0].action_id),
        "topic_id": str(topic1.topic_id),
        "user_id": str(user1.user_id),
        "pteam_id": str(pteam1.pteam_id),
        "service_id": str(service_id),
        "ticket_id": ticket1_id,
        "executed_at": str(now) if now else None,
    }

    client.post("/actionlogs", headers=headers(USER1), json=request)

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


def test_get_pteam_topic_actions():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)  # TAG1
    create_topic(USER1, TOPIC2, actions=[ACTION1, ACTION2, ACTION3])  # noise
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2, ACTION3])

    def _find_action(resp_: dict, action_: dict) -> dict:
        return next(filter(lambda x: x["action"] == action_["action"], resp_["actions"]), {})

    data = assert_200(
        client.get(
            f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 3
    assert _find_action(data, ACTION1)
    assert _find_action(data, ACTION2)
    assert _find_action(data, ACTION3)

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
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)

    # wrong topic_id
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.get(
                f"/topics/{pteam1.pteam_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
            )
        )

    # user2 not a member of pteam1
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(
            client.get(
                f"/topics/{topic1.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER2)
            )
        )

    # wrong pteam_id
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

    def _gen_topic(tags: list[str], actions: list[dict]) -> dict:
        return {
            **TOPIC1,
            "topic_id": str(uuid4()),
            "tags": tags,
            "actions": actions,
        }

    def _gen_action(tags: list[str]) -> dict:
        return {
            "action_id": None,
            "action": "action " + str(uuid4()),
            "action_type": "elimination",
            "recommended": True,
            "ext": {
                "tags": tags,
                "vulnerable_versions": {},
            },
        }

    def _pick_action(topic: dict, action: dict) -> dict:
        return next(filter(lambda x: x["action"] == action["action"], topic["actions"]), {})

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
            elif alpha[key] != bravo[key]:
                return False
        return True

    # ordinary topic and actions
    action1 = _gen_action([])
    action2 = _gen_action([child11.tag_name])
    action3 = _gen_action([parent1.tag_name])
    topic1 = _gen_topic([parent1.tag_name], [action1, action2, action3])
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
    action4 = _gen_action([child21.tag_name])
    topic2 = _gen_topic([parent1.tag_name], [action4])
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        data = assert_200(
            client.post(f"/topics/{topic2['topic_id']}", headers=headers(USER1), json=topic2)
        )


def test_create_topic_actions__with_action_id():
    create_user(USER1)
    parent1 = create_tag(USER1, "alpha:alpha:")
    child11 = create_tag(USER1, "alpha:alpha:alpha1")

    def _gen_action(action_id: UUID | None) -> dict:
        return {
            "action_id": str(action_id) if action_id else None,
            "action": f"action for {action_id}",
            "action_type": "elimination",
            "recommended": True,
            "ext": {"tags": [child11.tag_name]},
        }

    def _gen_topic(tags: list[str], actions: list[dict]) -> dict:
        return {
            **TOPIC1,
            "topic_id": str(uuid4()),
            "tags": tags,
            "actions": actions,
        }

    def _pick_action(topic: dict, action_id: UUID) -> dict:
        return next(filter(lambda x: x["action_id"] == str(action_id), topic["actions"]), {})

    def _cmp_actions(alpha: dict, bravo: dict) -> bool:
        for key in alpha.keys():
            if key == "topic_id":
                if (t_a := alpha.get(key)) and (t_b := bravo.get(key)) and t_a != t_b:
                    return False
                # ignore missing topic_id
            elif key == "created_by" or key == "created_at":
                continue
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

        @staticmethod
        def create_minimal_topic(user: dict, params: dict) -> schemas.TopicCreateResponse:
            minimal_topic = {
                "topic_id": uuid4(),
                "title": "",
                "abstract": "",
                "threat_impact": 1,
                **params,
                "exploitation": "active",
                "automatable": "yes",
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
            return result

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
                ([0], set()),  # wrong params are just ignored
                ([1], {1}),
                ([2], {2}),
                ([3], {3}),
                ([4], {4}),
                ([5], set()),  # wrong params are just ignored
                (["xxx"], "422: Unprocessable Entity:"),  # not integer
                ([1, 2], {1, 2}),
                ([""], "422: Unprocessable Entity:"),  # reserved keyword does not make sense
                ([1, 5], {1}),  # wrong params are just ignored
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
                (["one"], {1}),
                (["topic"], {1, 2, 3, 4}),  # case-insensitive
                ([" t"], {2, 3}),  # spaces also considered
                (["xxx"], set()),
                ([""], {5}),  # "" is the reserved keyword means empty
                (["", "w"], {2, 5}),
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
                (["one"], {1}),
                (["abstract"], {1, 2, 3, 4}),  # case-insensitive
                ([" t"], {2, 3}),  # spaces also considered
                (["xxx"], set()),
                ([""], {5}),  # "" is the reserved keyword means empty
                (["", "w"], {2, 5}),
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
                ([TAG1], {1, 3}),
                ([TAG2], {2, 3}),
                ([TAG3], set()),  # unused tag
                (["xxx"], set()),  # not existed tag
                ([""], {4}),  # "" is the reserved keyword means empty
                (["", TAG1], {1, 3, 4}),
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
                ([MISPTAG1], {1, 3}),
                ([MISPTAG2], {2, 3}),
                ([MISPTAG3], set()),  # unused misp_tag
                (["xxx"], set()),  # not existed misp_tag
                ([""], {4}),  # "" is the reserved keyword means empty
                (["", MISPTAG1], {1, 3, 4}),
            ],
        )
        def test_search_by_misp_tag(self, search_words, expected):
            search_params = {} if search_words is None else {"misp_tag_names": search_words}
            self.try_search_topics(USER1, self.topics, search_params, expected)

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
            self.topic_ids = {
                "TOPIC1": self.topic1.topic_id,
                "TOPIC2": self.topic2.topic_id,
                "TOPIC3": self.topic3.topic_id,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3}),
                (["TOPIC1"], {1}),
                (["TOPIC1", "TOPIC2"], {1, 2}),
                (["xxx"], set()),  # wrong uuid
                ([str(uuid4())], set()),  # uuid4 but not a valid topic_id
                ([""], set()),  # reserved keyword for empty does not make sense
                (["", "TOPIC1"], {1}),
            ],
        )
        def test_search_by_topic_id(self, search_words, expected):
            search_params = (
                {}
                if search_words is None
                else {
                    "topic_ids": [
                        self.topic_ids.get(search_word, search_word) for search_word in search_words
                    ]
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
            self.creator_ids = {
                "USER1": self.user1.user_id,
                "USER2": self.user2.user_id,
                "USER3": self.user3.user_id,
            }

        @pytest.mark.parametrize(
            "search_words, expected",
            [
                (None, {1, 2, 3}),
                (["USER1"], {1}),
                (["USER1", "USER2"], {1, 2}),
                (["xxx"], set()),  # wrong uuid
                ([str(uuid4())], set()),  # uuid4 but not a valid user_id
                ([""], set()),  # reserved keyword for empty does not make sense
                (["", "USER1"], {1}),
            ],
        )
        def test_search_by_creator(self, search_words, expected):
            search_params = (
                {}
                if search_words is None
                else {
                    "creator_ids": [
                        self.creator_ids.get(search_word, search_word)
                        for search_word in search_words
                    ]
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

    class TestSearchByPteamId(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_pteam_id(self):
            self.pteam1 = create_pteam(USER1, PTEAM1)

            params = {"service": "threatconnectome", "force_mode": True}
            sbom_file = (
                Path(__file__).resolve().parent.parent.parent
                / "requests"
                / "upload_test"
                / "tag.jsonl"
            )
            with open(sbom_file, "rb") as tags:
                response_upload_sbom_file = client.post(
                    f"/pteams/{self.pteam1.pteam_id}/upload_tags_file",
                    headers=file_upload_headers(USER1),
                    params=params,
                    files={"file": tags},
                )
            assert response_upload_sbom_file.status_code == 200
            self.result = response_upload_sbom_file.json()

            # topic registration without pteam
            topic1 = self.create_minimal_topic(USER1, {"tags": [TAG1]})
            topic2 = self.create_minimal_topic(USER1, {"tags": [TAG2]})
            topic3 = self.create_minimal_topic(USER1, {"tags": [TAG3]})
            self.topics_not_pteam = {
                1: topic1,
                2: topic2,
                3: topic3,
            }

        @pytest.mark.parametrize(
            "topic_registration_num, expected",
            [
                (1, {1}),
                (2, {1, 2}),
            ],
        )
        def test_search_by_pteam_id(self, topic_registration_num, expected):
            # topic registration with pteam
            topics = {}
            for idx in range(topic_registration_num):
                params = {"tags": [self.result[idx]["tag_name"]]}
                topics[idx + 1] = self.create_minimal_topic(USER1, params)

            search_params = {
                "pteam_id": self.pteam1.pteam_id,
            }

            result_search_topics = self.try_search_topics(USER1, topics, search_params, expected)
            assert result_search_topics.num_topics == len(expected)

        @pytest.mark.parametrize(
            "topic_registration_num, expected",
            [
                (1, {1, 2, 3, 4}),
                (2, {1, 2, 3, 4, 5}),
            ],
        )
        def test_search_by_not_pteam_id(self, topic_registration_num, expected):
            # topic registration with pteam
            topics = {}
            for idx in range(topic_registration_num):
                params = {"tags": [self.result[idx]["tag_name"]]}
                topics[idx + 4] = self.create_minimal_topic(USER1, params)

            topics = {**self.topics_not_pteam, **topics}

            # not pteam_id
            search_params = {}

            result_search_topics = self.try_search_topics(USER1, topics, search_params, expected)
            assert result_search_topics.num_topics == len(expected)

    class TestSearchByAteamId(Common_):
        @pytest.fixture(scope="function", autouse=True)
        def setup_for_ateam_id(self):
            pteam1 = create_pteam(USER1, PTEAM1)
            pteam2 = create_pteam(USER1, PTEAM2)
            self.ateam1 = create_ateam(USER1, ATEAM1)
            watching_request1 = create_watching_request(USER1, self.ateam1.ateam_id)
            watching_request2 = create_watching_request(USER1, self.ateam1.ateam_id)
            request1 = {
                "request_id": str(watching_request1.request_id),
                "pteam_id": str(pteam1.pteam_id),
            }
            request2 = {
                "request_id": str(watching_request2.request_id),
                "pteam_id": str(pteam2.pteam_id),
            }

            data1 = client.post(
                "/ateams/apply_watching_request", headers=headers(USER1), json=request1
            )
            data2 = client.post(
                "/ateams/apply_watching_request", headers=headers(USER1), json=request2
            )
            assert data1.status_code == 200
            assert data2.status_code == 200

            # register tag with pteam1
            params = {"service": "threatconnectome", "force_mode": True}
            sbom_file = (
                Path(__file__).resolve().parent.parent.parent
                / "requests"
                / "upload_test"
                / "tag.jsonl"
            )
            with open(sbom_file, "rb") as tags:
                response_upload_sbom_file_pteam1 = client.post(
                    f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                    headers=file_upload_headers(USER1),
                    params=params,
                    files={"file": tags},
                )
            assert response_upload_sbom_file_pteam1.status_code == 200
            self.result_pteam1 = response_upload_sbom_file_pteam1.json()

            # register tag with pteam2
            params = {"service": "threatconnectome", "force_mode": True}
            sbom_file = (
                Path(__file__).resolve().parent.parent.parent
                / "requests"
                / "upload_test"
                / "tag2.jsonl"
            )
            with open(sbom_file, "rb") as tags:
                response_upload_sbom_file_pteam2 = client.post(
                    f"/pteams/{pteam2.pteam_id}/upload_tags_file",
                    headers=file_upload_headers(USER1),
                    params=params,
                    files={"file": tags},
                )
            assert response_upload_sbom_file_pteam2.status_code == 200
            self.result_pteam2 = response_upload_sbom_file_pteam2.json()

            # topic registration without pteam
            topic1 = self.create_minimal_topic(USER1, {"tags": [TAG1]})
            topic2 = self.create_minimal_topic(USER1, {"tags": [TAG2]})
            topic3 = self.create_minimal_topic(USER1, {"tags": [TAG3]})
            self.topics_not_pteam = {
                1: topic1,
                2: topic2,
                3: topic3,
            }

        @pytest.mark.parametrize(
            "topic_registration_num, expected",
            [
                (1, {1}),
                (2, {1, 2}),
            ],
        )
        def test_search_by_ateam_id_with_one_pteam(self, topic_registration_num, expected):
            # topic registration with pteam
            topics = {}
            for idx in range(topic_registration_num):
                params = {"tags": [self.result_pteam1[idx]["tag_name"]]}
                topics[idx + 1] = self.create_minimal_topic(USER1, params)

            search_params = {
                "ateam_id": self.ateam1.ateam_id,
            }

            result_search_topics = self.try_search_topics(USER1, topics, search_params, expected)
            assert result_search_topics.num_topics == len(expected)

        @pytest.mark.parametrize(
            "topic_registration_num, expected",
            [
                (1, {1, 2}),
                (2, {1, 2, 3, 4}),
            ],
        )
        def test_search_by_ateam_id_with_two_pteam(self, topic_registration_num, expected):
            # topic registration with pteam
            topics_list = []
            for idx in range(topic_registration_num):
                params_pteam1 = {"tags": [self.result_pteam1[idx]["tag_name"]]}
                params_pteam2 = {"tags": [self.result_pteam2[idx]["tag_name"]]}
                topics_list.append(self.create_minimal_topic(USER1, params_pteam1))
                topics_list.append(self.create_minimal_topic(USER1, params_pteam2))

            topics_dict = {}
            for idx in range(len(topics_list)):
                topics_dict[idx + 1] = topics_list[idx]

            search_params = {
                "ateam_id": self.ateam1.ateam_id,
            }

            result_search_topics = self.try_search_topics(
                USER1, topics_dict, search_params, expected
            )
            assert result_search_topics.num_topics == len(expected)

        @pytest.mark.parametrize(
            "topic_registration_num, expected",
            [
                (1, {1, 2, 3, 4}),
                (2, {1, 2, 3, 4, 5}),
            ],
        )
        def test_search_by_not_ateam_id(self, topic_registration_num, expected):
            # topic registration with pteam
            topics = {}
            for idx in range(topic_registration_num):
                params = {"tags": [self.result_pteam1[idx]["tag_name"]]}
                topics[idx + 4] = self.create_minimal_topic(USER1, params)

            topics = {**self.topics_not_pteam, **topics}
            search_params = {}

            result_search_topics = self.try_search_topics(USER1, topics, search_params, expected)
            assert result_search_topics.num_topics == len(expected)

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
                (("xxx", None, None), "422: Unprocessable Entity: "),
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
                ((None, "xxx", None), "422: Unprocessable Entity: "),
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
