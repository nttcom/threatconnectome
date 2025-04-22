from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.tests.medium.constants import (
    USER1,
)
from app.tests.medium.utils import (
    create_user,
    headers,
)

client = TestClient(app)


class TestCreateAction:

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        self.new_vuln_id = uuid4()
        vuln_request1 = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

        client.put(f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=vuln_request1)

    def test_response_200_if_create_action_successfully(self, testdb: Session):
        # Given
        action_create_request = {
            "vuln_id": str(self.new_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # When
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        assert response.status_code == 200

    def test_raise_400_if_vuln_id_is_invalid(self):
        """
        Test that create_action raises a 400 error if vuln_id is invalid.
        """
        # Given
        invalid_vuln_id = uuid4()
        action_create_request = {
            "vuln_id": str(invalid_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # Send the request and check the response
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "No such vuln"}

    def test_raise_400_if_vuln_id_is_none(self):
        """
        Test that create_action raises a 400 error if vuln_id is None.
        """
        # Given
        action_create_request = {
            "vuln_id": None,
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # Send the request and check the response
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "Missing vuln_id"}
