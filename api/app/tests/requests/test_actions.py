from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.tests.medium.constants import USER1, VULN1
from app.tests.medium.utils import (
    create_user,
    create_vuln,
    headers,
)

client = TestClient(app)


class TestCreateAction:

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        self.vuln_id = VULN1["vuln_id"]
        # Create a vuln
        create_vuln(USER1, VULN1)

    def test_response_200_if_create_action_successfully(self, testdb: Session):
        # Given
        action_create_request = {
            "vuln_id": str(self.vuln_id),
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


class TestUpdateAction:

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        create_vuln(USER1, VULN1)

        # Create an action
        action_create_request = {
            "vuln_id": VULN1["vuln_id"],
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        action_response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )
        self.action_id = action_response.json()["action_id"]
        self.vuln_id = action_response.json()["vuln_id"]
        self.created_at = action_response.json()["created_at"]

    def test_response_200_if_update_action_successfully(self, testdb: Session):
        # Given
        action_update_request = {
            "action": "updated action",
            "action_type": "mitigation",
            "recommended": False,
        }

        # When
        response = client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        assert response.status_code == 200
        assert response.json()["action"] == action_update_request["action"]
        assert response.json()["action_type"] == action_update_request["action_type"]
        assert response.json()["recommended"] == action_update_request["recommended"]
        assert response.json()["vuln_id"] == str(self.vuln_id)
        assert response.json()["action_id"] == str(self.action_id)
        assert response.json()["created_at"] == self.created_at

    def test_raise_404_if_action_id_does_not_exist(self):
        # Given
        non_existent_action_id = uuid4()
        action_update_request = {
            "action": "updated action",
        }

        # When
        response = client.put(
            f"/actions/{non_existent_action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such vuln action"}

    def test_raise_400_if_action_is_none(self):
        # Given
        action_update_request = {
            "action": None,
        }

        # When
        response = client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot specify None for action"}

    def test_raise_400_if_action_type_is_none(self):
        # Given
        action_update_request = {
            "action_type": None,
        }

        # When
        response = client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot specify None for action_type"}

    def test_raise_400_if_recommended_is_none(self):
        # Given
        action_update_request = {
            "recommended": None,
        }

        # When
        response = client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot specify None for recommended"}


class TestGetAction:

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        create_vuln(USER1, VULN1)

        # Create an action
        action_create_request = {
            "vuln_id": VULN1["vuln_id"],
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        action_response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )
        self.action_id = action_response.json()["action_id"]
        self.vuln_id = action_response.json()["vuln_id"]
        self.created_at = action_response.json()["created_at"]
        self.action = action_response.json()["action"]
        self.action_type = action_response.json()["action_type"]
        self.recommended = action_response.json()["recommended"]

    def test_return_action_and_response_200_if_get_action_successfully(self, testdb: Session):
        # When
        response = client.get(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        assert response.json()["action_id"] == str(self.action_id)
        assert response.json()["vuln_id"] == str(self.vuln_id)
        assert response.json()["action"] == self.action
        assert response.json()["action_type"] == self.action_type
        assert response.json()["recommended"] == self.recommended
        assert response.json()["created_at"] == self.created_at

    def test_raise_404_if_action_id_does_not_exist(self):
        # Given
        non_existent_action_id = uuid4()

        # When
        response = client.get(
            f"/actions/{non_existent_action_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such vuln action"}
