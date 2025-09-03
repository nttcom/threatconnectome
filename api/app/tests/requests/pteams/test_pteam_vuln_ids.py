from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models, persistence
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    VULN1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    set_ticket_status,
)

client = TestClient(app)


class TestGetVulnIdsTiedToServicePackage:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        service_name = "test_service1"
        self.ticket_response = ticket_utils.create_ticket(
            testdb, USER1, PTEAM1, service_name, VULN1
        )

        json_data = {
            "ticket_handling_status": "acknowledged",
            "note": "string",
            "assignees": [],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response["pteam_id"],
            self.ticket_response["ticket_id"],
            json_data,
        )

    def test_it_should_return_404_with_wrong_pteam_id(self):
        # Given
        wrong_pteam_id = str(uuid4())

        # When
        response = client.get(
            f"/pteams/{wrong_pteam_id}/vuln_ids?service_id={self.ticket_response['service_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such pteam"}

    def test_it_should_return_403_with_wrong_pteam_member(self):
        # Given
        create_user(USER2)  # with wrong pteam member

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?service_id={self.ticket_response['service_id']}",
            headers=headers(USER2),
        )

        # Then
        assert response.status_code == 403
        assert response.json() == {"detail": "Not a pteam member"}

    def test_it_should_return_404_with_wrong_service_id(self):
        # Given
        wrong_service_id = str(uuid4())  # with wrong service_id

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?service_id={wrong_service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service"}

    def test_it_should_return_404_with_service_not_in_pteam(self, testdb):
        # Given
        pteam2 = create_pteam(USER1, PTEAM2)
        service2 = models.Service(
            service_name="test_service2",
            pteam_id=str(pteam2.pteam_id),
        )
        testdb.add(service2)
        testdb.flush()

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?service_id={service2.service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service"}

    def test_it_should_return_404_with_wrong_package_id(self):
        # Given
        wrong_package_id = str(uuid4())  # with wrong tag_id

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?service_id={self.ticket_response['service_id']}&package_id={wrong_package_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such package"}

    def test_it_should_return_404_with_valid_but_not_service_package(self, testdb):
        # Given
        # with valid but not service package
        package = models.Package(
            name="a1",
            ecosystem="a2",
        )
        persistence.create_package(testdb, package)

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?service_id={self.ticket_response['service_id']}&package_id={package.package_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service package"}

    def test_it_should_return_404_with_wrong_related_ticket_status(self, testdb):
        # Given
        related_ticket_status = "wrong_status"

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/vuln_ids?related_ticket_status={related_ticket_status}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Input should be 'solved' or 'unsolved'"
