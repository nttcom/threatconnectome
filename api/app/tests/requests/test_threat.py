from pathlib import Path
from typing import Dict, Union

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
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


def test_get_threat_no_data():
    with pytest.raises(HTTPError, match=r"404: Not Found: No such threat"):
        assert_200(client.get("/threats/3fa85f64-5717-4562-b3fc-2c963f66afa6", headers=headers))


def test_get_all_threats(testdb: Session):
    response1 = create_threat(testdb, USER1, PTEAM1, TOPIC1)
    data = assert_200(client.get("/threats", headers=headers))
    assert len(data) == 1
    assert data[0]["threat_id"] == str(response1.threat_id)
    assert data[0]["tag_id"] == str(response1.tag_id)
    assert data[0]["service_id"] == str(response1.service_id)
    assert data[0]["topic_id"] == str(response1.topic_id)


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
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )
        )

    ##tag_idの取得
    tag_id = data[0]["tag_id"]

    ##service_idの取得
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
    response = client.post("/threats", headers=headers, json=request)
    if response.status_code != 200:
        raise HTTPError(response)

    return schemas.ThreatResponse(**response.json())


def test_create_threat(testdb: Session):
    create_threat(testdb, USER1, PTEAM1, TOPIC1)
