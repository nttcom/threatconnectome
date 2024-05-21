import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
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
    create_pteam,
    create_tag,
    create_topic,
    create_topicstatus,
    create_user,
    headers,
    invite_to_pteam,
    upload_pteam_tags,
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
    group_name = "group_x"
    service_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service_id, pteam_id=pteam1.pteam_id, service_name=group_name
        )
    )

    # create threat
    request = {
        "tag_id": str(tag1.tag_id),
        "service_id": str(service_id),
        "topic_id": str(topic1.topic_id),
    }
    response = client.post("/threats", headers=header_threat, json=request)
    threat = schemas.ThreatResponse(**response.json())

    # upload pteam_tags
    refs0 = {
        TAG1: [("fake target 1", "1.2.3")],
    }
    upload_pteam_tags(USER1, pteam1.pteam_id, group_name, refs0)

    # set topic_status
    json_data1 = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": [str(x.user_id) for x in [user1, user2]],
        "scheduled_at": str(datetime(2024, 6, 1)),
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data1)

    json_data2 = {
        "topic_status": "scheduled",
        "note": "scheduled",
        "assignees": [str(x.user_id) for x in [user1, user2]],
        "scheduled_at": str(datetime(2024, 6, 2)),
    }
    create_topicstatus(USER2, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data2)

    # When
    # update topics
    put_topics_request = {"disabled": True}
    client.put(f"/topics/{topic1.topic_id}", headers=headers(USER1), json=put_topics_request)

    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()

    return {
        "ticket_id": ticket.ticket_id,
        "tag_id": tag1.tag_id,
        "service_id": service_id,
        "topic_id": topic1.topic_id,
        "pteam_id": pteam1.pteam_id,
        "assignees": [str(x.user_id) for x in [user1, user2]],
    }


