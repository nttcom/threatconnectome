from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.constants import (
    USER1,
)
from app.tests.medium.utils import (
    create_user,
    headers,
)

client = TestClient(app)


class TestUpdateVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        self.user1 = create_user(USER1)
        self.request1 = {
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

    def test_create_vuln_and_affect_if_given_vuln_id_is_new_and_package_exists(
        self, testdb: Session
    ):
        # Given
        new_vuln_id = uuid4()
        new_package = models.Package(
            name=self.request1["vulnerable_packages"][0]["name"],
            ecosystem=self.request1["vulnerable_packages"][0]["ecosystem"],
        )
        testdb.add(new_package)
        testdb.commit()

        # When
        response = client.put(f"/vulns/{new_vuln_id}", headers=headers(USER1), json=self.request1)

        # Then
        vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(new_vuln_id))
        ).one_or_none()

        assert response.status_code == 200
        assert self.request1["title"] == vuln.title
        assert self.request1["cve_id"] == vuln.cve_id
        assert self.request1["detail"] == vuln.detail
        assert self.request1["exploitation"] == vuln.exploitation
        assert self.request1["automatable"] == vuln.automatable
        assert self.request1["cvss_v3_score"] == vuln.cvss_v3_score
        assert (
            self.request1["vulnerable_packages"][0]["affected_versions"]
            == vuln.affects[0].affected_versions
        )
        assert (
            self.request1["vulnerable_packages"][0]["fixed_versions"]
            == vuln.affects[0].fixed_versions
        )

    def test_create_package_if_given_vuln_id_is_new_and_package_does_not_exists(
        self, testdb: Session
    ):
        # Given
        new_vuln_id = uuid4()

        # When
        response = client.put(f"/vulns/{new_vuln_id}", headers=headers(USER1), json=self.request1)

        # Then
        package = testdb.scalars(
            select(models.Package).where(
                models.Package.name == self.request1["vulnerable_packages"][0]["name"]
            )
        ).one_or_none()
        assert response.status_code == 200
        assert self.request1["vulnerable_packages"][0]["name"] == package.name
        assert self.request1["vulnerable_packages"][0]["ecosystem"] == package.ecosystem
