from pathlib import Path
from typing import Dict, Union

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    file_upload_headers,
)

client = TestClient(app)


def create_ticket(testdb: Session, user: dict, pteam: dict, topic: dict):
    create_user(user)
    pteam1 = create_pteam(user, pteam)

    # Uploaded sbom file.
    # Create tag, service and dependency table
    params: Dict[str, Union[str, bool]] = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "tag.jsonl"
    with open(sbom_file, "rb") as tags:
        response_upload_sbom_file = client.post(
            f"/pteams/{pteam1.pteam_id}/upload_tags_file",
            headers=file_upload_headers(user),
            params=params,
            files={"file": tags},
        )
        assert response_upload_sbom_file.status_code == 200
        data = response_upload_sbom_file.json()

    tag_id = data[0]["tag_id"]

    # Create topic and topicaction table
    tag_name_of_upload_sbom_file = data[0]["tag_name"]

    # TODO Provisional Processing
    # responsed_topic = create_topic_with_versioned_actions(
    #     user, topic, [[tag_name_of_upload_sbom_file]]
    # )

    # Saerch threat table
    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["service"]),
        )
    ).one_or_none()

    # TODO Provisional Processing
    # dependency = persistence.get_dependency_from_service_id_and_tag_id(
    #     testdb, str(service_id), str(tag_id)
    # )

    # if dependency:
    #     threats = command.search_threats(
    #         testdb, None, str(dependency.dependency_id), str(responsed_topic.topic_id)
    #     )

    #     assert threats

    return {
        "pteam_id": str(pteam1.pteam_id),
        "service_id": str(service_id),
        "tag_id": str(tag_id),
        "tag_name": data[0]["tag_name"],
        # TODO Provisional Processing
        # "topic_id": str(responsed_topic.topic_id),
        # "threat_id": str(threats[0].threat_id),
        # "ticket_id": str(threats[0].ticket.ticket_id),
        "topic_id": "",
        "threat_id": "",
        "ticket_id": "",
    }
