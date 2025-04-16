from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1
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
        self.request1: dict[str, Any] = {
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
        assert vuln is not None
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
        assert package is not None
        assert self.request1["vulnerable_packages"][0]["name"] == package.name
        assert self.request1["vulnerable_packages"][0]["ecosystem"] == package.ecosystem

    def test_update_vuln_if_given_vuln_id_is_exists(self, testdb: Session, update_setup):
        # Given
        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=self.request1
        )

        # Then
        vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln1.vuln_id))
        ).one_or_none()
        print(response.json()["detail"])
        assert response.status_code == 200
        assert vuln is not None
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

    def test_delete_unneeded_affect_on_vuln_update(self, testdb: Session, update_setup):
        # Given
        request: dict[str, Any] = {
            "vulnerable_packages": [
                {
                    "name": "example-lib2",
                    "ecosystem": "npm",
                    "affected_versions": ["<1.0.0"],
                    "fixed_versions": ["1.0.0"],
                }
            ],
        }

        # When
        response = client.put(f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=request)

        # Then
        vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln1.vuln_id))
        ).one_or_none()
        print(response.json()["detail"])
        assert response.status_code == 200
        assert vuln is not None
        assert self.affect1.affected_versions != vuln.affects[0].affected_versions
        assert self.affect1.fixed_versions != vuln.affects[0].fixed_versions

    def test_send_alert_if_vulnerabilities_are_found_when_updating_vuln(
        self, testdb: Session, mocker, update_setup
    ):
        # Given
        request = {
            "exploitation": "active",
            "automatable": "yes",
        }

        send_alert_to_pteam = mocker.patch("app.business.ticket_business.send_alert_to_pteam")

        # When
        response = client.put(f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=request)

        ## get ticket_id
        ticket = persistence.get_ticket_by_threat_id_and_dependency_id(
            testdb, self.threat1.threat_id, self.dependency1.dependency_id
        )

        if ticket is not None:
            alerts = testdb.scalars(
                select(models.Alert)
                .where(models.Alert.ticket_id == str(ticket.ticket_id))
                .order_by(models.Alert.alerted_at.desc())
            ).all()

        assert alerts is not None
        assert alerts[0].ticket.threat.vuln_id == str(self.vuln1.vuln_id)

        send_alert_to_pteam.assert_called_once()
        send_alert_to_pteam.assert_called_with(alerts[0])
