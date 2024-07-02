from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import PTEAM1, TOPIC1, USER1
from app.tests.medium.utils import (
    create_service_topicstatus,
    create_topic_with_versioned_actions,
    headers,
)

client = TestClient(app)


@pytest.mark.parametrize(
    "topic_status, solved_num, unsolved_num",
    [
        (models.TopicStatusType.completed, 1, 0),
    ],
)
def test_it_should_return_solved_number_based_on_ticket_status(
    testdb, topic_status, solved_num, unsolved_num
):

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["solved"]["topic_ticket_ids"]) == solved_num
    assert (
        ticket_response["ticket_id"] in response["solved"]["topic_ticket_ids"][0]["ticket_ids"][0]
    )
    assert response["solved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["unsolved"]["topic_ticket_ids"]) == unsolved_num


@pytest.mark.parametrize(
    "topic_status, solved_num, unsolved_num",
    [
        (models.TopicStatusType.acknowledged, 0, 1),
        (models.TopicStatusType.scheduled, 0, 1),
    ],
)
def test_it_should_return_unsolved_number_based_on_ticket_status(
    testdb, topic_status, solved_num, unsolved_num
):

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["solved"]["topic_ticket_ids"]) == solved_num

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["unsolved"]["topic_ticket_ids"]) == unsolved_num
    assert (
        ticket_response["ticket_id"] in response["unsolved"]["topic_ticket_ids"][0]["ticket_ids"][0]
    )
    assert response["unsolved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]


@pytest.mark.parametrize(
    "threat_impact, topic_status, solved_threat_impact_count, unsolved_threat_impact_count",
    [
        (
            1,
            models.TopicStatusType.completed,
            {"1": 1, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            2,
            models.TopicStatusType.completed,
            {"1": 0, "2": 1, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            3,
            models.TopicStatusType.completed,
            {"1": 0, "2": 0, "3": 1, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            4,
            models.TopicStatusType.completed,
            {"1": 0, "2": 0, "3": 0, "4": 1},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            1,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 1, "2": 0, "3": 0, "4": 0},
        ),
        (
            2,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 1, "3": 0, "4": 0},
        ),
        (
            3,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 1, "4": 0},
        ),
        (
            4,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 1},
        ),
    ],
)
def test_it_shoud_return_threat_impact_count_num_based_on_tickte_status(
    testdb, threat_impact, topic_status, solved_threat_impact_count, unsolved_threat_impact_count
):
    topic = {
        **TOPIC1,
        "threat_impact": threat_impact,
    }

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert response["solved"]["threat_impact_count"] == solved_threat_impact_count

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert response["unsolved"]["threat_impact_count"] == unsolved_threat_impact_count


