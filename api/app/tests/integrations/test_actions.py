import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import PTEAM1, USER1, VULN1
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
)

client = TestClient(app)


class TestCreateAction:

    def test_action_is_created_when_request_is_successful(self, testdb: Session):
        # Given
        create_user(USER1)
        # Create a vuln
        create_vuln(USER1, VULN1)
        action_create_request = {
            "vuln_id": str(VULN1["vuln_id"]),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # When
        client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        action = testdb.scalars(
            select(models.VulnAction).where(models.VulnAction.vuln_id == VULN1["vuln_id"])
        ).one_or_none()

        assert action is not None
        assert action.action == action_create_request["action"]
        assert action.action_type == action_create_request["action_type"]
        assert action.recommended == action_create_request["recommended"]

    def test_vuln_action_triggers_ticket_creation(self, testdb: Session):
        # Given
        create_user(USER1)

        ## If fixed_versions is not provided, a ticket will not be created without a vuln_action.
        no_fixed_versions_vuln_id = uuid4()
        no_fixed_versions_vuln_request: dict[str, Any] = {
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
                    "fixed_versions": [],
                }
            ],
        }

        client.put(
            f"/vulns/{no_fixed_versions_vuln_id}",
            headers=headers(USER1),
            json=no_fixed_versions_vuln_request,
        )

        pteam1 = create_pteam(USER1, PTEAM1)

        service1 = models.Service(
            service_name="Service1 name",
            pteam_id=str(pteam1.pteam_id),
        )

        testdb.add(service1)

        package1 = persistence.get_package_by_name_and_ecosystem(
            testdb,
            str(no_fixed_versions_vuln_request["vulnerable_packages"][0]["name"]),
            str(no_fixed_versions_vuln_request["vulnerable_packages"][0]["ecosystem"]),
        )

        if package1 is None:
            raise Exception("package1 is None")

        package_version = models.PackageVersion(
            package_id=package1.package_id,
            version="1.0.0",
        )

        persistence.create_package_version(testdb, package_version)

        threat1 = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=no_fixed_versions_vuln_id
        )

        persistence.create_threat(testdb, threat1)

        dependency1 = models.Dependency(
            service_id=str(service1.service_id),
            package_version_id=package_version.package_version_id,
            package_manager="npm",
            target="dependency1 target",
        )

        testdb.add(dependency1)
        testdb.commit()

        # When
        action_create_request = {
            "vuln_id": str(no_fixed_versions_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }
        client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        ticket = persistence.get_ticket_by_threat_id_and_dependency_id(
            testdb,
            threat1.threat_id,
            dependency1.dependency_id,
        )

        assert ticket is not None


class TestUpdateAction:

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        self.vuln_id = VULN1["vuln_id"]
        create_vuln(USER1, VULN1)

        # Create an action
        action_create_request = {
            "vuln_id": str(self.vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        self.action_id = response.json()["action_id"]

    def test_action_is_updated_when_request_is_successful(self, testdb: Session):
        # Given
        action_update_request = {
            "action": "updated action",
            "action_type": "mitigation",
            "recommended": False,
        }

        # When
        client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        action = testdb.scalars(
            select(models.VulnAction).where(models.VulnAction.action_id == self.action_id)
        ).one_or_none()

        assert action is not None
        assert action.action == action_update_request["action"]
        assert action.action_type == action_update_request["action_type"]
        assert action.recommended == action_update_request["recommended"]

    def test_update_with_partial_fields(self, testdb: Session):
        # Given
        action_update_request = {
            "action": "only action updated",
        }

        # When
        client.put(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
            json=action_update_request,
        )

        # Then
        action = testdb.scalars(
            select(models.VulnAction).where(models.VulnAction.action_id == self.action_id)
        ).one_or_none()

        assert action is not None
        assert action.action == "only action updated"
        assert action.action_type == "elimination"
        assert action.recommended is True


class TestDeleteAction:
    @pytest.fixture(autouse=False)
    def action_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        self.vuln_id = VULN1["vuln_id"]
        create_vuln(USER1, VULN1)

        # Create an action
        action_create_request = {
            "vuln_id": str(self.vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        self.action_id = response.json()["action_id"]

    def test_action_is_deleted_when_request_is_successful(self, testdb: Session, action_setup):

        # When
        response = client.delete(
            f"/actions/{self.action_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 204

        action = testdb.scalars(
            select(models.VulnAction).where(models.VulnAction.action_id == self.action_id)
        ).one_or_none()

        assert action is None

    def test_delete_action_triggers_ticket_deletion(self, testdb: Session):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        # Create package, package_version, service and dependency table by upload sbom file
        upload_file_name = "test_trivy_cyclonedx_axios.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        service_name = "Service1 name"
        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name, upload_file_name)

        # Create a vuln
        ## If fixed_versions is not provided, a ticket will not be created without a vuln_action.
        no_fixed_versions_vuln_id = uuid4()
        no_fixed_versions_vuln_request: dict[str, Any] = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "name": "axios",
                    "ecosystem": "npm",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": [],
                }
            ],
        }

        client.put(
            f"/vulns/{no_fixed_versions_vuln_id}",
            headers=headers(USER1),
            json=no_fixed_versions_vuln_request,
        )

        action_create_request = {
            "vuln_id": str(no_fixed_versions_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # Create an action and trigger ticket creation
        action_response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        vuln = persistence.get_vuln_by_id(testdb, no_fixed_versions_vuln_id)
        if vuln is None:
            raise Exception("Vulnerability not found")

        threat1 = vuln.threats[0] if vuln and vuln.threats else None

        if threat1 is None:
            raise Exception("package1 is None")

        dependency1 = testdb.scalars(select(models.Dependency)).one()
        ticket_before_delete_action = persistence.get_ticket_by_threat_id_and_dependency_id(
            testdb,
            threat1.threat_id,
            dependency1.dependency_id,
        )

        # When
        client.delete(
            f"/actions/{action_response.json()['action_id']}",
            headers=headers(USER1),
        )

        # Then
        ticket_after_delete_action = persistence.get_ticket_by_threat_id_and_dependency_id(
            testdb,
            threat1.threat_id,
            dependency1.dependency_id,
        )

        # The ticket should be deleted
        assert ticket_before_delete_action != ticket_after_delete_action
        assert ticket_after_delete_action is None
