import uuid
from pathlib import Path
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.main import app
from app.tests.common import threat_utils
from app.tests.medium.constants import (
    ACTION1,
    PTEAM1,
    PTEAM2,
    TAG1,
    TAG2,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    file_upload_headers,
    headers,
)

client = TestClient(app)

header_threat = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


@pytest.fixture(scope="function")
def threat1(testdb: Session) -> schemas.ThreatResponse:
    return threat_utils.create_threat(testdb, USER1, PTEAM1, TOPIC1, None)


@pytest.fixture(scope="function")
def threat2(testdb: Session) -> schemas.ThreatResponse:
    return threat_utils.create_threat(testdb, USER2, PTEAM2, TOPIC2, None)


def test_get_threat(threat1: schemas.ThreatResponse, threat2: schemas.ThreatResponse):

    data = assert_200(client.get("/threats/" + str(threat1.threat_id), headers=header_threat))
    assert data["threat_id"] == str(threat1.threat_id)
    assert data["dependency_id"] == str(threat1.dependency_id)
    assert data["topic_id"] == str(threat1.topic_id)


def test_get_threat_no_data():
    with pytest.raises(HTTPError, match=r"404: Not Found: No such threat"):
        assert_200(
            client.get("/threats/3fa85f64-5717-4562-b3fc-2c963f66afa6", headers=header_threat)
        )


def test_get_all_threats(testdb: Session):
    # create pteam
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # create topic
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)

    action1 = {
        **ACTION1,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: ["<0.30"],
            },
        },
    }
    action2 = {
        **ACTION1,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: ["<0.30"],
            },
        },
    }

    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name]}, actions=[action1])
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [tag2.parent_name]}, actions=[action2])

    # create service
    service1_name = "service_x"
    service1_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service1_id, pteam_id=pteam1.pteam_id, service_name=service1_name
        )
    )

    service2_name = "service_y"
    service2_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service2_id, pteam_id=pteam1.pteam_id, service_name=service2_name
        )
    )

    # create dependency
    dependency1_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency1_id,
            service_id=service1_id,
            tag_id=str(tag1.tag_id),
            version="1.0",
            target="Pipfile.lock",
        )
    )

    dependency2_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency2_id,
            service_id=service2_id,
            tag_id=str(tag2.tag_id),
            version="1.0",
            target="Pipfile.lock",
        )
    )

    # create threat
    threat1 = models.Threat(
        dependency_id=str(dependency1_id),
        topic_id=str(topic1.topic_id),
    )

    threat2 = models.Threat(
        dependency_id=str(dependency2_id),
        topic_id=str(topic2.topic_id),
    )

    persistence.create_threat(testdb, threat1)
    persistence.create_threat(testdb, threat2)
    testdb.commit()

    data = assert_200(client.get("/threats", headers=header_threat))
    assert len(data) == 2

    assert (data[0]["threat_id"] == str(threat1.threat_id)) or (
        data[0]["threat_id"] == str(threat2.threat_id)
    )
    assert (data[0]["dependency_id"] == str(threat1.dependency_id)) or (
        data[0]["dependency_id"] == str(threat2.dependency_id)
    )
    assert (data[0]["topic_id"] == str(threat1.topic_id)) or (
        data[0]["topic_id"] == str(threat2.topic_id)
    )

    assert (data[1]["threat_id"] == str(threat1.threat_id)) or (
        data[1]["threat_id"] == str(threat2.threat_id)
    )
    assert (data[1]["dependency_id"] == str(threat1.dependency_id)) or (
        data[1]["dependency_id"] == str(threat2.dependency_id)
    )
    assert (data[1]["topic_id"] == str(threat1.topic_id)) or (
        data[1]["topic_id"] == str(threat2.topic_id)
    )


@pytest.mark.parametrize(
    "exist_dependency_id, exist_topic_id, expected_len",
    [
        (False, False, 2),
        (True, False, 1),
        (False, True, 1),
        (True, True, 1),
    ],
)
def test_get_all_threats_with_param(
    testdb: Session,
    exist_dependency_id: bool,
    exist_topic_id: bool,
    expected_len: int,
):
    # create pteam
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # create topic
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)

    action1 = {
        **ACTION1,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: ["<0.30"],
            },
        },
    }
    action2 = {
        **ACTION1,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: ["<0.30"],
            },
        },
    }

    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name]}, actions=[action1])
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [tag2.parent_name]}, actions=[action2])

    # create service
    service1_name = "service_x"
    service1_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service1_id, pteam_id=pteam1.pteam_id, service_name=service1_name
        )
    )

    service2_name = "service_y"
    service2_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Service).values(
            service_id=service2_id, pteam_id=pteam1.pteam_id, service_name=service2_name
        )
    )

    # create dependency
    dependency1_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency1_id,
            service_id=service1_id,
            tag_id=str(tag1.tag_id),
            version="1.0",
            target="Pipfile.lock",
        )
    )

    dependency2_id = str(uuid.uuid4())
    testdb.execute(
        insert(models.Dependency).values(
            dependency_id=dependency2_id,
            service_id=service2_id,
            tag_id=str(tag2.tag_id),
            version="1.0",
            target="Pipfile.lock",
        )
    )

    # create threat
    threat1 = models.Threat(
        dependency_id=str(dependency1_id),
        topic_id=str(topic1.topic_id),
    )

    threat2 = models.Threat(
        dependency_id=str(dependency2_id),
        topic_id=str(topic2.topic_id),
    )

    persistence.create_threat(testdb, threat1)
    persistence.create_threat(testdb, threat2)
    testdb.commit()

    params = {}
    if exist_dependency_id:
        params["dependency_id"] = str(threat1.dependency_id)
    if exist_topic_id:
        params["topic_id"] = str(threat1.topic_id)

    response = client.get("/threats", headers=header_threat, params=params)
    if response.status_code != 200:
        raise HTTPError(response)
    data = response.json()
    assert len(data) == expected_len


def test_create_threat(testdb: Session):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # Uploaded sbom file.
    # Create tag, service and dependency table
    params: Dict[str, str | bool] = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "tag.jsonl"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/upload_tags_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )
        assert response.status_code == 200
        data = response.json()

    tag_id = data[0]["tag_id"]

    # Create topic and topicaction table
    tag_name_of_upload_sbom_file = data[0]["tag_name"]

    action = {
        **ACTION1,
        "ext": {
            "tags": [tag_name_of_upload_sbom_file],
            "vulnerable_versions": {
                tag_name_of_upload_sbom_file: ["<100"],  # Prevent auto close from being executed
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
            assert dependency.dependency_id == threat.dependency_id
            assert str(responsed_topic.topic_id) == threat.topic_id
