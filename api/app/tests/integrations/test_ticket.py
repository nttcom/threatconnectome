from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.common import threat_utils
from app.tests.medium.constants import ACTION1, PTEAM1, TOPIC1, USER1

client = TestClient(app)

header_threat = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def test_ticket_should_not_be_created_when_topic_action_does_not_exist(testdb: Session):
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, None)

    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket is None


def test_ticket_should_be_created_when_topic_action_exist_and_both_action_and_tag_have_child_tags(
    testdb: Session,
):
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

    # Then
    # Registered in the Ticket table.
    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket
    assert str(threat.threat_id) == str(ticket.threat_id)

    now = datetime.now()
    assert ticket.created_at > now - timedelta(seconds=30)
    assert ticket.created_at < now
    assert ticket.updated_at > now - timedelta(seconds=30)
    assert ticket.updated_at < now


def test_ticket_ssvc_deployer_priority(
    testdb: Session,
):
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket
    assert ticket.ssvc_deployer_priority == models.SSVCDeployerPriorityEnum.IMMEDIATE
