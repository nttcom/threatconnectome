import uuid
from datetime import datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.common import threat_meets_condition_to_create_ticket
from app.main import app
from app.ssvc import calculate_ssvc_deployer_priority
from app.tests.common import threat_utils
from app.tests.medium.constants import (
    ACTION1,
    PTEAM1,
    TAG1,
    TOPIC1,
    USER1,
    USER2,
)
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_actionlog,
    create_pteam,
    create_service_topicstatus,
    create_tag,
    create_topic,
    create_user,
    invite_to_pteam,
)

client = TestClient(app)

header_threat = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


@pytest.fixture
def threat_data(testdb: Session) -> dict:
    # create pteam
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # create topic
    tag1 = create_tag(USER1, TAG1)
    action = {
        **ACTION1,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: ["<0.30"],
            },
        },
    }
    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name]}, actions=[action])

    # create service
    service_name = "service_x"
    service_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service_id, pteam_id=pteam1.pteam_id, service_name=service_name
        )
    )

    # create dependency
    dependency_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency_id,
            service_id=service_id,
            tag_id=str(tag1.tag_id),
            version="1.0",
            target="Pipfile.lock",
        )
    )

    # create threat
    threat = models.Threat(
        dependency_id=str(dependency_id),
        topic_id=str(topic1.topic_id),
    )
    persistence.create_threat(testdb, threat)

    # create ticket
    now = datetime.now()
    if threat_meets_condition_to_create_ticket(testdb, threat):
        _ticket = models.Ticket(
            threat_id=threat.threat_id,
            created_at=now,
            updated_at=now,
            ssvc_deployer_priority=calculate_ssvc_deployer_priority(threat),
        )
        persistence.create_ticket(testdb, _ticket)

    testdb.commit()

    # get threat_id
    threats = persistence.search_threats(testdb, dependency_id, topic1.topic_id)
    for _threat in threats:
        threat_data = schemas.ThreatResponse(
            threat_id=uuid.UUID(_threat.threat_id),
            dependency_id=uuid.UUID(_threat.dependency_id),
            topic_id=uuid.UUID(_threat.topic_id),
        )

    ticket_id: str = ""
    if ticket := testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat_data.threat_id))
    ).one_or_none():
        ticket_id = str(ticket.ticket_id)
    return {
        "ticket_id": ticket_id,
        "tag_id": tag1.tag_id,
        "service_id": service_id,
        "topic_id": topic1.topic_id,
        "pteam_id": pteam1.pteam_id,
        "assignees": [str(x.user_id) for x in [user1, user2]],
    }


