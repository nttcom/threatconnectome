from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app import models, persistence
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    PTEAM1,
    PTEAM2,
    SERVICE1,
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
    create_actionlog_with_related_data,
    create_pteam,
    create_topic,
    create_user,
    headers,
    invite_to_pteam,
    upload_pteam_tags,
)

client = TestClient(app)


def test_create_log(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]
    now = datetime.now()

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    actionlogs = create_actionlog_with_related_data(
        user1.user_id,
        USER1,
        topic1,
        action1.action_id,
        pteam1.pteam_id,
        service1.service_id,
        tag_id,
        dependency1_id,
        threat1_id,
        ticket1_id,
        now,
        testdb,
    )

    actionlog1 = actionlogs[0]

    assert actionlog1.logging_id != ZERO_FILLED_UUID
    assert actionlog1.action_id == action1.action_id
    assert actionlog1.topic_id == topic1.topic_id
    assert actionlog1.action == ACTION1["action"]
    assert actionlog1.action_type == ACTION1["action_type"]
    assert actionlog1.recommended == ACTION1["recommended"]
    assert actionlog1.user_id == user1.user_id
    assert actionlog1.pteam_id == pteam1.pteam_id
    assert str(actionlog1.service_id) == service1.service_id
    assert str(actionlog1.ticket_id) == ticket1_id
    assert actionlog1.email == USER1["email"]
    assert actionlog1.executed_at == now
    assert actionlog1.created_at > now


def test_create_log__with_wrong_action(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # wrong action
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog_with_related_data(
            user1.user_id,
            USER1,
            topic1,
            uuid4(),
            pteam1.pteam_id,
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_create_log__with_wrong_topic(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # create dependency
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency1_id,
            service_id=service1.service_id,
            tag_id=tag_id,
            version="",
            target="1",
            dependency_mission_impact=models.MissionImpactEnum.MISSION_FAILURE,
        )
    )
    # create threat
    testdb.execute(
        insert(models.Threat).values(
            threat_id=threat1_id,
            dependency_id=dependency1_id,
            topic_id=topic1.topic_id,
        )
    )
    # create ticket
    testdb.execute(
        insert(models.Ticket).values(
            ticket_id=ticket1_id,
            threat_id=threat1_id,
            created_at="2033-06-26 15:00:00",
            updated_at="2033-06-26 15:00:00",
            ssvc_deployer_priority=models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        )
    )

    # wrong topic
    topic1.topic_id = uuid4()
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog(
            USER1,
            action1.action_id,
            uuid4(),
            user1.user_id,
            pteam1.pteam_id,
            service1.service_id,
            None,
        )


def test_create_log__with_wrong_user(testdb: Session):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # wrong user
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog_with_related_data(
            uuid4(),
            USER1,
            topic1,
            action1.action_id,
            pteam1.pteam_id,
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_create_log__with_wrong_pteam(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # wrong pteam
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog_with_related_data(
            user1.user_id,
            USER1,
            topic1,
            action1.action_id,
            uuid4(),
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_create_log__with_called_by_not_pteam_member(testdb: Session):
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # called by not pteam member
    with pytest.raises(HTTPError, match="403: Forbidden"):
        create_actionlog_with_related_data(
            user1.user_id,
            USER2,
            topic1,
            action1.action_id,
            pteam1.pteam_id,
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_create_log__with_not_pteam_member_as_recipient(testdb: Session):
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # not pteam member as recipient
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog_with_related_data(
            user2.user_id,
            USER1,
            topic1,
            action1.action_id,
            pteam1.pteam_id,
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_create_log__with_action_mismatch_with_topic(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    topic2_data = {**TOPIC2, "tags": ["fake tag"]}
    topic2 = create_topic(USER1, topic2_data, actions=[ACTION1])
    action2 = topic2.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"

    # action mismatch with topic
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_actionlog_with_related_data(
            user1.user_id,
            USER1,
            topic1,
            action2.action_id,
            pteam1.pteam_id,
            service1.service_id,
            tag_id,
            dependency1_id,
            threat1_id,
            ticket1_id,
            None,
            testdb,
        )


def test_get_logs(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    actionlogs1 = create_actionlog_with_related_data(
        user1.user_id,
        USER1,
        topic1,
        action1.action_id,
        pteam1.pteam_id,
        service1.service_id,
        tag_id,
        dependency1_id,
        threat1_id,
        ticket1_id,
        yesterday,
        testdb,
    )
    actionlog1 = actionlogs1[0]

    actionlogs2 = create_actionlog(
        USER1,
        action2.action_id,
        topic1.topic_id,
        user1.user_id,
        pteam1.pteam_id,
        service1.service_id,
        now,
    )
    actionlog2 = actionlogs2[0]

    response = client.get("/actionlogs", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
    assert data[0]["service_id"] == str(service1.service_id)
    assert data[0]["ticket_id"] == str(ticket1_id)
    assert data[1]["logging_id"] == str(actionlog1.logging_id)


def test_get_logs__members_only(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag1_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action1 = topic1.actions[0]

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    actionlogs1 = create_actionlog_with_related_data(
        user1.user_id,
        USER1,
        topic1,
        action1.action_id,
        pteam1.pteam_id,
        service1.service_id,
        tag1_id,
        dependency1_id,
        threat1_id,
        ticket1_id,
        None,
        testdb,
    )
    actionlog1 = actionlogs1[0]

    user2 = create_user(USER2)
    pteam2 = create_pteam(USER2, PTEAM2)
    upload_pteam_tags(USER2, pteam2.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam2_model = persistence.get_pteam_by_id(testdb, pteam2.pteam_id)
    assert pteam2_model is not None
    service2 = pteam2_model.services[0]
    tag2_id = service2.dependencies[0].tag.tag_id

    dependency2_id = "dependency2_id"
    threat2_id = "threat2_id"
    ticket2_id = "4d362f0f-e08e-45a3-9ae9-5a46936372c2"
    actionlogs2 = create_actionlog_with_related_data(
        user2.user_id,
        USER2,
        topic1,
        action1.action_id,
        pteam2.pteam_id,
        service2.service_id,
        tag2_id,
        dependency2_id,
        threat2_id,
        ticket2_id,
        None,
        testdb,
    )
    actionlog2 = actionlogs2[0]

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


def test_get_topic_logs(testdb: Session):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, SERVICE1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam1_model = persistence.get_pteam_by_id(testdb, pteam1.pteam_id)
    assert pteam1_model is not None
    service1 = pteam1_model.services[0]
    tag1_id = service1.dependencies[0].tag.tag_id
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1, ACTION2])
    action1 = topic1.actions[0]
    action2 = topic1.actions[1]
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    dependency1_id = "dependency1_id"
    threat1_id = "threat1_id"
    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    actionlogs1 = create_actionlog_with_related_data(
        user1.user_id,
        USER1,
        topic1,
        action1.action_id,
        pteam1.pteam_id,
        service1.service_id,
        tag1_id,
        dependency1_id,
        threat1_id,
        ticket1_id,
        yesterday,
        testdb,
    )
    actionlog1 = actionlogs1[0]

    actionlogs2 = create_actionlog(
        USER1,
        action2.action_id,
        topic1.topic_id,
        user1.user_id,
        pteam1.pteam_id,
        service1.service_id,
        now,
    )
    actionlog2 = actionlogs2[0]

    response = client.get(f"/actionlogs/topics/{topic1.topic_id}", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
    assert data[1]["logging_id"] == str(actionlog1.logging_id)
