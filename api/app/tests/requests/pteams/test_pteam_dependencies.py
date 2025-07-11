from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, persistence
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
    USER2,
    VULN1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
)

client = TestClient(app)


class TestGetDependency:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        service_name1 = "test_service1"
        ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, service_name1, VULN1)
        self.pteam_id = ticket_response["pteam_id"]

        dependencies_response = client.get(
            f"/pteams/{self.pteam_id}/dependencies", headers=headers(USER1)
        )
        self.dependency1 = dependencies_response.json()[0]
        self.dependency_id = self.dependency1["dependency_id"]

    def test_it_should_return_dependency_details_when_valid_ids_are_provided(self):
        # When
        dependency_response = client.get(
            f"/pteams/{self.pteam_id}/dependencies/{self.dependency_id}",
            headers=headers(USER1),
        )

        # Then
        assert dependency_response.status_code == 200
        data = dependency_response.json()
        assert data["dependency_id"] == self.dependency1["dependency_id"]
        assert data["service_id"] == self.dependency1["service_id"]
        assert data["package_version_id"] == self.dependency1["package_version_id"]
        assert data["package_id"] == self.dependency1["package_id"]
        assert data["package_manager"] == self.dependency1["package_manager"]
        assert data["target"] == self.dependency1["target"]
        assert data["dependency_mission_impact"] == self.dependency1["dependency_mission_impact"]
        assert data["package_name"] == self.dependency1["package_name"]
        assert data["package_source_name"] == self.dependency1["package_source_name"]
        assert data["package_version"] == self.dependency1["package_version"]
        assert data["package_ecosystem"] == self.dependency1["package_ecosystem"]
        assert data["vuln_matching_ecosystem"] == self.dependency1["vuln_matching_ecosystem"]

    def test_it_should_return_404_when_pteam_id_does_not_exist(self):
        # Given
        wrong_pteam_id = str(uuid4())

        # When
        dependency_response = client.get(
            f"/pteams/{wrong_pteam_id}/dependencies/{self.dependency_id}",
            headers=headers(USER1),
        )

        # Then
        assert dependency_response.status_code == 404
        assert dependency_response.json() == {"detail": "No such pteam"}

    def test_it_should_return_404_when_dependency_id_does_not_exist(self):
        # Given
        wrong_dependency_id = str(uuid4())

        # When
        dependency_response = client.get(
            f"/pteams/{self.pteam_id}/dependencies/{wrong_dependency_id}",
            headers=headers(USER1),
        )

        # Then
        assert dependency_response.status_code == 404
        assert dependency_response.json() == {"detail": "No such dependency"}


