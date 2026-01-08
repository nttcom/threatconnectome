from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.tests.medium.constants import USER1
from app.tests.medium.utils import (
    create_user,
    headers,
    headers_with_api_key,
)

client = TestClient(app)


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
