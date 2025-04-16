from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1, USER2
from app.tests.medium.utils import (
    create_pteam,
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

    @pytest.fixture(scope="function", autouse=False)
    def update_setup(self, testdb: Session):
        self.pteam1 = create_pteam(USER1, PTEAM1)

        self.service1 = models.Service(
            service_name="Service1 name",
            pteam_id=str(self.pteam1.pteam_id),
        )
        testdb.add(self.service1)

        self.vuln1 = models.Vuln(
            vuln_id=str(uuid4()),
            title="Vuln1 title",
            detail="Vuln1 detail",
            cve_id="CVE-0000-0001",
            created_by=str(self.user1.user_id),
            created_at=datetime(2025, 4, 15, 12, 0, 0),
            updated_at=datetime(2025, 4, 15, 12, 0, 0),
            cvss_v3_score=8.0,
            content_fingerprint="dummy_fingerprint",
            exploitation="none",
            automatable="no",
        )

        testdb.add(self.vuln1)

        self.package1 = models.Package(
            name="Package1 name",
            ecosystem="npm",
        )

        testdb.add(self.package1)

        self.package_version1 = models.PackageVersion(
            package_id=self.package1.package_id,
            version="1.0.0",
        )

        testdb.add(self.package_version1)

        self.dependency1 = models.Dependency(
            target="dependency1 target",
            package_manager="npm",
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )
        testdb.add(self.dependency1)

        self.affect1 = models.Affect(
            vuln_id=self.vuln1.vuln_id,
            package_id=self.package1.package_id,
            affected_versions=["<2.0.0"],
            fixed_versions=["2.0.0"],
        )

        testdb.add(self.affect1)

        self.threat1 = models.Threat(
            package_version_id=self.package_version1.package_version_id, vuln_id=self.vuln1.vuln_id
        )

        persistence.create_threat(testdb, self.threat1)

        ticket_business.fix_ticket_by_threat(testdb, self.threat1)

    def test_raise_400_if_given_vuln_id_is_default_vuln_id(self):
        # Given
        default_vuln_id = UUID(int=0)

        # When
        response = client.put(
            f"/vulns/{default_vuln_id}", headers=headers(USER1), json=self.request1
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot create default vuln"

    def test_raise_400_if_requested_title_is_None(self):
        # Given
        new_vuln_id = uuid4()
        title_none_request = {
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
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=title_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_requested_detail_is_None(self):
        # Given
        new_vuln_id = uuid4()
        detail_none_request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
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
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=detail_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_cvss_v3_score_is_out_of_range(self):
        # Given
        new_vuln_id = uuid4()
        out_of_range_cvss_request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 9999.9999,
            "vulnerable_packages": [
                {
                    "name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=out_of_range_cvss_request
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"

    def test_raise_403_if_current_user_is_not_vuln_creator(self, testdb: Session, update_setup):
        # Given
        create_user(USER2)

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER2), json=self.request1
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "You are not vuln creator"

    @pytest.mark.parametrize(
        "field_name",
        [
            "title",
            "detail",
            "cve_id",
            "exploitation",
            "automatable",
            "cvss_v3_score",
        ],
    )
    def test_raise_400_if_field_update_with_none(self, testdb: Session, update_setup, field_name):
        # Given
        invalid_request: dict[str, Any] = {
            f"{field_name}": None,
        }

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=invalid_request
        )

        assert response.status_code == 400
        assert response.json()["detail"] == f"Cannot specify None for {field_name}"

    def test_raise_400_if_cvss_v3_score_update_with_out_of_range(
        self, testdb: Session, update_setup
    ):
        # Given
        invalid_request: dict[str, Any] = {
            "cvss_v3_score": 9999.9999,
        }

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=invalid_request
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"


class TestGetVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # Given
        self.user1 = create_user(USER1)
        self.new_vuln_id = uuid4()
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

        client.put(f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=self.request1)

    def test_it_should_return_200_when_vuln_id_is_correctly_registered(self):
        # When
        response = client.get(f"/vulns/{self.new_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        assert response.json()["vuln_id"] == str(self.new_vuln_id)
        assert response.json()["title"] == self.request1["title"]
        assert response.json()["cve_id"] == self.request1["cve_id"]
        assert response.json()["detail"] == self.request1["detail"]
        assert response.json()["exploitation"] == self.request1["exploitation"]
        assert response.json()["automatable"] == self.request1["automatable"]
        assert response.json()["cvss_v3_score"] == self.request1["cvss_v3_score"]
        assert (
            response.json()["vulnerable_packages"][0]["name"]
            == self.request1["vulnerable_packages"][0]["name"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["ecosystem"]
            == self.request1["vulnerable_packages"][0]["ecosystem"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["affected_versions"]
            == self.request1["vulnerable_packages"][0]["affected_versions"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["fixed_versions"]
            == self.request1["vulnerable_packages"][0]["fixed_versions"]
        )

    def test_it_should_return_400_when_vuln_id_is_not_registered(self):
        # Given
        not_registered_vuln_id = str(uuid4())

        # When
        response = client.get(f"/vulns/{not_registered_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such vuln"
