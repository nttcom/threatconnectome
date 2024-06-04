from pathlib import Path
from typing import Dict, Union
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.main import app
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_user,
    file_upload_headers,
    headers,
)

client = TestClient(app)


def create_threat(
    testdb: Session, user: dict, pteam: dict, topic: dict, action: dict | None
) -> schemas.ThreatResponse:
    create_user(user)
    pteam1 = create_pteam(user, pteam)

    # Uploaded sbom file.
    # Create tag, service and dependency table
    params: Dict[str, Union[str, bool]] = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "test_syft_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        data = assert_200(
            client.post(
                f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(user),
                params=params,
                files={"file": tags},
            )
        )

    tag_id = data[0]["tag_id"]

    # Create topic and topicaction table
    tag_name_of_upload_sbom_file = data[0]["tag_name"]

    if action:
        action = {
            **action,
            "ext": {
                "tags": [tag_name_of_upload_sbom_file],
                "vulnerable_versions": {
                    tag_name_of_upload_sbom_file: [
                        "<100"
                    ],  # Prevent auto close from being executed
                },
            },
        }

        topic = {
            **topic,
            "tags": [tag_name_of_upload_sbom_file],
            "actions": [action],
        }

    else:
        topic = {
            **topic,
            "tags": [tag_name_of_upload_sbom_file],
        }

    request = {**topic}
    del request["topic_id"]

    response = client.post(f'/topics/{topic["topic_id"]}', headers=headers(user), json=request)

    assert response.status_code == 200
    responsed_topic = schemas.TopicCreateResponse(**response.json())

    # Saerch threat table
    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["service"]),
        )
    ).one_or_none()

    dependency = persistence.get_dependency_from_service_id_and_tag_id(
        testdb, str(service_id), str(tag_id)
    )

    if dependency:
        threats = persistence.search_threats(
            testdb, str(dependency.dependency_id), str(responsed_topic.topic_id)
        )

        assert threats

        for threat in threats:
            response_threat = schemas.ThreatResponse(
                threat_id=UUID(threat.threat_id),
                dependency_id=UUID(threat.dependency_id),
                topic_id=UUID(threat.topic_id),
            )

    return response_threat
