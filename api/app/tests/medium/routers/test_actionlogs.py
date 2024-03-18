import re
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    GROUP1,
    GROUP2,
    PTEAM1,
    PTEAM2,
    TAG1,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
    USER3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_actionlog,
    create_pteam,
    create_topic,
    create_user,
    headers,
    invite_to_pteam,
    upload_pteam_tags,
)

client = TestClient(app)


def test_create_log():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]
    now = datetime.now()

    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )

    assert actionlog1.logging_id != ZERO_FILLED_UUID
    assert actionlog1.action_id == action1.action_id
    assert actionlog1.topic_id == topic1.topic_id
    assert actionlog1.action == ACTION1["action"]
    assert actionlog1.action_type == ACTION1["action_type"]
    assert actionlog1.recommended == ACTION1["recommended"]
    assert actionlog1.user_id == user1.user_id
    assert actionlog1.pteam_id == pteam1.pteam_id
    assert actionlog1.email == USER1["email"]
    assert actionlog1.executed_at == now
    assert actionlog1.created_at > now


def test_create_log__with_wrong_params():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]
    topic2_data = {**TOPIC2, "tags": ["fake tag"]}
    topic2 = create_topic(USER1, topic2_data, actions=[ACTION1])
    action2 = topic2.actions[0]

    # wrong action
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(USER1, uuid4(), topic1.topic_id, user1.user_id, pteam1.pteam_id, None)
    # wrong topic
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(USER1, action1.action_id, uuid4(), user1.user_id, pteam1.pteam_id, None)
    # wrong user
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(USER1, action1.action_id, topic1.topic_id, uuid4(), pteam1.pteam_id, None)
    # wrong pteam
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(USER1, action1.action_id, topic1.topic_id, user1.user_id, uuid4(), None)
    # called by not pteam member
    with pytest.raises(HTTPError, match="403: Forbidden"):
        create_actionlog(
            USER2, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
        )
    # not pteam member as recipient
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(
            USER1, action1.action_id, topic1.topic_id, user2.user_id, pteam1.pteam_id, None
        )
    # not pteam topic
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(
            USER1, action2.action_id, topic2.topic_id, user1.user_id, pteam1.pteam_id, None
        )
    # action mismatch with topic
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(
            USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
        )

    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
    )
    assert actionlog1.action_id == action1.action_id


def test_get_logs():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, yesterday
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    response = client.get("/actionlogs", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
    assert data[1]["logging_id"] == str(actionlog1.logging_id)


def test_get_logs__members_only():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
    )
    user2 = create_user(USER2)
    pteam2 = create_pteam(USER2, PTEAM2)
    upload_pteam_tags(USER2, pteam2.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    actionlog2 = create_actionlog(
        USER2, action1.action_id, topic1.topic_id, user2.user_id, pteam2.pteam_id, None
    )

    response = client.get("/actionlogs", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog1.logging_id)  # pteam1 only

    response = client.get("/actionlogs", headers=headers(USER2))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # pteam2 only

    create_user(USER3)

    response = client.get("/actionlogs", headers=headers(USER3))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # nothing for pteamless

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)

    response = client.get("/actionlogs", headers=headers(USER3))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog1.logging_id)  # pteam1 only

    invitation = invite_to_pteam(USER2, pteam2.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)

    response = client.get("/actionlogs", headers=headers(USER3))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # both of pteam1 & pteam2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by created_st
    assert data[1]["logging_id"] == str(actionlog1.logging_id)


