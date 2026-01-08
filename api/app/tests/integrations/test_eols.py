from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.tests.medium.constants import USER1
from app.tests.medium.utils import (
    create_user,
    headers_with_api_key,
)

client = TestClient(app)


class TestUpdateVuln:
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
