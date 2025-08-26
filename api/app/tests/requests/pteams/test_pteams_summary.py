from datetime import datetime
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models, persistence
from app.main import app
from app.ssvc.ssvc_calculator import calculate_ssvc_priority_by_ticket
from app.tests.medium.constants import (
    PACKAGE1,
    PTEAM1,
    USER1,
    VULN1,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
)

client = TestClient(app)


class TestGetPTeamPackagesSummary:
    ssvc_priority_count_zero: dict[str, int] = {
        ssvc_priority.value: 0 for ssvc_priority in list(models.SSVCDeployerPriorityEnum)
    }

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        return data["access_token"]

    @staticmethod
    def _get_service_id_by_service_name(user: dict, pteam_id: UUID | str, service_name: str) -> str:
        response = client.get(f"/pteams/{pteam_id}/services", headers=headers(user))
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        service = next(filter(lambda x: x["service_name"] == service_name, data))
        return service["service_id"]

    def package_setup_with_single_service(self, testdb, test_service, test_target, test_version):
        create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

        self.service1 = models.Service(
            service_name=test_service,
            pteam_id=str(self.pteam1.pteam_id),
        )

        testdb.add(self.service1)
        testdb.flush()

        self.package1 = models.Package(
            name=PACKAGE1["package_name"],
            ecosystem=PACKAGE1["ecosystem"],
        )

        persistence.create_package(testdb, self.package1)

        self.package_version1 = models.PackageVersion(
            package_id=self.package1.package_id,
            version=test_version,
        )
        persistence.create_package_version(testdb, self.package_version1)

        self.dependency1 = models.Dependency(
            target=test_target,
            package_manager=PACKAGE1["package_manager"],
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )

        testdb.add(self.dependency1)
        testdb.flush()

    def test_returns_summary_even_if_no_vulns(self, testdb):
        # Given
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"

        self.package_setup_with_single_service(testdb, test_service, test_target, test_version)

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/packages/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["packages"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_name": PACKAGE1["package_name"],
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatus)
                },
            }
        ]

    def test_returns_summary_even_if_no_tickets(self, testdb):
        # Given
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"

        self.package_setup_with_single_service(testdb, test_service, test_target, test_version)

        # create vuln
        create_vuln(USER1, VULN1)  # PACKAGE1

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/packages/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["packages"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_name": PACKAGE1["package_name"],
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatus)
                },
            }
        ]

    def test_returns_summary_if_having_alerted_ticket(self, testdb):
        # Given

        # Todo: Replace when API is created.
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        vulnerable_version = "1.2"  # vulnerable

        self.package_setup_with_single_service(
            testdb, test_service, test_target, vulnerable_version
        )

        vuln1 = create_vuln(USER1, VULN1)  # PACKAGE1
        db_ticket1 = testdb.scalars(select(models.Ticket)).one()

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/packages/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()
        expected_ssvc_priority = calculate_ssvc_priority_by_ticket(db_ticket1)
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            expected_ssvc_priority.value: 1,
        }
        summary["packages"][0]["updated_at"] = summary["packages"][0]["updated_at"].replace(
            "Z", "+00:00"
        )
        assert summary["packages"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_name": PACKAGE1["package_name"],
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(vuln1.updated_at),
                "status_count": {
                    **{status_type.value: 0 for status_type in list(models.TicketHandlingStatus)},
                    models.TicketHandlingStatus.alerted.value: 1,  # default status is ALERTED
                },
            }
        ]

    def test_returns_summary_even_if_multiple_services_are_registrered(self, testdb):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        # Todo: Replace when API is created.
        # add test_service to pteam1
        test_service1 = "test_service1"
        test_service2 = "test_service2"
        test_target = "test target"
        vulnerable_version = "1.2"  # vulnerable

        service1 = models.Service(
            service_name=test_service1,
            pteam_id=str(pteam1.pteam_id),
        )
        testdb.add(service1)
        service2 = models.Service(
            service_name=test_service2,
            pteam_id=str(pteam1.pteam_id),
        )
        testdb.add(service2)
        testdb.flush()

        package = models.Package(
            name=PACKAGE1["package_name"],
            ecosystem=PACKAGE1["ecosystem"],
        )
        persistence.create_package(testdb, package)

        package_version = models.PackageVersion(
            package_id=package.package_id,
            version=vulnerable_version,
        )
        persistence.create_package_version(testdb, package_version)

        dependency1 = models.Dependency(
            target=test_target,
            package_manager=PACKAGE1["package_manager"],
            package_version_id=package_version.package_version_id,
            service=service1,
        )
        testdb.add(dependency1)
        dependency2 = models.Dependency(
            target=test_target,
            package_manager=PACKAGE1["package_manager"],
            package_version_id=package_version.package_version_id,
            service=service2,
        )
        testdb.add(dependency2)
        testdb.flush()
        vuln1 = create_vuln(USER1, VULN1)  # PACKAGE1
        db_ticket1 = testdb.scalars(select(models.Ticket))

        # When
        url = f"/pteams/{pteam1.pteam_id}/packages/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()
        expected_ssvc_priority = min(  # we have only 1 tag
            calculate_ssvc_priority_by_ticket(db_threat) for db_threat in db_ticket1
        )
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            expected_ssvc_priority: 1,
        }

        assert len(summary["packages"][0]["service_ids"]) == 2
        assert set(summary["packages"][0]["service_ids"]) == {
            service1.service_id,
            service2.service_id,
        }

        del summary["packages"][0]["service_ids"]
        summary["packages"][0]["updated_at"] = summary["packages"][0]["updated_at"].replace(
            "Z", "+00:00"
        )
        assert summary["packages"] == [
            {
                "package_id": str(package.package_id),
                "package_name": PACKAGE1["package_name"],
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(vuln1.updated_at),
                "status_count": {
                    **{status_type.value: 0 for status_type in list(models.TicketHandlingStatus)},
                    models.TicketHandlingStatus.alerted.value: 2,  # default status is ALERTED
                },
            }
        ]

    def test_returns_summary_merges_multiple_package_managers_for_same_package(self, testdb):
        # Given
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"

        self.package_setup_with_single_service(testdb, test_service, test_target, test_version)

        # add second package_dependency
        dependency2 = models.Dependency(
            target="test_target2",
            package_manager="pip",
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )

        testdb.add(dependency2)
        testdb.flush()

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/packages/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }

        assert summary["packages"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_name": PACKAGE1["package_name"],
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"], "pip"],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatus)
                },
            }
        ]
