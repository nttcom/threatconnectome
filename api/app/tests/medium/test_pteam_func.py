from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app import models, persistence
from app.routers import pteams


@pytest.mark.parametrize(
    "updated_at_1, updated_at_2, topic_status_1, topic_status_2, expected_topic_status",
    [
        (
            "2099-01-01 01:00:00",
            "2099-01-01 00:00:00",
            models.TopicStatusType.alerted,
            models.TopicStatusType.scheduled,
            models.TopicStatusType.scheduled,
        ),
        (
            "2099-01-01 00:00:00",
            "2099-01-01 01:00:00",
            models.TopicStatusType.alerted,
            models.TopicStatusType.scheduled,
            models.TopicStatusType.alerted,
        ),
    ],
)
def test_get_oldest_status(
    updated_at_1: datetime,
    updated_at_2: datetime,
    topic_status_1: models.TopicStatusType,
    topic_status_2: models.TopicStatusType,
    expected_topic_status: models.TopicStatusType,
    testdb: Session,
):
    # Given
    pteam_id = "pteam1_id"
    testdb.execute(
        insert(models.PTeam).values(
            pteam_id=pteam_id,
            pteam_name="",
            contact_info="",
        )
    )

    tag_id = "da54de37-308e-40a7-a5ba-aab594796992"
    testdb.execute(
        insert(models.Tag).values(
            tag_id=tag_id,
            tag_name="",
        )
    )

    service_id = "service1_id"
    testdb.execute(
        insert(models.Service).values(
            service_id=service_id,
            pteam_id=pteam_id,
            service_name="",
            exposure=models.ExposureEnum.OPEN,
            service_mission_impact=models.MissionImpactEnum.MISSION_FAILURE,
        )
    )

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

    dependency2_id = "dependency2_id"
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency2_id,
            service_id=service_id,
            tag_id=tag_id,
            version="",
            target="2",
            dependency_mission_impact=models.MissionImpactEnum.MISSION_FAILURE,
        )
    )

    user_id = "user1_id"
    testdb.execute(
        insert(models.Account).values(
            user_id=user_id,
            disabled=False,
        )
    )

    topic_id = "71b6ff27-b6b5-431c-95d3-b2383be61209"
    testdb.execute(
        insert(models.Topic).values(
            topic_id=topic_id,
            title="",
            abstract="",
            threat_impact=2,
            created_by=user_id,
            created_at="2033-06-26 15:00:00",
            updated_at="2033-06-26 15:00:00",
            content_fingerprint="",
            safety_impact=models.SafetyImpactEnum.CATASTROPHIC,
            exploitation=models.ExploitationEnum.POC,
            automatable=True,
        )
    )

    threat1_id = "threat1_id"
    testdb.execute(
        insert(models.Threat).values(
            threat_id=threat1_id,
            dependency_id=dependency1_id,
            topic_id=topic_id,
        )
    )

    threat2_id = "threat2_id"
    testdb.execute(
        insert(models.Threat).values(
            threat_id=threat2_id,
            dependency_id=dependency2_id,
            topic_id=topic_id,
        )
    )

    ticket1_id = "3d362f0f-e08e-45a3-9ae9-5a46936372c0"
    testdb.execute(
        insert(models.Ticket).values(
            ticket_id=ticket1_id,
            threat_id=threat1_id,
            created_at="2033-06-26 15:00:00",
            updated_at="2033-06-26 15:00:00",
            ssvc_deployer_priority=models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        )
    )

    ticket2_id = "ticket2_id"
    testdb.execute(
        insert(models.Ticket).values(
            ticket_id=ticket2_id,
            threat_id=threat2_id,
            created_at="2033-06-26 15:00:00",
            updated_at="2033-06-26 15:00:00",
            ssvc_deployer_priority=models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE,
        )
    )

    status1_id = "status1_id"
    testdb.execute(
        insert(models.TicketStatus).values(
            status_id=status1_id,
            ticket_id=ticket1_id,
            user_id=user_id,
            topic_status=topic_status_1,
            logging_ids=[],
            assignees=[],
            scheduled_at="2050-06-26 15:00:00",
            created_at="2033-06-26 15:00:00",
        )
    )

    status2_id = "status2_id"
    testdb.execute(
        insert(models.TicketStatus).values(
            status_id=status2_id,
            ticket_id=ticket2_id,
            user_id=user_id,
            topic_status=topic_status_2,
            logging_ids=[],
            assignees=[],
            scheduled_at="2055-06-26 15:00:00",
            created_at="2033-06-26 15:00:00",
        )
    )

    current_status1_id = "current_status1_id"
    testdb.execute(
        insert(models.CurrentTicketStatus).values(
            current_status_id=current_status1_id,
            ticket_id=ticket1_id,
            status_id=status1_id,
            topic_status=topic_status_1,
            updated_at=updated_at_1,
        )
    )

    current_status2_id = "current_status2_id"
    testdb.execute(
        insert(models.CurrentTicketStatus).values(
            current_status_id=current_status2_id,
            ticket_id=ticket2_id,
            status_id=status2_id,
            topic_status=topic_status_2,
            updated_at=updated_at_2,
        )
    )

    service = persistence.get_service_by_id(testdb, service_id)
    assert service is not None

    # When
    oldest_status = pteams.get_oldest_status(service, UUID(topic_id), UUID(tag_id), testdb)

    # Then
    assert oldest_status is not None
    assert oldest_status.topic_status == expected_topic_status