class TestGetDependencies:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

        test_service1 = "test_service1"
        test_service2 = "test_service2"
        self.test_target = "test target"
        test_version = "1.0.0"

        # Todo: Replace when API is created.
        self.service1 = models.Service(
            service_name=test_service1,
            pteam_id=str(self.pteam1.pteam_id),
        )
        testdb.add(self.service1)
        testdb.flush()

        self.service2 = models.Service(
            service_name=test_service2,
            pteam_id=str(self.pteam1.pteam_id),
        )
        testdb.add(self.service2)
        testdb.flush()

        self.package1 = models.LangPackage(
            name="test_package1",
            ecosystem="test_ecosystem1",
        )

        self.package2 = models.OSPackage(
            name="test_package2", ecosystem="test_ecosystem2", source_name="test_source_package2"
        )

        persistence.create_package(testdb, self.package1)
        persistence.create_package(testdb, self.package2)

        self.package_version1 = models.PackageVersion(
            package_id=self.package1.package_id,
            version=test_version,
        )

        self.package_version2 = models.PackageVersion(
            package_id=self.package2.package_id,
            version=test_version,
        )

        persistence.create_package_version(testdb, self.package_version1)
        persistence.create_package_version(testdb, self.package_version2)

        self.dependency1 = models.Dependency(
            target=self.test_target,
            package_manager="npm",
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )
        testdb.add(self.dependency1)
        testdb.flush()

        self.dependency2 = models.Dependency(
            target=self.test_target,
            package_manager="npm",
            package_version_id=self.package_version1.package_version_id,
            service=self.service2,
        )
        testdb.add(self.dependency2)
        testdb.flush()

        self.dependency3 = models.Dependency(
            target=self.test_target,
            package_manager="npm",
            package_version_id=self.package_version2.package_version_id,
            service=self.service2,
        )

        testdb.add(self.dependency3)
        testdb.flush()

    def test_is_should_return_200_when_dependencies_exist(self):
        # Given
        expected_dependency = [
            {
                "dependency_id": str(self.dependency1.dependency_id),
                "service_id": str(self.service1.service_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_id": str(self.package1.package_id),
                "package_manager": "npm",
                "target": self.test_target,
                "dependency_mission_impact": None,
                "package_name": self.package1.name,
                "package_source_name": None,
                "package_version": self.package_version1.version,
                "package_ecosystem": self.package1.ecosystem,
                "vuln_matching_ecosystem": self.package1.vuln_matching_ecosystem,
            },
            {
                "dependency_id": str(self.dependency2.dependency_id),
                "service_id": str(self.service2.service_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_id": str(self.package1.package_id),
                "package_manager": "npm",
                "target": self.test_target,
                "dependency_mission_impact": None,
                "package_name": self.package1.name,
                "package_source_name": None,
                "package_version": self.package_version1.version,
                "package_ecosystem": self.package1.ecosystem,
                "vuln_matching_ecosystem": self.package1.vuln_matching_ecosystem,
            },
            {
                "dependency_id": str(self.dependency3.dependency_id),
                "service_id": str(self.service2.service_id),
                "package_version_id": str(self.package_version2.package_version_id),
                "package_id": str(self.package2.package_id),
                "package_manager": "npm",
                "target": self.test_target,
                "dependency_mission_impact": None,
                "package_name": self.package2.name,
                "package_source_name": self.package2.source_name,
                "package_version": self.package_version2.version,
                "package_ecosystem": self.package2.ecosystem,
                "vuln_matching_ecosystem": self.package2.vuln_matching_ecosystem,
            },
        ]

        # returned dependencies are sorted by dependency_id
        expected_dependency.sort(key=lambda x: x["dependency_id"])

        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 200
        assert response.json() == expected_dependency

    def test_it_should_return_200_when_service_id_is_specified(self):
        # Given
        expected_dependency = {
            "dependency_id": str(self.dependency1.dependency_id),
            "service_id": str(self.service1.service_id),
            "package_version_id": str(self.package_version1.package_version_id),
            "package_id": str(self.package1.package_id),
            "package_manager": "npm",
            "target": self.test_target,
            "dependency_mission_impact": None,
            "package_name": self.package1.name,
            "package_source_name": None,
            "package_version": self.package_version1.version,
            "package_ecosystem": self.package1.ecosystem,
            "vuln_matching_ecosystem": self.package1.vuln_matching_ecosystem,
        }

        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies?service_id={self.service1.service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        assert response.json()[0] == expected_dependency

    def test_it_should_paginate_response_when_dependencies_exceed_limit(self, testdb: Session):
        # Given
        number_of_additional_deps = 8
        limit = 5

        # Add the existing dependencies
        expected_dependencies = [
            {
                "dependency_id": str(self.dependency1.dependency_id),
                "service_id": str(self.service1.service_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_id": str(self.package1.package_id),
                "package_manager": self.dependency1.package_manager,
                "target": self.dependency1.target,
                "dependency_mission_impact": self.dependency1.dependency_mission_impact,
                "package_name": self.package1.name,
                "package_source_name": None,
                "package_version": self.package_version1.version,
                "package_ecosystem": self.package1.ecosystem,
                "vuln_matching_ecosystem": self.package1.vuln_matching_ecosystem,
            },
            {
                "dependency_id": str(self.dependency2.dependency_id),
                "service_id": str(self.service2.service_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_id": str(self.package1.package_id),
                "package_manager": self.dependency2.package_manager,
                "target": self.dependency2.target,
                "dependency_mission_impact": self.dependency2.dependency_mission_impact,
                "package_name": self.package1.name,
                "package_source_name": None,
                "package_version": self.package_version1.version,
                "package_ecosystem": self.package1.ecosystem,
                "vuln_matching_ecosystem": self.package1.vuln_matching_ecosystem,
            },
            {
                "dependency_id": str(self.dependency3.dependency_id),
                "service_id": str(self.service2.service_id),
                "package_version_id": str(self.package_version2.package_version_id),
                "package_id": str(self.package2.package_id),
                "package_manager": "npm",
                "target": self.test_target,
                "dependency_mission_impact": None,
                "package_name": self.package2.name,
                "package_source_name": self.package2.source_name,
                "package_version": self.package_version2.version,
                "package_ecosystem": self.package2.ecosystem,
                "vuln_matching_ecosystem": self.package2.vuln_matching_ecosystem,
            },
        ]

        # Create additional dependencies
        for i in range(number_of_additional_deps):
            package = models.Package(
                name=f"test_package_pagination_{i}",
                ecosystem="test_ecosystem_pagination",
            )
            persistence.create_package(testdb, package)

            package_version = models.PackageVersion(
                package_id=package.package_id,
                version=f"1.0.{i}",
            )
            persistence.create_package_version(testdb, package_version)

            dependency = models.Dependency(
                target=f"test_target_pagination_{i}",
                package_manager="npm",
                package_version_id=package_version.package_version_id,
                service=self.service1,
            )
            testdb.add(dependency)

            # Add to expected results
            expected_dependency = {
                "dependency_id": str(dependency.dependency_id),
                "service_id": str(dependency.service.service_id),
                "package_version_id": str(package_version.package_version_id),
                "package_id": str(package.package_id),
                "package_manager": dependency.package_manager,
                "target": dependency.target,
                "dependency_mission_impact": dependency.dependency_mission_impact,
                "package_name": package.name,
                "package_source_name": None,
                "package_version": package_version.version,
                "package_ecosystem": package.ecosystem,
                "vuln_matching_ecosystem": package.vuln_matching_ecosystem,
            }
            expected_dependencies.append(expected_dependency)

        testdb.commit()

        # Sort expected dependencies by dependency_id (string comparison)
        expected_dependencies.sort(key=lambda x: x["dependency_id"])

        # When
        response_first_page = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies?offset=0&limit={limit}",
            headers=headers(USER1),
        )

        response_second_page = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies?offset={limit}&limit={limit}",
            headers=headers(USER1),
        )

        # Then
        # Check first page response
        assert response_first_page.status_code == 200
        first_page_data = response_first_page.json()
        assert len(first_page_data) == limit

        for i in range(limit):
            assert first_page_data[i] == expected_dependencies[i]

        # Check second page response
        assert response_second_page.status_code == 200
        second_page_data = response_second_page.json()
        assert len(second_page_data) == limit

        # Verify both pages match expected data
        for i in range(limit):
            assert second_page_data[i] == expected_dependencies[i + limit]

    def test_it_should_return_404_when_service_id_does_not_exist(self):
        # Given
        wrong_service_id = str(uuid4())

        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies?service_id={wrong_service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such service"

    def test_it_should_return_404_when_pteam_id_does_not_exist(self):
        # Given
        wronge_pteam_id = str(uuid4())

        # When
        response = client.get(f"/pteams/{wronge_pteam_id}/dependencies", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_it_should_return_403_when_not_pteam_member(self):
        # Given
        create_user(USER2)

        # When
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/dependencies", headers=headers(USER2)
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"
