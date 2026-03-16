from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1, USER2
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
)

client = TestClient(app)


class TestGetSbomProgress:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        self.service1 = models.Service(
            pteam_id=self.pteam1.pteam_id,
            service_name="test service1",
        )
        testdb.add(self.service1)
        testdb.flush()

    def test_it_should_return_sbom_progress(self, testdb: Session):
        # Given
        progress_rate = 0.5
        created_at = datetime.now(timezone.utc)
        sbom_upload_progress = models.SbomUploadProgress(
            pteam_id=self.pteam1.pteam_id,
            service_name=self.service1.service_name,
            progress_rate=progress_rate,
            created_at=created_at,
        )
        testdb.add(sbom_upload_progress)
        testdb.flush()

        # When
        before = datetime.now(timezone.utc)
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/sbom_upload_progress", headers=headers(USER1)
        )
        after = datetime.now(timezone.utc)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "sbom_upload_progress_id" in data[0]
        assert data[0]["service_name"] == self.service1.service_name
        assert data[0]["progress_rate"] == progress_rate

        expected_finish_time = datetime.strptime(
            data[0]["expected_finish_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(tzinfo=timezone.utc)
        expected_min = created_at + (before - created_at) / progress_rate
        expected_max = created_at + (after - created_at) / progress_rate
        assert expected_min <= expected_finish_time <= expected_max

    def test_it_should_return_no_sbom_progress(self):
        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/sbom_upload_progress", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_return_404_when_pteam_id_does_not_exist(self):
        # Given
        non_existing_pteam_id = uuid4()

        # When
        response = client.get(
            f"/pteams/{non_existing_pteam_id}/sbom_upload_progress", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_return_403_when_not_pteam_member(self):
        # Given
        create_user(USER2)

        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/sbom_upload_progress", headers=headers(USER2)
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"