def test_TicketStatus_when_create_pteam_topicstatus(testdb: Session, threat_data: dict):
    # When
    # set topic_status
    json_data1 = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 5, 1)),
    }
    create_service_topicstatus(
        USER1,
        threat_data["pteam_id"],
        threat_data["service_id"],
        threat_data["topic_id"],
        threat_data["tag_id"],
        json_data1,
    )

    json_data2 = {
        "topic_status": "scheduled",
        "note": "scheduled",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 5, 2)),
    }
    create_service_topicstatus(
        USER2,
        threat_data["pteam_id"],
        threat_data["service_id"],
        threat_data["topic_id"],
        threat_data["tag_id"],
        json_data2,
    )

    # Then
    # check TicketStatus
    ticket_statuses_list = testdb.scalars(
        select(models.TicketStatus).where(
            models.TicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).all()

    assert len(ticket_statuses_list) == 2
    for status in ticket_statuses_list:
        if status.note == "acknowledged":
            assert status.user_id == threat_data["assignees"][0]
            assert status.topic_status == models.TopicStatusType.acknowledged
            assert len(status.logging_ids) == 0
            assert len(status.assignees) == 2
            assert all(assignee in threat_data["assignees"] for assignee in status.assignees)
            assert status.scheduled_at == datetime(2024, 5, 1)
        elif status.note == "scheduled":
            assert status.user_id == threat_data["assignees"][1]
            assert status.topic_status == models.TopicStatusType.scheduled
            assert len(status.logging_ids) == 0
            assert len(status.assignees) == 2
            assert all(assignee in threat_data["assignees"] for assignee in status.assignees)
            assert status.scheduled_at == datetime(2024, 5, 2)

    # check CurrentTicketStatus
    current_tcket_status = testdb.scalars(
        select(models.CurrentTicketStatus).where(
            models.CurrentTicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).one_or_none()

    assert current_tcket_status is not None
    assert current_tcket_status.topic_status == models.TopicStatusType.scheduled
    assert current_tcket_status.threat_impact == 1


def test_TicketStatus_when_create_service_topicstatus(testdb: Session, threat_data: dict):
    # When
    # set topic_status
    json_data1 = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 5, 1)),
    }
    create_service_topicstatus(
        USER1,
        threat_data["pteam_id"],
        threat_data["service_id"],
        threat_data["topic_id"],
        threat_data["tag_id"],
        json_data1,
    )

    json_data2 = {
        "topic_status": "scheduled",
        "note": "scheduled",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 5, 2)),
    }
    create_service_topicstatus(
        USER2,
        threat_data["pteam_id"],
        threat_data["service_id"],
        threat_data["topic_id"],
        threat_data["tag_id"],
        json_data2,
    )

    # Then
    # check TicketStatus
    ticket_statuses_list = testdb.scalars(
        select(models.TicketStatus).where(
            models.TicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).all()

    assert len(ticket_statuses_list) == 2
    for status in ticket_statuses_list:
        if status.note == "acknowledged":
            assert status.user_id == threat_data["assignees"][0]
            assert status.topic_status == models.TopicStatusType.acknowledged
            assert len(status.logging_ids) == 0
            assert len(status.assignees) == 2
            assert all(assignee in threat_data["assignees"] for assignee in status.assignees)
            assert status.scheduled_at == datetime(2024, 5, 1)
        elif status.note == "scheduled":
            assert status.user_id == threat_data["assignees"][1]
            assert status.topic_status == models.TopicStatusType.scheduled
            assert len(status.logging_ids) == 0
            assert len(status.assignees) == 2
            assert all(assignee in threat_data["assignees"] for assignee in status.assignees)
            assert status.scheduled_at == datetime(2024, 5, 2)

    # check CurrentTicketStatus
    current_tcket_status = testdb.scalars(
        select(models.CurrentTicketStatus).where(
            models.CurrentTicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).one_or_none()

    assert current_tcket_status is not None
    assert current_tcket_status.topic_status == models.TopicStatusType.scheduled
    assert current_tcket_status.threat_impact == 1


def test_CurrentTicketStatus_when_create_threat(testdb: Session):
    # When
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

    # Then
    # check CurrentTicketStatus
    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket is not None

    current_tcket_status = testdb.scalars(
        select(models.CurrentTicketStatus).where(
            models.CurrentTicketStatus.ticket_id == str(ticket.ticket_id)
        )
    ).one_or_none()

    assert current_tcket_status is not None
    assert current_tcket_status.status_id is None
    assert current_tcket_status.topic_status == models.TopicStatusType.alerted
    assert current_tcket_status.threat_impact == 1


def test_TicketStatus_with_multi_ActionLogs(testdb: Session):
    # Given
    # A service has tow ticket with same topic_id and tag_id.
    threat_respose1 = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, ACTION1)
    user1 = persistence.get_account_by_email(testdb, str(USER1["email"]))
    assert user1 is not None
    threats1 = persistence.search_threats(
        testdb, threat_respose1.dependency_id, threat_respose1.topic_id
    )
    threat1 = threats1[0]

    dependency2_id = "1d362f0f-e08e-45a3-9ae9-5a46936372c1"
    threat2_id = "2d362f0f-e08e-45a3-9ae9-5a46936372c2"
    ticket2_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c3"
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency2_id,
            service_id=threat1.dependency.service.service_id,
            tag_id=threat1.dependency.tag.tag_id,
            version="",
            target="2",
            dependency_mission_impact=models.MissionImpactEnum.MISSION_FAILURE,
        )
    )
    testdb.execute(
        insert(models.Threat).values(
            threat_id=threat2_id, dependency_id=dependency2_id, topic_id=threat1.topic.topic_id
        )
    )
    testdb.execute(
        insert(models.Ticket).values(
            ticket_id=ticket2_id,
            threat_id=threat2_id,
            created_at="2033-06-26 15:00:00",
            updated_at="2033-06-26 15:00:00",
            ssvc_deployer_priority=models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        )
    )

    # When
    # create ActionLog and create TicketTopicStatus
    actionlogs1 = create_actionlog(
        USER1,
        threat1.topic.actions[0].action_id,
        threat1.topic.topic_id,
        UUID(user1.user_id),
        threat1.dependency.service.pteam.pteam_id,
        threat1.dependency.service.service_id,
        None,
    )
    for actionlog in actionlogs1:
        if str(threat1.ticket.ticket_id) == str(actionlog.ticket_id):
            ticket1_logging_id = actionlog.logging_id
        elif ticket2_id == str(actionlog.ticket_id):
            ticket2_logging_id = actionlog.logging_id

    json_data = {
        "topic_status": "acknowledged",
        "logging_ids": [str(ticket1_logging_id), str(ticket2_logging_id)],
        "note": "acknowledged",
        "assignees": [str(user1.user_id)],
        "scheduled_at": str(datetime(2024, 5, 1)),
    }
    create_service_topicstatus(
        USER1,
        threat1.dependency.service.pteam.pteam_id,
        threat1.dependency.service.service_id,
        threat1.topic.topic_id,
        threat1.dependency.tag.tag_id,
        json_data,
    )

    # Then
    # each ticket record has logging_id
    ticket_statuses_list1 = testdb.scalars(
        select(models.TicketStatus).where(
            models.TicketStatus.ticket_id == str(threat1.ticket.ticket_id)
        )
    ).all()
    assert len(ticket_statuses_list1) == 1
    assert len(ticket_statuses_list1[0].logging_ids) == 1
    assert str(ticket_statuses_list1[0].logging_ids[0]) == str(ticket1_logging_id)

    ticket_statuses_list2 = testdb.scalars(
        select(models.TicketStatus).where(models.TicketStatus.ticket_id == ticket2_id)
    ).all()
    assert len(ticket_statuses_list2) == 1
    assert len(ticket_statuses_list2[0].logging_ids) == 1
    assert str(ticket_statuses_list2[0].logging_ids[0]) == str(ticket2_logging_id)
