from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
)

client = TestClient(app)


## create_actionのテストコード
class TestCreateAction:

    ## 共通の設定

    @pytest.fixture(autouse=True)
    def common_setup(self, testdb: Session):
        # Create a user
        self.user = create_user(USER1)

        # Create a vuln
        self.new_vuln_id = uuid4()
        self.vuln_request1 = {
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

        response = client.put(
            f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=self.vuln_request1
        )

    def test_create_action_successfully(self, testdb: Session):
        """
        Test that create_action successfully creates an action.
        """
        # Given
        action_create_request = {
            "vuln_id": str(self.new_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # When
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        action = testdb.scalars(
            select(models.VulnAction).where(models.VulnAction.vuln_id == str(self.new_vuln_id))
        ).one_or_none()

        assert response.status_code == 200
        assert action is not None
        assert action.action == action_create_request["action"]
        assert action.action_type == action_create_request["action_type"]
        assert action.recommended == action_create_request["recommended"]

    def test_create_ticket_when_create_vuln_action(self, testdb: Session):
        # Given
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
                    "fixed_versions": [],  # fixed_versionsがない場合、vuln_acitonがないとticketは生成されない
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
        response = client.post(
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

    def test_raise_400_if_vuln_id_is_invalid(self):
        """
        Test that create_action raises a 400 error if vuln_id is invalid.
        """
        # Given
        invalid_vuln_id = uuid4()
        action_create_request = {
            "vuln_id": str(invalid_vuln_id),
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # Send the request and check the response
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "No such vuln"}

    def test_raise_400_if_vuln_id_is_none(self):
        """
        Test that create_action raises a 400 error if vuln_id is None.
        """
        # Given
        action_create_request = {
            "vuln_id": None,
            "action": "example action",
            "action_type": "elimination",
            "recommended": True,
        }

        # Send the request and check the response
        response = client.post(
            "/actions",
            headers=headers(USER1),
            json=action_create_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json() == {"detail": "Missing vuln_id"}