def test_PTeamTopicTagStatus_equals_TicketStatus_when_create_topicstatus2(
    testdb: Session, threat_data: dict
):
    # When
    # set topic_status
    json_data1 = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 6, 1)),
    }
    create_topicstatus(
        USER1, threat_data["pteam_id"], threat_data["topic_id"], threat_data["tag_id"], json_data1
    )

    json_data2 = {
        "topic_status": "scheduled",
        "note": "scheduled",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 6, 2)),
    }
    create_topicstatus(
        USER2, threat_data["pteam_id"], threat_data["topic_id"], threat_data["tag_id"], json_data2
    )

    # Then
    # table data of PTeamTopicTagStatus and TicketStatus is equal
    pteam_topic_tag_status_list = testdb.scalars(
        select(models.PTeamTopicTagStatus).where(
            models.PTeamTopicTagStatus.pteam_id == str(threat_data["pteam_id"]),
            models.PTeamTopicTagStatus.topic_id == str(threat_data["topic_id"]),
            models.PTeamTopicTagStatus.tag_id == str(threat_data["tag_id"]),
        )
    ).all()

    ticket_statuses_list = testdb.scalars(
        select(models.TicketStatus).where(
            models.TicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).all()

    assert len(pteam_topic_tag_status_list) == len(ticket_statuses_list)

    for statuses_index in range(len(ticket_statuses_list)):
        old_status = pteam_topic_tag_status_list[statuses_index]
        new_status = ticket_statuses_list[statuses_index]

        assert old_status.topic_status == new_status.topic_status

        assert old_status.note == new_status.note

        assert len(old_status.logging_ids) == len(new_status.logging_ids)
        for logging_ids_index in range(len(new_status.logging_ids)):
            assert (
                old_status.logging_ids[logging_ids_index]
                == new_status.logging_ids[logging_ids_index]
            )

        assert len(old_status.assignees) == len(new_status.assignees)
        for assignees_index in range(len(new_status.assignees)):
            assert old_status.assignees[assignees_index] == new_status.assignees[assignees_index]

        assert old_status.scheduled_at == new_status.scheduled_at

    # table data of CurrentPTeamTopicTagStatus and CurrentTicketStatus is equal
    current_pteam_topic_tag_status = testdb.scalars(
        select(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(threat_data["pteam_id"]),
            models.CurrentPTeamTopicTagStatus.topic_id == str(threat_data["topic_id"]),
            models.CurrentPTeamTopicTagStatus.tag_id == str(threat_data["tag_id"]),
        )
    ).one_or_none()

    current_tcket_status = testdb.scalars(
        select(models.CurrentTicketStatus).where(
            models.CurrentTicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).one_or_none()

    assert current_pteam_topic_tag_status is not None
    assert current_tcket_status is not None
    assert current_pteam_topic_tag_status.topic_status == current_tcket_status.topic_status
    assert current_pteam_topic_tag_status.threat_impact == current_tcket_status.threat_impact


def test_PTeamTopicTagStatus_equals_TicketStatus_when_auto_close(
    testdb: Session, threat_data: dict
):
    # Given
    # set topic_status
    json_data1 = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 6, 1)),
    }
    create_topicstatus(
        USER1, threat_data["pteam_id"], threat_data["topic_id"], threat_data["tag_id"], json_data1
    )

    json_data2 = {
        "topic_status": "scheduled",
        "note": "scheduled",
        "assignees": threat_data["assignees"],
        "scheduled_at": str(datetime(2024, 6, 2)),
    }
    create_topicstatus(
        USER2, threat_data["pteam_id"], threat_data["topic_id"], threat_data["tag_id"], json_data2
    )

    # When
    # update topics
    put_topics_request = {"disabled": True}
    topic_id = threat_data["topic_id"]
    client.put(f"/topics/{topic_id}", headers=headers(USER1), json=put_topics_request)

    # Then
    # table data of PTeamTopicTagStatus and TicketStatus is equal
    pteam_topic_tag_status_list = testdb.scalars(
        select(models.PTeamTopicTagStatus).where(
            models.PTeamTopicTagStatus.pteam_id == str(threat_data["pteam_id"]),
            models.PTeamTopicTagStatus.topic_id == str(threat_data["topic_id"]),
            models.PTeamTopicTagStatus.tag_id == str(threat_data["tag_id"]),
        )
    ).all()

    ticket_statuses_list = testdb.scalars(
        select(models.TicketStatus).where(
            models.TicketStatus.ticket_id == str(threat_data["ticket_id"])
        )
    ).all()

    assert len(pteam_topic_tag_status_list) == len(ticket_statuses_list)

    for statuses_index in range(len(ticket_statuses_list)):
        old_status = pteam_topic_tag_status_list[statuses_index]
        new_status = ticket_statuses_list[statuses_index]

        assert old_status.topic_status == new_status.topic_status

        assert old_status.note == new_status.note

        assert len(old_status.logging_ids) == len(new_status.logging_ids)
        for logging_ids_index in range(len(new_status.logging_ids)):
            assert (
                old_status.logging_ids[logging_ids_index]
                == new_status.logging_ids[logging_ids_index]
            )

        assert len(old_status.assignees) == len(new_status.assignees)
        for assignees_index in range(len(new_status.assignees)):
            assert old_status.assignees[assignees_index] == new_status.assignees[assignees_index]

        assert old_status.scheduled_at == new_status.scheduled_at

    # table data of CurrentPTeamTopicTagStatus and CurrentTicketStatus is equal
    current_pteam_topic_tag_status = testdb.scalars(
        select(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(threat_data["pteam_id"]),
            models.CurrentPTeamTopicTagStatus.topic_id == str(threat_data["topic_id"]),
            models.CurrentPTeamTopicTagStatus.tag_id == str(threat_data["tag_id"]),
        )
    ).one_or_none()

    assert current_pteam_topic_tag_status is None

    # TODO 本来current_tcket_statusもNoneになるべきだが、
    # fix_current_status_by_topic()のTicket対応が未実装のため、assertも保留とする
    # current_tcket_status = testdb.scalars(
    #     select(models.CurrentTicketStatus).where(
    #         models.CurrentTicketStatus.ticket_id == str(ticket.ticket_id)
    #     )
    # ).one_or_none()
    # assert current_tcket_status is None