def test_get_topic_logs():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, yesterday
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    response = client.get(f"/actionlogs/topics/{topic1.topic_id}", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
    assert data[1]["logging_id"] == str(actionlog1.logging_id)


def test_search_logs__filtered_by_topic_ids():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    topic2 = create_topic(USER1, TOPIC2, actions=[ACTION2])
    action1 = topic1.actions[0]
    action2 = topic2.actions[0]
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic2.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    params = {
        "topic_ids": [topic1.topic_id],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog2.logging_id
    assert UUID(data[0]["topic_id"]) in params["topic_ids"]


def test_search_logs__filtered_by_action_words():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    topic2 = create_topic(USER1, TOPIC2, actions=[ACTION2])
    action1 = topic1.actions[0]  # action: "action one"
    action2 = topic2.actions[0]  # action: "action two"
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic2.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    params = {
        "action_words": ["one", "zero"],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog2.logging_id
    assert re.search("|".join(params["action_words"]), data[0]["action"])


def test_search_logs__filtered_by_action_types():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]  # action_type : elimination
    action2 = topic1.actions[1]  # action_type : mitigation
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    params = {
        "action_types": ["elimination", "rejection"],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog2.logging_id
    assert data[0]["action_type"] in params["action_types"]


def test_search_logs__filtered_by_user_ids():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )  # excuted by user1
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user2.user_id, pteam1.pteam_id, now
    )  # excuted by user2
    params = {
        "user_ids": [user1.user_id],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog2.logging_id
    assert UUID(data[0]["user_id"]) in params["user_ids"]


def test_search_logs__filtered_by_pteam_ids():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER2, PTEAM2)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    upload_pteam_tags(USER2, pteam2.pteam_id, GROUP2, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])  # TAG1
    action1 = topic1.actions[0]
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )  # pteam_id: pteam1.pteam_id
    actionlog2 = create_actionlog(
        USER2, action1.action_id, topic1.topic_id, user2.user_id, pteam2.pteam_id, now
    )  # pteam_id: pteam2.pteam_id
    params = {
        "pteam_ids": [pteam1.pteam_id],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog2.logging_id
    assert UUID(data[0]["pteam_id"]) in params["pteam_ids"]


def test_search_logs__filtered_by_executed_at():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog2 = create_actionlog(
        USER1,
        action2.action_id,
        topic1.topic_id,
        user1.user_id,
        pteam1.pteam_id,
        now - timedelta(days=2),
    )
    actionlog3 = create_actionlog(
        USER1,
        action2.action_id,
        topic1.topic_id,
        user1.user_id,
        pteam1.pteam_id,
        now - timedelta(days=4),
    )
    params = {
        "executed_before": str(now - timedelta(days=1)),
        "executed_after": str(now - timedelta(days=3)),
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog2.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog3.logging_id
    assert (
        datetime.fromisoformat(params["executed_after"])
        <= datetime.fromisoformat(data[0]["executed_at"])
        < datetime.fromisoformat(params["executed_before"])
    )


def test_search_logs__filtered_by_created_at(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog2 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    actionlog3 = create_actionlog(
        USER1, action2.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, now
    )
    db_actionlog2 = (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.logging_id == str(actionlog2.logging_id))
        .one()
    )
    db_actionlog2.created_at = now - timedelta(days=2)  # overwrite created_at on DB
    testdb.add(db_actionlog2)
    db_actionlog3 = (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.logging_id == str(actionlog3.logging_id))
        .one()
    )
    db_actionlog3.created_at = now - timedelta(days=4)  # overwrite created_at on DB
    testdb.add(db_actionlog2)
    testdb.commit()

    params = {
        "created_before": str(now - timedelta(days=1)),
        "created_after": str(now - timedelta(days=3)),
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert UUID(data[0]["logging_id"]) == actionlog2.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog1.logging_id
    assert UUID(data[0]["logging_id"]) != actionlog3.logging_id
    assert (
        datetime.fromisoformat(params["created_after"])
        <= datetime.fromisoformat(data[0]["created_at"])
        < datetime.fromisoformat(params["created_before"])
    )


def test_search_logs__members_only():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER2, PTEAM2)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    upload_pteam_tags(USER2, pteam2.pteam_id, GROUP2, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
    )
    actionlog2 = create_actionlog(
        USER2, action1.action_id, topic1.topic_id, user2.user_id, pteam2.pteam_id, None
    )

    # filtered with pteams by default
    params = {}
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog1.logging_id)

    # searching out of pteams is forbidden
    params = {
        "pteam_ids": [pteam2.pteam_id],
    }
    response = client.get("/actionlogs/search", headers=headers(USER1), params=params)
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # nothing found for pteam less
    params = {}
    response = client.get("/actionlogs/search", headers=headers(USER3), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

    # be a member of pteam1
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    params = {}
    response = client.get("/actionlogs/search", headers=headers(USER3), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog1.logging_id)

    # be a member of pteam2 (and pteam1)
    invitation = invite_to_pteam(USER2, pteam2.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    params = {}
    response = client.get("/actionlogs/search", headers=headers(USER3), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by executed_at
    assert data[1]["logging_id"] == str(actionlog1.logging_id)

    # filtering by pteam_id
    params = {
        "pteam_ids": [pteam1.pteam_id],
    }
    response = client.get("/actionlogs/search", headers=headers(USER3), params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["logging_id"] == str(actionlog1.logging_id)
