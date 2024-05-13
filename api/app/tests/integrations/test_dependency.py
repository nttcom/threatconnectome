from pathlib import Path
from typing import Dict, Union

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_user,
    file_upload_headers,
)

client = TestClient(app)

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


@pytest.mark.parametrize(
    "service_mission_impact, dependency_mission_impact, expected_mission_impact",
    [
        # Prioritize dependency_mission_impact.
        (
            models.MissionImpactEnum.CRIPPLED,
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.DEGRADED,
        ),
        # If dependency_mission_impact is None, service_mission_impact is enabled.
        (
            models.MissionImpactEnum.CRIPPLED,
            None,
            models.MissionImpactEnum.CRIPPLED,
        ),
        # The models.MissionImpactEnum.NONE is considered specified.
        (
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.NONE,
            models.MissionImpactEnum.NONE,
        ),
        (
            models.MissionImpactEnum.NONE,
            models.MissionImpactEnum.DEGRADED,
            models.MissionImpactEnum.DEGRADED,
        ),
    ],
)
def test_get_mission_impact(
    testdb: Session,
    service_mission_impact: models.MissionImpactEnum,
    dependency_mission_impact: models.MissionImpactEnum,
    expected_mission_impact: models.MissionImpactEnum,
):
    # Given
    # Uploaded sbom file.
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

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

    tag_id = data[0]["tag_id"]

    service_id = testdb.scalars(
        select(models.Service.service_id).where(
            models.Service.pteam_id == str(pteam1.pteam_id),
            models.Service.service_name == str(params["group"]),
        )
    ).one_or_none()

    # Set service_mission_impact and dependency_mission_impact.
    testdb.execute(
        update(models.Service)
        .where(models.Service.service_id == service_id)
        .values(service_mission_impact=service_mission_impact)
    )
    testdb.execute(
        update(models.Dependency)
        .where(
            models.Dependency.tag_id == str(tag_id), models.Dependency.service_id == str(service_id)
        )
        .values(dependency_mission_impact=dependency_mission_impact)
    )

    # When
    # Execute get_mission_impact.
    mission_impact = persistence.get_mission_impact(testdb, tag_id, str(service_id))

    # Then
    assert mission_impact == expected_mission_impact
