from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.tests.medium.constants import USER1
from app.tests.medium.utils import (
    create_user,
    headers,
    headers_with_api_key,
)

client = TestClient(app)


class TestUpdateEol:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        self.user1 = create_user(USER1)
        self.request1 = {
            "name": "test_eol_product",
            "product_category": models.ProductCategoryEnum.PACKAGE,
            "description": "test_description",
            "is_ecosystem": False,
            "matching_name": "test_matching_name",
            "eol_versions": [
                {
                    "version": "2.0.0",
                    "release_date": "2020-01-02",
                    "eol_from": "2030-01-02",
                    "matching_version": "2.0.0",
                }
            ],
        }

    @pytest.fixture(scope="function", autouse=False)
    def update_setup(self):
        self.eol_product_id = uuid4()
        self.response1_eol = client.put(
            f"/eols/{self.eol_product_id}", headers=headers_with_api_key(USER1), json=self.request1
        )

    def test_return_200_when_create_eol_successfully(self):
        # Given
        new_eol_product_id = uuid4()
        current_time = datetime.now(timezone.utc)

        # When
        response = client.put(
            f"/eols/{new_eol_product_id}", headers=headers_with_api_key(USER1), json=self.request1
        )

        # Then
        assert response.status_code == 200
        assert response.json()["eol_product_id"] == str(new_eol_product_id)
        assert response.json()["name"] == self.request1["name"]
        assert response.json()["product_category"] == self.request1["product_category"]
        assert response.json()["description"] == self.request1["description"]
        assert response.json()["is_ecosystem"] == self.request1["is_ecosystem"]
        assert response.json()["matching_name"] == self.request1["matching_name"]
        assert (
            response.json()["eol_versions"][0]["version"]
            == self.request1["eol_versions"][0]["version"]
        )
        assert (
            response.json()["eol_versions"][0]["release_date"]
            == self.request1["eol_versions"][0]["release_date"]
        )
        assert (
            response.json()["eol_versions"][0]["eol_from"]
            == self.request1["eol_versions"][0]["eol_from"]
        )
        assert (
            response.json()["eol_versions"][0]["matching_version"]
            == self.request1["eol_versions"][0]["matching_version"]
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                response.json()["eol_versions"][0]["created_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                response.json()["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )

    def test_return_200_when_update_eol_successfully(self, update_setup):
        # Given
        current_time = datetime.now(timezone.utc)
        update_request = {
            "name": "test_update_eol_product",
            "product_category": models.ProductCategoryEnum.OS,
            "description": "test_update_description",
            "is_ecosystem": True,
            "matching_name": "test_update_matching_name",
            "eol_versions": [
                {
                    "version": "2.0.0",
                    "release_date": "2020-01-06",
                    "eol_from": "2030-02-01",
                    "matching_version": "<2.0",
                },
                {
                    "version": "3.0.0",
                    "release_date": "2021-01-02",
                    "eol_from": "2032-01-02",
                    "matching_version": "3.0.0",
                },
            ],
        }

        # When
        update_response = client.put(
            f"/eols/{self.eol_product_id}",
            headers=headers_with_api_key(USER1),
            json=update_request,
        )

        # Then
        assert update_response.status_code == 200
        assert update_response.json()["eol_product_id"] == str(self.eol_product_id)
        assert update_response.json()["name"] == update_request["name"]
        assert update_response.json()["product_category"] == update_request["product_category"]
        assert update_response.json()["description"] == update_request["description"]
        assert update_response.json()["is_ecosystem"] == update_request["is_ecosystem"]
        assert update_response.json()["matching_name"] == update_request["matching_name"]
        assert update_response.json()["eol_versions"][0]["version"] in [
            eol_version["version"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][0]["release_date"] in [
            eol_version["release_date"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][0]["eol_from"] in [
            eol_version["eol_from"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][0]["matching_version"] in [
            eol_version["matching_version"] for eol_version in update_request["eol_versions"]
        ]
        assert (
            update_response.json()["eol_versions"][0]["created_at"]
            == self.response1_eol.json()["eol_versions"][0]["created_at"]
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                update_response.json()["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert update_response.json()["eol_versions"][1]["version"] in [
            eol_version["version"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][1]["release_date"] in [
            eol_version["release_date"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][1]["eol_from"] in [
            eol_version["eol_from"] for eol_version in update_request["eol_versions"]
        ]
        assert update_response.json()["eol_versions"][1]["matching_version"] in [
            eol_version["matching_version"] for eol_version in update_request["eol_versions"]
        ]
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                update_response.json()["eol_versions"][1]["created_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                update_response.json()["eol_versions"][1]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )

    @pytest.mark.parametrize(
        "field_name",
        [
            "name",
            "product_category",
            "is_ecosystem",
            "matching_name",
            "version",
            "release_date",
            "eol_from",
            "matching_version",
        ],
    )
    def test_raise_400_when_create_if_field_with_none(self, field_name):
        # Given
        new_eol_product_id = uuid4()
        request = self.request1
        name = ["version", "release_date", "eol_from", "matching_version"]
        if field_name in name:
            request["eol_versions"][0][f"{field_name}"] = None
        else:
            request[f"{field_name}"] = None

        # When
        response = client.put(
            f"/eols/{new_eol_product_id}", headers=headers_with_api_key(USER1), json=request
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == f"Cannot specify None for {field_name}"

    @pytest.mark.parametrize(
        "field_name",
        [
            "name",
            "product_category",
            "is_ecosystem",
            "matching_name",
            "version",
            "release_date",
            "eol_from",
            "matching_version",
        ],
    )
    def test_raise_400_when_update_if_field_with_none(self, update_setup, field_name):
        # Given
        name = ["version", "release_date", "eol_from", "matching_version"]
        if field_name in name:
            invalid_request = {"eol_versions": [{f"{field_name}": None}]}
        else:
            invalid_request = {
                f"{field_name}": None,
            }

        # When
        response = client.put(
            f"/eols/{self.eol_product_id}",
            headers=headers_with_api_key(USER1),
            json=invalid_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == f"Cannot specify None for {field_name}"

    def test_raise_400_whe_update_if_version_is_not_specified(self, update_setup):
        # Given
        update_request = {
            "eol_versions": [
                {
                    "eol_from": "2030-02-01T00:00:00Z",
                    "matching_version": "<2.0",
                },
            ],
        }

        # When
        update_response = client.put(
            f"/eols/{self.eol_product_id}",
            headers=headers_with_api_key(USER1),
            json=update_request,
        )

        # Then
        assert update_response.status_code == 400
        assert (
            update_response.json()["detail"]
            == "Cannot update EoL product without specifying a 'version' when eol_product_id exists"
        )

    def test_raise_401_if_invalid_api_key(self):
        # Given
        invalid_headers = headers(USER1)
        invalid_headers["X-API-Key"] = "invalid"
        new_eol_product_id = uuid4()

        # When
        response = client.put(
            f"/eols/{new_eol_product_id}",
            headers=invalid_headers,
            json=self.request1,
        )

        # Then
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API Key"