@pytest.mark.parametrize(
    "_topic1, _topic2, _topic3, _topic4, sorted_titles",
    [
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 2, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 4, "title": "topic four"},
            ["topic one", "topic two", "topic three", "topic four"],
        ),
        (
            {"threat_impact": 4, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 2, "title": "topic three"},
            {"threat_impact": 1, "title": "topic four"},
            ["topic four", "topic three", "topic two", "topic one"],
        ),
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 2, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic one", "topic two", "topic four", "topic three"],
        ),
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic one", "topic four", "topic three", "topic two"],
        ),
        (
            {"threat_impact": 3, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic four", "topic three", "topic two", "topic one"],
        ),
    ],
)
def test_it_shoud_return_solved_sorted_title_based_on_threat_impact(
    testdb, _topic1, _topic2, _topic3, _topic4, sorted_titles
):
    topic1 = {
        **TOPIC1,
        "title": _topic1["title"],
        "threat_impact": _topic1["threat_impact"],
    }
    ticket_response1 = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic1)

    topic2 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic2["title"],
        "threat_impact": _topic2["threat_impact"],
    }
    topic3 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic3["title"],
        "threat_impact": _topic3["threat_impact"],
    }
    topic4 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic4["title"],
        "threat_impact": _topic4["threat_impact"],
    }
    topic_response2 = create_topic_with_versioned_actions(
        USER1, topic2, [[ticket_response1["tag_name"]]]
    )
    topic_response3 = create_topic_with_versioned_actions(
        USER1, topic3, [[ticket_response1["tag_name"]]]
    )
    topic_response4 = create_topic_with_versioned_actions(
        USER1, topic4, [[ticket_response1["tag_name"]]]
    )

    json_data = {
        "topic_status": models.TopicStatusType.completed,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        ticket_response1["topic_id"],
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response2.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response3.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response4.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response1['pteam_id']}/services/{ticket_response1['service_id']}/tags/{ticket_response1['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response_json = response.json()

    # solved
    assert response_json["solved"]["pteam_id"] == ticket_response1["pteam_id"]
    assert response_json["solved"]["service_id"] == ticket_response1["service_id"]
    assert response_json["solved"]["tag_id"] == ticket_response1["tag_id"]
    topic_title_list = []
    for topic_ticket_id in response_json["solved"]["topic_ticket_ids"]:
        response_topic = client.get(
            f"/topics/{topic_ticket_id['topic_id']}",
            headers=headers(USER1),
        )
        topic = response_topic.json()
        topic_title_list.append(topic["title"])

    assert topic_title_list == sorted_titles

    # unsolved
    assert response_json["unsolved"]["pteam_id"] == ticket_response1["pteam_id"]
    assert response_json["unsolved"]["service_id"] == ticket_response1["service_id"]
    assert response_json["unsolved"]["tag_id"] == ticket_response1["tag_id"]
    assert len(response_json["unsolved"]["topic_ticket_ids"]) == 0


@pytest.mark.parametrize(
    "_topic1, _topic2, _topic3, _topic4, sorted_titles",
    [
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 2, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 4, "title": "topic four"},
            ["topic one", "topic two", "topic three", "topic four"],
        ),
        (
            {"threat_impact": 4, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 2, "title": "topic three"},
            {"threat_impact": 1, "title": "topic four"},
            ["topic four", "topic three", "topic two", "topic one"],
        ),
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 2, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic one", "topic two", "topic four", "topic three"],
        ),
        (
            {"threat_impact": 1, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic one", "topic four", "topic three", "topic two"],
        ),
        (
            {"threat_impact": 3, "title": "topic one"},
            {"threat_impact": 3, "title": "topic two"},
            {"threat_impact": 3, "title": "topic three"},
            {"threat_impact": 3, "title": "topic four"},
            ["topic four", "topic three", "topic two", "topic one"],
        ),
    ],
)
def test_it_shoud_return_unsolved_sorted_title_based_on_threat_impact(
    testdb, _topic1, _topic2, _topic3, _topic4, sorted_titles
):
    topic1 = {
        **TOPIC1,
        "title": _topic1["title"],
        "threat_impact": _topic1["threat_impact"],
    }
    ticket_response1 = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic1)

    topic2 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic2["title"],
        "threat_impact": _topic2["threat_impact"],
    }
    topic3 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic3["title"],
        "threat_impact": _topic3["threat_impact"],
    }
    topic4 = {
        **TOPIC1,
        "topic_id": uuid4(),
        "tag_name": ticket_response1["tag_name"],
        "title": _topic4["title"],
        "threat_impact": _topic4["threat_impact"],
    }
    topic_response2 = create_topic_with_versioned_actions(
        USER1, topic2, [[ticket_response1["tag_name"]]]
    )
    topic_response3 = create_topic_with_versioned_actions(
        USER1, topic3, [[ticket_response1["tag_name"]]]
    )
    topic_response4 = create_topic_with_versioned_actions(
        USER1, topic4, [[ticket_response1["tag_name"]]]
    )

    json_data = {
        "topic_status": models.TopicStatusType.acknowledged,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        ticket_response1["topic_id"],
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response2.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response3.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )
    create_service_topicstatus(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        topic_response4.topic_id,
        ticket_response1["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response1['pteam_id']}/services/{ticket_response1['service_id']}/tags/{ticket_response1['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response_json = response.json()

    # solved
    assert response_json["solved"]["pteam_id"] == ticket_response1["pteam_id"]
    assert response_json["solved"]["service_id"] == ticket_response1["service_id"]
    assert response_json["solved"]["tag_id"] == ticket_response1["tag_id"]
    assert len(response_json["solved"]["topic_ticket_ids"]) == 0

    # unsolved
    assert response_json["unsolved"]["pteam_id"] == ticket_response1["pteam_id"]
    assert response_json["unsolved"]["service_id"] == ticket_response1["service_id"]
    assert response_json["unsolved"]["tag_id"] == ticket_response1["tag_id"]
    topic_title_list = []
    for topic_ticket_id in response_json["unsolved"]["topic_ticket_ids"]:
        response_topic = client.get(
            f"/topics/{topic_ticket_id['topic_id']}",
            headers=headers(USER1),
        )
        topic = response_topic.json()
        topic_title_list.append(topic["title"])

    assert topic_title_list == sorted_titles
