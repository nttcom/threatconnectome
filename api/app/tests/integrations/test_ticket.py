from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Union

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
from app.tests.common import threat_utils
from app.tests.medium.constants import PTEAM1, TOPIC1, USER1
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_topic,
    create_user,
    file_upload_headers,
)

client = TestClient(app)

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def test_create_threat_without_ticket(testdb: Session):
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1)

    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket is None


def test_create_ticket(testdb: Session):
    # Given
    # Topic has been created with hint_for_action.
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)
    testdb.execute(
        update(models.Topic)
        .where(models.Topic.topic_id == str(topic1.topic_id))
        .values(hint_for_action="hint1 for test")
    )

    # Uploaded sbom file.
    params: Dict[str, Union[str, bool]] = {"group": "threatconnectome", "force_mode": True}
    sbom_file = (
        Path(__file__).resolve().parent.parent
        / "common"
        / "upload_test"
        / "test_syft_cyclonedx.json"
    )
    with open(sbom_file, "rb") as tags:
        data = assert_200(
            client.post(
                f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )
        )

    # Create post threats request.
    tag_id = data[0]["tag_id"]

    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["group"]),
        )
    ).one_or_none()

    request = {
        "tag_id": str(tag_id),
        "service_id": str(service_id),
        "topic_id": str(topic1.topic_id),
    }

    # When
    # Post threats request.
    response = client.post("/threats", headers=headers, json=request)
    if response.status_code != 200:
        raise HTTPError(response)

    # Then
    # Registered in the Ticket table.
    threat = schemas.ThreatResponse(**response.json())

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
