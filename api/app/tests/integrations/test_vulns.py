import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
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
                    "affected_name": "example-lib",
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
            created_at=datetime(2025, 4, 15, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 4, 15, 12, 0, 0, tzinfo=timezone.utc),
            cvss_v3_score=8.0,
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
            affected_versions=["<2.0.0"],
            fixed_versions=["2.0.0"],
            affected_name=self.package1.name,
            ecosystem=self.package1.ecosystem,
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
            name=self.request1["vulnerable_packages"][0]["affected_name"],
            ecosystem=self.request1["vulnerable_packages"][0]["ecosystem"],
        )
        testdb.add(new_package)
        testdb.commit()

        current_time = datetime.now(timezone.utc)

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
        assert str(self.user1.user_id) == vuln.created_by
        assert (
            self.request1["vulnerable_packages"][0]["affected_versions"]
            == vuln.affects[0].affected_versions
        )
        assert (
            self.request1["vulnerable_packages"][0]["fixed_versions"]
            == vuln.affects[0].fixed_versions
        )
        assert (
            current_time - timedelta(seconds=10)
            <= vuln.created_at
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= vuln.updated_at
            <= current_time + timedelta(seconds=10)
        )

    def test_not_create_package_if_given_vuln_id_is_new_and_package_does_not_exists(
        self, testdb: Session
    ):
        # Given
        new_vuln_id = uuid4()

        # When
        response = client.put(f"/vulns/{new_vuln_id}", headers=headers(USER1), json=self.request1)

        # Then
        package = testdb.scalars(
            select(models.Package).where(
                models.Package.name == self.request1["vulnerable_packages"][0]["affected_name"]
            )
        ).one_or_none()

        assert response.status_code == 200
        assert package is None

    def test_update_vuln_if_given_vuln_id_is_exists(self, testdb: Session, update_setup):
        # Given
        created_time = self.vuln1.created_at
        current_time = datetime.now(timezone.utc)

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=self.request1
        )

        # Then
        vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln1.vuln_id))
        ).one_or_none()

        assert response.status_code == 200
        assert vuln is not None
        assert self.request1["title"] == vuln.title
        assert self.request1["cve_id"] == vuln.cve_id
        assert self.request1["detail"] == vuln.detail
        assert self.request1["exploitation"] == vuln.exploitation
        assert self.request1["automatable"] == vuln.automatable
        assert self.request1["cvss_v3_score"] == vuln.cvss_v3_score
        assert str(self.user1.user_id) == vuln.created_by
        assert (
            self.request1["vulnerable_packages"][0]["affected_versions"]
            == vuln.affects[0].affected_versions
        )
        assert (
            self.request1["vulnerable_packages"][0]["fixed_versions"]
            == vuln.affects[0].fixed_versions
        )

        assert (
            created_time - timedelta(seconds=10)
            <= vuln.created_at
            <= created_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= vuln.updated_at
            <= current_time + timedelta(seconds=10)
        )

    def test_delete_unneeded_affect_on_vuln_update(self, testdb: Session, update_setup):
        # Given
        request: dict[str, Any] = {
            "vulnerable_packages": [
                {
                    "affected_name": "example-lib2",
                    "ecosystem": "npm",
                    "affected_versions": ["<1.0.0"],
                    "fixed_versions": ["1.0.0"],
                }
            ],
        }
        before_affected_versions = self.affect1.affected_versions
        before_fixed_versions = self.affect1.fixed_versions

        # When
        response = client.put(f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=request)

        # Then
        vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln1.vuln_id))
        ).one_or_none()

        assert response.status_code == 200
        assert vuln is not None
        assert before_affected_versions != vuln.affects[0].affected_versions
        assert before_fixed_versions != vuln.affects[0].fixed_versions

    def test_recalculate_ssvc_when_updating_vuln(self, testdb: Session, update_setup):
        # Given
        request = {
            "exploitation": "active",
            "automatable": "yes",
        }

        previous_ticket = copy.deepcopy(
            persistence.get_ticket_by_threat_id_and_dependency_id(
                testdb, self.threat1.threat_id, self.dependency1.dependency_id
            )
        )

        if previous_ticket is None:
            raise Exception("previous_ticket is None")

        # When
        response = client.put(f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=request)

        updated_ticket = persistence.get_ticket_by_id(testdb, previous_ticket.ticket_id)

        # Then
        ## previous_ssvc = scheduled,updated_ssvc = immediate
        assert response.status_code == 200
        assert previous_ticket is not None
        assert updated_ticket is not None
        assert previous_ticket.ssvc_deployer_priority != updated_ticket.ssvc_deployer_priority

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

        ticket = persistence.get_ticket_by_threat_id_and_dependency_id(
            testdb, self.threat1.threat_id, self.dependency1.dependency_id
        )

        if ticket is not None:
            alerts = testdb.scalars(
                select(models.Alert)
                .where(models.Alert.ticket_id == str(ticket.ticket_id))
                .order_by(models.Alert.alerted_at.desc())
            ).all()
        assert response.status_code == 200
        assert alerts is not None
        assert alerts[0].ticket.threat.vuln_id == str(self.vuln1.vuln_id)

        send_alert_to_pteam.assert_called_once()
        send_alert_to_pteam.assert_called_with(alerts[0])

    def test_create_ticket_if_vulnerabilities_matched_by_source_name_when_updating_vuln(
        self, testdb: Session
    ):
        # Given
        pteam1 = create_pteam(USER1, PTEAM1)

        service_name1 = "test_service1"
        upload_file_name = "trivy-ubuntu2004.cdx.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

        # source_name in purl:
        #   "pkg:deb/ubuntu/gcc-10-base@10.5.0-1ubuntu1~20.04?arch=arm64&distro=ubuntu-20.04"
        source_name = "gcc-10"

        request1: dict[str, Any] = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "affected_name": source_name,
                    "ecosystem": "ubuntu-20.04",
                    "affected_versions": ["<=10.5.0-1ubuntu1~20.040"],
                    "fixed_versions": ["10.5.0-1ubuntu2~20.040"],
                }
            ],
        }

        # When
        vuln_id = str(uuid4())
        client.put(f"/vulns/{vuln_id}", headers=headers(USER1), json=request1)

        tickets = testdb.scalars(select(models.Ticket)).all()
        assert len(tickets) == 3
