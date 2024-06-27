from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    ACTION1,
    PTEAM1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    create_service_topicstatus,
    headers,
)

client = TestClient(app)


@pytest.mark.parametrize(
    "topic_status, solved_num, unsolved_num",
    [
        (models.TopicStatusType.acknowledged, 0, 1),
        (models.TopicStatusType.scheduled, 0, 1),
        (models.TopicStatusType.completed, 1, 0),
    ],
)
def test_get_service_tagged_ticket_ids_when_change_the_topic_status_type(
    testdb, topic_status, solved_num, unsolved_num
):

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

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

    # create current_ticket_status table
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

    if solved_num == 1:
        assert (
            ticket_response["ticket_id"]
            in response["solved"]["topic_ticket_ids"][0]["ticket_ids"][0]
        )
        assert response["solved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["unsolved"]["topic_ticket_ids"]) == unsolved_num

    if unsolved_num == 1:
        assert (
            ticket_response["ticket_id"]
            in response["unsolved"]["topic_ticket_ids"][0]["ticket_ids"][0]
        )
        assert (
            response["unsolved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]
        )


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
def test_get_service_tagged_ticket_ids_when_change_the_threat_impact(
    testdb, threat_impact, topic_status, solved_threat_impact_count, unsolved_threat_impact_count
):
    topic = {
        **TOPIC1,
        "threat_impact": threat_impact,
    }

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic, ACTION1)

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

    # create current_ticket_status table
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
