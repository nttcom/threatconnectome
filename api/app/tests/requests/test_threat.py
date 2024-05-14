from pathlib import Path
from typing import Dict, Union

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
from app.tests.common import threat_utils
from app.tests.medium.constants import PTEAM1, PTEAM2, TOPIC1, TOPIC2, USER1, USER2
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


@pytest.fixture
def threat1(testdb: Session) -> schemas.ThreatResponse:
    return threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1)


@pytest.fixture
def threat2(testdb: Session) -> schemas.ThreatResponse:
    return threat_utils.create_threat(testdb, USER2, PTEAM2, TOPIC2)


def test_get_threat(threat1: schemas.ThreatResponse, threat2: schemas.ThreatResponse):

    data = assert_200(client.get("/threats/" + str(threat1.threat_id), headers=headers))
    assert data["threat_id"] == str(threat1.threat_id)
    assert data["tag_id"] == str(threat1.tag_id)
    assert data["service_id"] == str(threat1.service_id)
    assert data["topic_id"] == str(threat1.topic_id)


def test_get_threat_no_data():
    with pytest.raises(HTTPError, match=r"404: Not Found: No such threat"):
        assert_200(client.get("/threats/3fa85f64-5717-4562-b3fc-2c963f66afa6", headers=headers))


def test_get_all_threats(threat1: schemas.ThreatResponse, threat2: schemas.ThreatResponse):
    data = assert_200(client.get("/threats", headers=headers))
    assert len(data) == 2

    assert (data[0]["threat_id"] == str(threat1.threat_id)) or (
        data[0]["threat_id"] == str(threat2.threat_id)
    )
    assert (data[0]["tag_id"] == str(threat1.tag_id)) or (data[0]["tag_id"] == str(threat2.tag_id))
    assert (data[0]["service_id"] == str(threat1.service_id)) or (
        data[0]["service_id"] == str(threat2.service_id)
    )
    assert (data[0]["topic_id"] == str(threat1.topic_id)) or (
        data[0]["topic_id"] == str(threat2.topic_id)
    )

    assert (data[1]["threat_id"] == str(threat1.threat_id)) or (
        data[1]["threat_id"] == str(threat2.threat_id)
    )
    assert (data[1]["tag_id"] == str(threat1.tag_id)) or (data[1]["tag_id"] == str(threat2.tag_id))
    assert (data[1]["service_id"] == str(threat1.service_id)) or (
        data[1]["service_id"] == str(threat2.service_id)
    )
    assert (data[1]["topic_id"] == str(threat1.topic_id)) or (
        data[1]["topic_id"] == str(threat2.topic_id)
    )


@pytest.mark.parametrize(
    "exist_tag_id, exist_service_id, exist_topic_id, expected_len",
    [
        (False, False, False, 2),
        (True, False, False, 2),  # 本ケースでは、tag_idは2件同一
        (False, True, False, 1),
        (False, False, True, 1),
        (True, True, True, 1),
    ],
)
def test_get_all_threats_with_param(
    exist_tag_id: bool,
    exist_service_id: bool,
    exist_topic_id: bool,
    expected_len: int,
    threat1: schemas.ThreatResponse,
    threat2: schemas.ThreatResponse,
):

    url: str = "/threats"
    if exist_tag_id or exist_service_id or exist_topic_id:
        url += "/?"
    if exist_tag_id:
        url += "tag_id=" + str(threat1.tag_id)
        if exist_service_id or exist_topic_id:
            url += "&"
    if exist_service_id:
        url += "service_id=" + str(threat1.service_id)
        if exist_topic_id:
            url += "&"
    if exist_topic_id:
        url += "topic_id=" + str(threat1.topic_id)

    data = assert_200(client.get(url, headers=headers))
    assert len(data) == expected_len


def test_create_threat(testdb: Session):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)

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
    response = client.post("/threats", headers=headers, json=request)
    if response.status_code != 200:
        raise HTTPError(response)

    threat = schemas.ThreatResponse(**response.json())

    assert request["tag_id"] == str(threat.tag_id)
    assert request["service_id"] == str(threat.service_id)
    assert request["topic_id"] == str(threat.topic_id)


def test_delete_threat(threat1: schemas.ThreatResponse):
    response = client.delete(f"/threats/{threat1.threat_id}", headers=headers)
    assert response.status_code == 204

    data = assert_200(client.get("/threats", headers=headers))
    assert len(data) == 0
