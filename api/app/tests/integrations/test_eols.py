from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
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

    def test_delete_unneeded_eol_version_on_eol_update(self, update_setup):
        # Given
        update_request = {
            "eol_versions": [
                {
                    "version": "3.0.0",
                    "release_date": "2021-01-02",
                    "eol_from": "2032-01-02",
                    "matching_version": "3.0.0",
                },
            ],
        }
        before_eol_product = self.response1_eol.json()

        # When
        after_eol_product = client.put(
            f"/eols/{self.eol_product_id}", headers=headers_with_api_key(USER1), json=update_request
        )

        # Then
        assert after_eol_product.status_code == 200
        assert (
            before_eol_product["eol_versions"][0]["version"]
            != after_eol_product.json()["eol_versions"][0]["version"]
        )
        assert (
            before_eol_product["eol_versions"][0]["release_date"]
            != after_eol_product.json()["eol_versions"][0]["release_date"]
        )
        assert (
            before_eol_product["eol_versions"][0]["eol_from"]
            != after_eol_product.json()["eol_versions"][0]["eol_from"]
        )
        assert (
            before_eol_product["eol_versions"][0]["matching_version"]
            != after_eol_product.json()["eol_versions"][0]["matching_version"]
        )

    def test_it_should_create_eol_dependency_when_ecosystem_matched(self, testdb: Session):
        # Given
        pteam1 = create_pteam(USER1, PTEAM1)

        service_name1 = "test_service1"
        upload_file_name = "trivy-ubuntu2004.cdx.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = sbom.read()

        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

        update_request = {
            "name": "ubuntu",
            "product_category": models.ProductCategoryEnum.OS,
            "description": "test_description",
            "is_ecosystem": True,
            "matching_name": "test_matching_name",
            "eol_versions": [
                {
                    "version": "20.04",
                    "release_date": "2020-04-23",
                    "eol_from": "2025-05-31",
                    "matching_version": "ubuntu-20.04",
                }
            ],
        }

        # When
        client.put(f"/eols/{uuid4()}", headers=headers_with_api_key(USER1), json=update_request)

        # Then
        ecosystem_eol_dependency_1 = testdb.scalars(select(models.EcosystemEoLDependency)).one()
        assert ecosystem_eol_dependency_1.service.service_name == service_name1
        assert ecosystem_eol_dependency_1.eol_version.version == "20.04"
        assert ecosystem_eol_dependency_1.eol_version.matching_version == "ubuntu-20.04"
        assert ecosystem_eol_dependency_1.eol_version.eol_product.name == "ubuntu"
        assert ecosystem_eol_dependency_1.eol_notification_sent is False

    def test_it_should_skip_eol_matching_when_no_change_in_request(self, mocker, update_setup):
        # Given
        same_request1 = {
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

        # When
        eol_matching = mocker.patch(
            "app.routers.eols.eol_business.fix_eol_dependency_by_eol_product"
        )
        client.put(
            f"/eols/{self.eol_product_id}", headers=headers_with_api_key(USER1), json=same_request1
        )

        # Then
        eol_matching.assert_not_called()

    @pytest.mark.parametrize(
        "test_request",
        [  # test1: changes EoLProduct
            {
                "name": "test_eol_product1",
                "product_category": models.ProductCategoryEnum.PACKAGE,
                "description": "test_description",
                "is_ecosystem": False,
                "matching_name": "test_matching_name1",
                "eol_versions": [
                    {
                        "version": "1.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2030-01-02",
                        "matching_version": "2.0.0",
                    },
                    {
                        "version": "2.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2030-01-02",
                        "matching_version": "2.0.0",
                    },
                ],
            },
            {  # test2: changes EoLVersion.eol_from
                "name": "test_eol_product",
                "product_category": models.ProductCategoryEnum.PACKAGE,
                "description": "test_description",
                "is_ecosystem": False,
                "matching_name": "test_matching_name",
                "eol_versions": [
                    {
                        "version": "1.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2030-01-02",
                        "matching_version": "2.0.0",
                    },
                    {
                        "version": "2.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2035-01-02",
                        "matching_version": "2.0.0",
                    },
                ],
            },
            {  # test3: changes the number of EoLVersion
                "name": "test_eol_product",
                "product_category": models.ProductCategoryEnum.PACKAGE,
                "description": "test_description",
                "is_ecosystem": False,
                "matching_name": "test_matching_name",
                "eol_versions": [
                    {
                        "version": "1.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2030-01-02",
                        "matching_version": "2.0.0",
                    },
                    {
                        "version": "2.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2035-01-02",
                        "matching_version": "2.0.0",
                    },
                    {
                        "version": "3.0.0",
                        "release_date": "2020-01-02",
                        "eol_from": "2036-01-02",
                        "matching_version": "3.0.0",
                    },
                ],
            },
        ],
    )
    def test_it_should_run_eol_matching_when_change_in_request(self, mocker, test_request):
        # Given
        request1 = {
            "name": "test_eol_product",
            "product_category": models.ProductCategoryEnum.PACKAGE,
            "description": "test_description",
            "is_ecosystem": False,
            "matching_name": "test_matching_name",
            "eol_versions": [
                {
                    "version": "1.0.0",
                    "release_date": "2020-01-02",
                    "eol_from": "2030-01-02",
                    "matching_version": "2.0.0",
                },
                {
                    "version": "2.0.0",
                    "release_date": "2020-01-02",
                    "eol_from": "2030-01-02",
                    "matching_version": "2.0.0",
                },
            ],
        }
        eol_product_id = uuid4()
        client.put(f"/eols/{eol_product_id}", headers=headers_with_api_key(USER1), json=request1)

        # When
        eol_matching = mocker.patch(
            "app.routers.eols.eol_business.fix_eol_dependency_by_eol_product"
        )
        client.put(
            f"/eols/{eol_product_id}", headers=headers_with_api_key(USER1), json=test_request
        )

        # Then
        eol_matching.assert_called_once()
