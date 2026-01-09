from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    headers_with_api_key,
)

client = TestClient(app)


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
                    "version": "3.0.0",
                    "release_date": "2021-01-01",
                    "eol_from": "2026-01-01",
                    "matching_version": "3.0.0",
                }
            ],
        }

        self.eol_product_id_3 = uuid4()
        self.eol_product_3_request: dict[str, Any] = {
            "name": "product_3",
            "product_category": models.ProductCategoryEnum.PACKAGE,
            "description": "product 3 description",
            "is_ecosystem": False,
            "matching_name": "product_3",
            "eol_versions": [
                {
                    "version": "4.0.0",
                    "release_date": "2019-01-01",
                    "eol_from": "2024-01-01",
                    "matching_version": "4.0.0",
                }
            ],
        }

        # Todo: After creating the PUT API, modify the API.
        eol_product_1 = models.EoLProduct(
            eol_product_id=str(self.eol_product_id_1),
            name=self.eol_product_1_request["name"],
            product_category=self.eol_product_1_request["product_category"],
            description=self.eol_product_1_request["description"],
            is_ecosystem=self.eol_product_1_request["is_ecosystem"],
            matching_name=self.eol_product_1_request["matching_name"],
        )
        persistence.create_eol_product(testdb, eol_product_1)

        eol_product_2 = models.EoLProduct(
            eol_product_id=str(self.eol_product_id_2),
            name=self.eol_product_2_request["name"],
            product_category=self.eol_product_2_request["product_category"],
            description=self.eol_product_2_request["description"],
            is_ecosystem=self.eol_product_2_request["is_ecosystem"],
            matching_name=self.eol_product_2_request["matching_name"],
        )
        persistence.create_eol_product(testdb, eol_product_2)

        eol_product_3 = models.EoLProduct(
            eol_product_id=str(self.eol_product_id_3),
            name=self.eol_product_3_request["name"],
            product_category=self.eol_product_3_request["product_category"],
            description=self.eol_product_3_request["description"],
            is_ecosystem=self.eol_product_3_request["is_ecosystem"],
            matching_name=self.eol_product_3_request["matching_name"],
        )
        persistence.create_eol_product(testdb, eol_product_3)

        # Create EoL versions for product 1
        now = datetime.now(timezone.utc)
        self.eol_version_1_1 = models.EoLVersion(
            eol_product_id=str(self.eol_product_id_1),
            version=self.eol_product_1_request["eol_versions"][0]["version"],
            release_date=date.fromisoformat(
                self.eol_product_1_request["eol_versions"][0]["release_date"]
            ),
            eol_from=date.fromisoformat(self.eol_product_1_request["eol_versions"][0]["eol_from"]),
            matching_version=self.eol_product_1_request["eol_versions"][0]["matching_version"],
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(testdb, self.eol_version_1_1)

        self.eol_version_1_2 = models.EoLVersion(
            eol_product_id=str(self.eol_product_id_1),
            version=self.eol_product_1_request["eol_versions"][1]["version"],
            release_date=date.fromisoformat(
                self.eol_product_1_request["eol_versions"][1]["release_date"]
            ),
            eol_from=date.fromisoformat(self.eol_product_1_request["eol_versions"][1]["eol_from"]),
            matching_version=self.eol_product_1_request["eol_versions"][1]["matching_version"],
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(testdb, self.eol_version_1_2)

        # Create EoL versions for product 2
        self.eol_version_2_1 = models.EoLVersion(
            eol_product_id=str(self.eol_product_id_2),
            version=self.eol_product_2_request["eol_versions"][0]["version"],
            release_date=date.fromisoformat(
                self.eol_product_2_request["eol_versions"][0]["release_date"]
            ),
            eol_from=date.fromisoformat(self.eol_product_2_request["eol_versions"][0]["eol_from"]),
            matching_version=self.eol_product_2_request["eol_versions"][0]["matching_version"],
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(testdb, self.eol_version_2_1)

        # Create EoL versions for product 3
        self.eol_version_3_1 = models.EoLVersion(
            eol_product_id=str(self.eol_product_id_3),
            version=self.eol_product_3_request["eol_versions"][0]["version"],
            release_date=date.fromisoformat(
                self.eol_product_3_request["eol_versions"][0]["release_date"]
            ),
            eol_from=date.fromisoformat(self.eol_product_3_request["eol_versions"][0]["eol_from"]),
            matching_version=self.eol_product_3_request["eol_versions"][0]["matching_version"],
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(testdb, self.eol_version_3_1)

        # Create Service for pteam1
        self.service1 = models.Service(
            pteam_id=str(self.pteam1.pteam_id),
            service_name="test_service",
        )
        testdb.add(self.service1)
        testdb.flush()

        # Create EcosystemEoLDependency to link service to eol_version (product 2)
        ecosystem_dependency = models.EcosystemEoLDependency(
            service_id=self.service1.service_id,
            eol_version_id=str(self.eol_version_2_1.eol_version_id),
        )
        testdb.add(ecosystem_dependency)

        # Create Package, PackageVersion, Dependency and PackageEoLDependency to link to product 3
        self.package1 = models.Package(
            name="test_package",
            ecosystem="npm",
        )
        persistence.create_package(testdb, self.package1)

        self.package_version1 = models.PackageVersion(
            package_id=self.package1.package_id,
            version="1.0.0",
        )
        persistence.create_package_version(testdb, self.package_version1)

        self.dependency1 = models.Dependency(
            target="test_target",
            package_manager="npm",
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )
        testdb.add(self.dependency1)
        testdb.flush()

        # Create PackageEoLDependency to link dependency to eol_version (product 3)
        package_eol_dependency = models.PackageEoLDependency(
            dependency_id=self.dependency1.dependency_id,
            eol_version_id=str(self.eol_version_3_1.eol_version_id),
        )
        testdb.add(package_eol_dependency)

        testdb.commit()

    def test_get_all_eol_products(self):
        # When: Get all products without filters
        response = client.get("/eols/eol", headers=headers(USER1))

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
        response = client.get(f"/eols/eol?pteam_id={self.pteam1.pteam_id}", headers=headers(USER1))

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
            f"/eols/eol?eol_product_id={self.eol_product_id_1}", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        current_time = datetime.now(timezone.utc)
        print(type(data["products"][0]["eol_versions"][0]["release_date"]))
        print(type(self.eol_product_1_request["eol_versions"][0]["release_date"]))
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
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["created_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
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
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][1]["created_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][1]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )

    def test_get_eol_products_filtered_by_both_pteam_id_and_eol_product_id(self):
        # When: Filter by both pteam_id and eol_product_id (product_2 is linked to pteam1)
        response = client.get(
            f"/eols/eol?pteam_id={self.pteam1.pteam_id}&eol_product_id={self.eol_product_id_2}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        current_time = datetime.now(timezone.utc)
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
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["created_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(
                data["products"][0]["eol_versions"][0]["updated_at"].replace("Z", "+00:00")
            )
            <= current_time + timedelta(seconds=10)
        )

    def test_get_eol_products_no_match_for_pteam_and_product_combination(self):
        # When: Filter by pteam_id and eol_product_id that don't match
        # (product_1 is not linked to pteam1)
        response = client.get(
            f"/eols/eol?pteam_id={self.pteam1.pteam_id}&eol_product_id={self.eol_product_id_1}",
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
        response = client.get(f"/eols/eol?pteam_id={non_existing_pteam_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_return_404_when_eol_product_id_does_not_exist(self):
        # Given
        non_existing_eol_product_id = uuid4()

        # When
        response = client.get(
            f"/eols/eol?eol_product_id={non_existing_eol_product_id}", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such eol"


class TestDeleteEol:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        self.user1 = create_user(USER1)
        # Todo: After creating the PUT API, modify the API.
        self.new_eol_product_id = uuid4()
        eol_product = models.EoLProduct(
            eol_product_id=str(self.new_eol_product_id),
            name="test_eol_product",
            product_category=models.ProductCategoryEnum.PACKAGE,
            description="test_description",
            is_ecosystem=False,
            matching_name="test_matching_name",
        )

        persistence.create_eol_product(testdb, eol_product)

        now = datetime.now(timezone.utc)
        eol_version_model = models.EoLVersion(
            eol_product_id=str(self.new_eol_product_id),
            version="2.0.0",
            release_date=date.fromisoformat("2020-01-02"),
            eol_from=date.fromisoformat("2030-01-02"),
            matching_version="2.0.0",
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(testdb, eol_version_model)
        testdb.commit()
        # self.request1 = {
        #     "name": "test_eol_product",
        #     "product_category": models.ProductCategoryEnum.PACKAGE,
        #     "description": "test_description",
        #     "is_ecosystem": False,
        #     "matching_name": "test_matching_name",
        #     "eol_versions": [
        #         {
        #             "version": "2.0.0",
        #             "release_date": "2020-01-02",
        #             "eol_from": "2030-01-02",
        #             "matching_version": "2.0.0",
        #         }
        #     ],
        # }

        # # Create a eol to delete
        # client.put(
        #     f"/eols/{self.new_eol_product_id}",
        #     headers=headers_with_api_key(USER1),
        #     json=self.request1,
        # )

    def test_it_should_delete_eol_when_eol_product_id_exists(self, testdb: Session):
        # When
        response = client.delete(
            f"/eols/{self.new_eol_product_id}", headers=headers_with_api_key(USER1)
        )

        # Then
        assert response.status_code == 204
        # Todo: After creating the GET API, modify the API.
        eol_product = testdb.scalars(
            select(models.EoLProduct).where(
                models.EoLProduct.eol_product_id == str(self.new_eol_product_id)
            )
        ).one_or_none()
        assert eol_product is None
        # get_response = client.get(f"/eols/{self.new_eol_product_id}", headers=headers(USER1))
        # assert get_response.status_code == 404  # Not Found
        # assert get_response.json()["detail"] == "No such eol"

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
