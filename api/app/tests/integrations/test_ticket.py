from datetime import datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
from app.tests.common import threat_utils
from app.tests.medium.constants import ACTION1, PTEAM1, TOPIC1, USER1
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_user,
    file_upload_headers,
    headers,
)

client = TestClient(app)

header_threat = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


def test_ticket_should_not_be_created_when_topic_action_does_not_exist(testdb: Session):
    threat = threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1)

    ticket = testdb.scalars(
        select(models.Ticket).where(models.Ticket.threat_id == str(threat.threat_id))
    ).one_or_none()
    assert ticket is None


def test_ticket_should_be_created_when_topic_action_exist_and_both_action_and_tag_have_child_tags(
    testdb: Session,
):
    # Given
    # Topic has been created with topic action table.
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # Uploaded sbom file.
    params: dict[str, str | bool] = {"group": "threatconnectome", "force_mode": True}
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

    # create topic and topic action table
    tag_name_of_upload_sbom_file = data[0]["tag_name"]

    action = {
        **ACTION1,
        "ext": {
            "tags": [tag_name_of_upload_sbom_file],
            "vulnerable_versions": {
                tag_name_of_upload_sbom_file: ["<0.30"],
            },
        },
    }

    topic = {
        **TOPIC1,
        "tags": [tag_name_of_upload_sbom_file],
        "actions": [action],
    }

    request = {**topic}
    del request["topic_id"]

    response = client.post(f'/topics/{topic["topic_id"]}', headers=headers(USER1), json=request)

    assert response.status_code == 200
    responsed_topic = schemas.TopicCreateResponse(**response.json())

    # Create post threats request.
    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["group"]),
        )
    ).one_or_none()

    request = {
        "tag_id": str(data[0]["tag_id"]),
        "service_id": str(service_id),
        "topic_id": str(responsed_topic.topic_id),
    }

    # When
    # Post threats request.
    response = client.post("/threats", headers=header_threat, json=request)
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
