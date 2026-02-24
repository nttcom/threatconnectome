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
from app.tests.medium.constants import PTEAM1, USER1, USER2
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    headers_with_api_key,
)

client = TestClient(app)


class TestGetEolProductsWithPteamId:
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
            "name": "ubuntu",
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
        self.service_name1 = "test_service1"
        upload_file_name1 = "trivy-ubuntu2004.cdx.json"
        sbom_file1 = (
            Path(__file__).resolve().parent.parent.parent
            / "common"
            / "upload_test"
            / upload_file_name1
        )
        with open(sbom_file1, "r") as sbom:
            sbom_json1 = sbom.read()

        bg_create_tags_from_sbom_json(
            sbom_json1, self.pteam1.pteam_id, self.service_name1, upload_file_name1
        )

        # Add package data to match with self.eol_product_3_request
        self.service_name2 = "test_service2"
        upload_file_name2 = "test_trivy_cyclonedx_axios.json"
        sbom_file2 = (
            Path(__file__).resolve().parent.parent.parent
            / "common"
            / "upload_test"
            / upload_file_name2
        )
        with open(sbom_file2, "r") as sbom:
            sbom_json2 = sbom.read()

        bg_create_tags_from_sbom_json(
            sbom_json2, self.pteam1.pteam_id, self.service_name2, upload_file_name2
        )

    def test_get_eol_products_associated_with_pteam_id(self):
        # When
        response = client.get(f"/pteams/{self.pteam1.pteam_id}/eols", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["products"]) == 2

        for product in data["products"]:
            if product["name"] == "ubuntu":
                assert product["eol_product_id"] == str(self.eol_product_id_2)
                assert product["name"] == self.eol_product_2_request["name"]
                assert product["product_category"] == self.eol_product_2_request["product_category"]
                assert product["description"] == self.eol_product_2_request["description"]
                assert product["is_ecosystem"] == self.eol_product_2_request["is_ecosystem"]
                assert product["matching_name"] == self.eol_product_2_request["matching_name"]
                assert (
                    product["eol_versions"][0]["version"]
                    == self.eol_product_2_request["eol_versions"][0]["version"]
                )
                assert (
                    product["eol_versions"][0]["release_date"]
                    == self.eol_product_2_request["eol_versions"][0]["release_date"]
                )
                assert (
                    product["eol_versions"][0]["eol_from"]
                    == self.eol_product_2_request["eol_versions"][0]["eol_from"]
                )
                assert (
                    product["eol_versions"][0]["matching_version"]
                    == self.eol_product_2_request["eol_versions"][0]["matching_version"]
                )
                assert (
                    self.current_time - timedelta(seconds=10)
                    <= datetime.fromisoformat(
                        product["eol_versions"][0]["created_at"].replace("Z", "+00:00")
                    )
                    <= self.current_time + timedelta(seconds=10)
                )
                assert (
                    self.current_time - timedelta(seconds=10)
                    <= datetime.fromisoformat(
                        product["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
                    )
                    <= self.current_time + timedelta(seconds=10)
                )
                assert (
                    product["eol_versions"][0]["services"][0]["service_name"] == self.service_name1
                )

            if product["name"] == "product_3":
                assert product["eol_product_id"] == str(self.eol_product_id_3)
                assert product["name"] == self.eol_product_3_request["name"]
                assert product["product_category"] == self.eol_product_3_request["product_category"]
                assert product["description"] == self.eol_product_3_request["description"]
                assert product["is_ecosystem"] == self.eol_product_3_request["is_ecosystem"]
                assert product["matching_name"] == self.eol_product_3_request["matching_name"]
                assert (
                    product["eol_versions"][0]["version"]
                    == self.eol_product_3_request["eol_versions"][0]["version"]
                )
                assert (
                    product["eol_versions"][0]["release_date"]
                    == self.eol_product_3_request["eol_versions"][0]["release_date"]
                )
                assert (
                    product["eol_versions"][0]["eol_from"]
                    == self.eol_product_3_request["eol_versions"][0]["eol_from"]
                )
                assert (
                    product["eol_versions"][0]["matching_version"]
                    == self.eol_product_3_request["eol_versions"][0]["matching_version"]
                )
                assert (
                    self.current_time - timedelta(seconds=10)
                    <= datetime.fromisoformat(
                        product["eol_versions"][0]["created_at"].replace("Z", "+00:00")
                    )
                    <= self.current_time + timedelta(seconds=10)
                )
                assert (
                    self.current_time - timedelta(seconds=10)
                    <= datetime.fromisoformat(
                        product["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
                    )
                    <= self.current_time + timedelta(seconds=10)
                )
                assert (
                    product["eol_versions"][0]["services"][0]["service_name"] == self.service_name2
                )

    def test_return_404_when_pteam_id_does_not_exist(self):
        # Given
        non_existing_pteam_id = uuid4()

        # When
        response = client.get(f"/pteams/{non_existing_pteam_id}/eols", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_return_404_when_not_pteam_member(self):
        # Given
        create_user(USER2)
        # When
        response = client.get(f"/pteams/{self.pteam1.pteam_id}/eols", headers=headers(USER2))

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"
