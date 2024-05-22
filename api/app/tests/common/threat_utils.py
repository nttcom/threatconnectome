from pathlib import Path
from typing import Dict, Union

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.main import app
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


def create_threat(testdb: Session, user: dict, pteam: dict, topic: dict) -> schemas.ThreatResponse:
    create_user(user)
    pteam1 = create_pteam(user, pteam)
    topic1 = create_topic(user, topic)

    params: Dict[str, Union[str, bool]] = {"group": "threatconnectome", "force_mode": True}
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

    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["group"]),
        )
    ).one_or_none()

    dependency = persistence.get_dependency_from_service_id_and_tag_id(
        testdb, str(service_id), str(tag_id)
    )

    if dependency:
        request = {
            "dependency_id": str(dependency.dependency_id),
            "topic_id": str(topic1.topic_id),
        }
        response = client.post("/threats", headers=headers, json=request)
        if response.status_code != 200:
            raise HTTPError(response)

    return schemas.ThreatResponse(**response.json())
