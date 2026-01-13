from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import PTEAM1, USER1
from app.tests.medium.utils import (
    create_pteam,
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
        ],
    )
    def test_raise_400_when_create_if_field_with_none(self, field_name):
        # Given
        new_eol_product_id = uuid4()
        request = self.request1.copy()
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
        ],
    )
    def test_raise_400_when_update_if_field_with_none(self, update_setup, field_name):
        # Given
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

    @pytest.mark.parametrize(
        "field_name",
        [
            "name",
            "product_category",
            "is_ecosystem",
            "matching_name",
        ],
    )
    def test_raise_400_when_create_if_nothing_is_specified_in_the_request(self, field_name):
        # Given
        new_eol_product_id = uuid4()
        request = self.request1.copy()
        del request[f"{field_name}"]

        # When
        response = client.put(
            f"/eols/{new_eol_product_id}", headers=headers_with_api_key(USER1), json=request
        )

        # Then
        assert response.status_code == 400
        expected_message = (
            "'name' and 'product_category' and 'is_ecosystem' and 'matching_name' "
            "are required when creating a eol."
        )
        assert response.json()["detail"] == expected_message

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


class TestGetEolProducts:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

        # Create EoL products
        self.eol_product_id_1 = uuid4()
        self.eol_product_1_request: dict[str, Any] = {
            "name": "product_1",
            "product_category": models.ProductCategoryEnum.PACKAGE,
            "description": "product 1 description",
            "is_ecosystem": False,
            "matching_name": "product_1",
            "eol_versions": [
                {
                    "version": "1.0.0",
                    "release_date": "2020-01-01",
                    "eol_from": "2025-01-01",
                    "matching_version": "1.0.0",
                },
                {
                    "version": "2.0.0",
                    "release_date": "2022-01-01",
                    "eol_from": "2030-01-01",
                    "matching_version": "2.0.0",
                },
            ],
        }

        self.eol_product_id_2 = uuid4()
        self.eol_product_2_request: dict[str, Any] = {
            "name": "product_2",
            "product_category": models.ProductCategoryEnum.RUNTIME,
            "description": "product 2 description",
            "is_ecosystem": True,
            "matching_name": "product_2",
            "eol_versions": [
                {
                    "version": "20.04",
                    "release_date": "2021-01-01",
                    "eol_from": "2026-01-01",
                    "matching_version": "ubuntu-20.04",
                }
            ],
        }

        self.eol_product_id_3 = uuid4()
        self.eol_product_3_request: dict[str, Any] = {
            "name": "product_3",
            "product_category": models.ProductCategoryEnum.PACKAGE,
            "description": "product 3 description",
            "is_ecosystem": False,
            "matching_name": "axios",
            "eol_versions": [
                {
                    "version": "1.6.7",
                    "release_date": "2019-01-01",
                    "eol_from": "2024-01-01",
                    "matching_version": "1.6.7",
                }
            ],
        }

        self.current_time = datetime.now(timezone.utc)
        client.put(
            f"/eols/{self.eol_product_id_1}",
            headers=headers_with_api_key(USER1),
            json=self.eol_product_1_request,
        )
        client.put(
            f"/eols/{self.eol_product_id_2}",
            headers=headers_with_api_key(USER1),
            json=self.eol_product_2_request,
        )
        client.put(
            f"/eols/{self.eol_product_id_3}",
            headers=headers_with_api_key(USER1),
            json=self.eol_product_3_request,
        )

        # Add package data to match with self.eol_product_2_request
        service_name1 = "test_service1"
        upload_file_name1 = "trivy-ubuntu2004.cdx.json"
        sbom_file1 = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name1
        )
        with open(sbom_file1, "r") as sbom:
            sbom_json1 = sbom.read()

        bg_create_tags_from_sbom_json(
            sbom_json1, self.pteam1.pteam_id, service_name1, upload_file_name1
        )

        # Add package data to match with self.eol_product_3_request
        service_name2 = "test_service2"
        upload_file_name2 = "test_trivy_cyclonedx_axios.json"
        sbom_file2 = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name2
        )
        with open(sbom_file2, "r") as sbom:
            sbom_json2 = sbom.read()

        bg_create_tags_from_sbom_json(
            sbom_json2, self.pteam1.pteam_id, service_name2, upload_file_name2
        )

    def test_get_all_eol_products(self):
        # When: Get all products without filters
        response = client.get("/eols", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["products"]) == 3

        # Verify product structure
        product_names = {p["name"] for p in data["products"]}
        assert "product_1" in product_names
        assert "product_2" in product_names
        assert "product_3" in product_names

        # Verify eol_versions are included
        for product in data["products"]:
            assert "eol_versions" in product
            if product["name"] == "product_1":
                assert len(product["eol_versions"]) == 2
            elif product["name"] == "product_2":
                assert len(product["eol_versions"]) == 1
            elif product["name"] == "product_3":
                assert len(product["eol_versions"]) == 1

    def test_get_eol_products_filtered_by_pteam_id(self):
        # When: Filter by pteam_id
        response = client.get(f"/eols?pteam_id={self.pteam1.pteam_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["products"]) == 2

        product_names = {p["name"] for p in data["products"]}
        assert "product_2" in product_names  # linked via EcosystemEoLDependency
        assert "product_3" in product_names  # linked via PackageEoLDependency

    def test_get_eol_products_filtered_by_eol_product_id(self):
        # When: Filter by eol_product_id
        response = client.get(
            f"/eols?eol_product_id={self.eol_product_id_1}", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["products"]) == 1
        assert len(data["products"][0]["eol_versions"]) == 2
        assert data["products"][0]["eol_product_id"] == str(self.eol_product_id_1)
        assert data["products"][0]["name"] == self.eol_product_1_request["name"]
        assert (
            data["products"][0]["product_category"]
            == self.eol_product_1_request["product_category"]
        )
        assert data["products"][0]["description"] == self.eol_product_1_request["description"]
        assert data["products"][0]["is_ecosystem"] == self.eol_product_1_request["is_ecosystem"]
        assert data["products"][0]["matching_name"] == self.eol_product_1_request["matching_name"]

        assert data["products"][0]["eol_versions"][0]["version"] in [
            eol_version["version"] for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][0]["release_date"] in [
            eol_version["release_date"]
            for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][0]["eol_from"] in [
            eol_version["eol_from"] for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][0]["matching_version"] in [
            eol_version["matching_version"]
            for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["created_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )
        assert data["products"][0]["eol_versions"][1]["version"] in [
            eol_version["version"] for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][1]["release_date"] in [
            eol_version["release_date"]
            for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][1]["eol_from"] in [
            eol_version["eol_from"] for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert data["products"][0]["eol_versions"][1]["matching_version"] in [
            eol_version["matching_version"]
            for eol_version in self.eol_product_1_request["eol_versions"]
        ]
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][1]["created_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][1]["updated_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )

    def test_get_eol_products_filtered_by_both_pteam_id_and_eol_product_id(self):
        # When: Filter by both pteam_id and eol_product_id (product_2 is linked to pteam1)
        response = client.get(
            f"/eols?pteam_id={self.pteam1.pteam_id}&eol_product_id={self.eol_product_id_2}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["products"]) == 1
        assert data["products"][0]["eol_product_id"] == str(self.eol_product_id_2)
        assert data["products"][0]["name"] == self.eol_product_2_request["name"]
        assert (
            data["products"][0]["product_category"]
            == self.eol_product_2_request["product_category"]
        )
        assert data["products"][0]["description"] == self.eol_product_2_request["description"]
        assert data["products"][0]["is_ecosystem"] == self.eol_product_2_request["is_ecosystem"]
        assert data["products"][0]["matching_name"] == self.eol_product_2_request["matching_name"]

        assert (
            data["products"][0]["eol_versions"][0]["version"]
            == self.eol_product_2_request["eol_versions"][0]["version"]
        )
        assert (
            data["products"][0]["eol_versions"][0]["release_date"]
            == self.eol_product_2_request["eol_versions"][0]["release_date"]
        )
        assert (
            data["products"][0]["eol_versions"][0]["eol_from"]
            == self.eol_product_2_request["eol_versions"][0]["eol_from"]
        )
        assert (
            data["products"][0]["eol_versions"][0]["matching_version"]
            == self.eol_product_2_request["eol_versions"][0]["matching_version"]
        )
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["created_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )
        assert (
            self.current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= self.current_time + timedelta(seconds=10)
        )

    def test_get_eol_products_no_match_for_pteam_and_product_combination(self):
        # When: Filter by pteam_id and eol_product_id that don't match
        # (product_1 is not linked to pteam1)
        response = client.get(
            f"/eols?pteam_id={self.pteam1.pteam_id}&eol_product_id={self.eol_product_id_1}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["products"]) == 0

    def test_return_404_when_pteam_id_does_not_exist(self):
        # Given
        non_existing_pteam_id = uuid4()

        # When
        response = client.get(f"/eols?pteam_id={non_existing_pteam_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_return_404_when_eol_product_id_does_not_exist(self):
        # Given
        non_existing_eol_product_id = uuid4()

        # When
        response = client.get(
            f"/eols?eol_product_id={non_existing_eol_product_id}", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such eol"


class TestDeleteEol:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        self.user1 = create_user(USER1)
        self.new_eol_product_id = uuid4()
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

        # Create a eol to delete
        client.put(
            f"/eols/{self.new_eol_product_id}",
            headers=headers_with_api_key(USER1),
            json=self.request1,
        )

    def test_it_should_delete_eol_when_eol_product_id_exists(self, testdb: Session):
        # When
        response = client.delete(
            f"/eols/{self.new_eol_product_id}", headers=headers_with_api_key(USER1)
        )

        # Then
        assert response.status_code == 204
        get_response = client.get(
            f"/eols?eol_product_id={self.new_eol_product_id}", headers=headers(USER1)
        )
        assert get_response.status_code == 404
        assert get_response.json()["detail"] == "No such eol"

    def test_it_should_return_404_when_eol_product_id_does_not_exist(self):
        # Given
        non_existing_eol_product_id = uuid4()

        # When
        response = client.delete(
            f"/eols/{non_existing_eol_product_id}", headers=headers_with_api_key(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such eol"

    def test_raise_401_if_invalid_api_key(self):
        # Given
        invalid_headers = headers(USER1)
        invalid_headers["X-API-Key"] = "invalid"

        # When
        response = client.delete(f"/eols/{self.new_eol_product_id}", headers=invalid_headers)

        # Then
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API Key"
