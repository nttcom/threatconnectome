from datetime import datetime
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models, persistence
from app.main import app
from app.ssvc.ssvc_calculator import calculate_ssvc_priority_by_ticket
from app.tests.common.constants import (
    PACKAGE1,
    PTEAM1,
    USER1,
    VULN1,
)
from app.tests.common.exceptions import HTTPError
from app.tests.common.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
)

client = TestClient(app)


class TestGetPTeamPackagesSummary:
    @staticmethod
    def _get_ssvc_priority_count_zero() -> dict[str, int]:
        return {
            **{ssvc_priority.value: 0 for ssvc_priority in list(models.SSVCDeployerPriorityEnum)},
            "no_known_vulnerability": 0,
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
        url = f"/pteams/{self.pteam1.pteam_id}/package_versions/summary"
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
            **self._get_ssvc_priority_count_zero(),
            "no_known_vulnerability": 1,
        }
        assert summary["package_versions"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": test_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": "no_known_vulnerability",
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)
                },
            }
        ]

    def test_returns_legacy_packages_summary_alias(self, testdb):
        # Given
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"

        self.package_setup_with_single_service(testdb, test_service, test_target, test_version)

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/packages/summary"
        response = client.get(url, headers=headers(USER1))

        # Then
        assert response.status_code == 200
        summary = response.json()
        assert "package_versions" not in summary
        assert summary["packages"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": test_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": "no_known_vulnerability",
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)
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
        url = f"/pteams/{self.pteam1.pteam_id}/package_versions/summary"
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
            **self._get_ssvc_priority_count_zero(),
            "no_known_vulnerability": 1,
        }
        assert summary["package_versions"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": test_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": "no_known_vulnerability",
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)
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

        create_vuln(USER1, VULN1)  # PACKAGE1
        db_ticket1 = testdb.scalars(select(models.Ticket)).one()

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/package_versions/summary"
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
            **self._get_ssvc_priority_count_zero(),
            expected_ssvc_priority.value: 1,
        }
        summary["package_versions"][0]["updated_at"] = summary["package_versions"][0][
            "updated_at"
        ].replace("Z", "+00:00")
        assert summary["package_versions"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": vulnerable_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(db_ticket1.ticket_status.updated_at),
                "status_count": {
                    **{
                        status_type.value: 0
                        for status_type in list(models.TicketHandlingStatusType)
                    },
                    models.TicketHandlingStatusType.alerted.value: 1,  # default status is ALERTED
                },
            }
        ]

    def test_returns_summary_grouped_by_package_version(self, testdb):
        # Given
        create_user(USER1)
        pteam = create_pteam(USER1, PTEAM1)
        service = models.Service(service_name="test_service", pteam_id=str(pteam.pteam_id))
        testdb.add(service)
        testdb.flush()

        package = models.Package(
            name=PACKAGE1["package_name"],
            ecosystem=PACKAGE1["ecosystem"],
        )
        persistence.create_package(testdb, package)

        vulnerable_package_version = models.PackageVersion(
            package_id=package.package_id,
            version="1.2",
        )
        safe_package_version = models.PackageVersion(
            package_id=package.package_id,
            version="2.1",
        )
        persistence.create_package_version(testdb, vulnerable_package_version)
        persistence.create_package_version(testdb, safe_package_version)

        vulnerable_dependency = models.Dependency(
            target="requirements-vulnerable.txt",
            package_manager=PACKAGE1["package_manager"],
            package_version_id=vulnerable_package_version.package_version_id,
            service=service,
        )
        safe_dependency = models.Dependency(
            target="requirements-safe.txt",
            package_manager=PACKAGE1["package_manager"],
            package_version_id=safe_package_version.package_version_id,
            service=service,
        )
        testdb.add(vulnerable_dependency)
        testdb.add(safe_dependency)
        testdb.flush()

        create_vuln(USER1, VULN1)
        db_ticket = testdb.scalars(select(models.Ticket)).one()
        expected_ssvc_priority = calculate_ssvc_priority_by_ticket(db_ticket)

        # When
        url = f"/pteams/{pteam.pteam_id}/package_versions/summary"
        response = client.get(url, headers=headers(USER1))

        # Then
        assert response.status_code == 200
        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self._get_ssvc_priority_count_zero(),
            expected_ssvc_priority.value: 1,
            "no_known_vulnerability": 1,
        }

        vulnerable_summary = next(
            item
            for item in summary["package_versions"]
            if item["package_version_id"] == str(vulnerable_package_version.package_version_id)
        )
        safe_summary = next(
            item
            for item in summary["package_versions"]
            if item["package_version_id"] == str(safe_package_version.package_version_id)
        )
        vulnerable_summary["updated_at"] = vulnerable_summary["updated_at"].replace("Z", "+00:00")
        assert vulnerable_summary == {
            "package_id": str(package.package_id),
            "package_version_id": str(vulnerable_package_version.package_version_id),
            "package_name": PACKAGE1["package_name"],
            "package_version": vulnerable_package_version.version,
            "ecosystem": PACKAGE1["ecosystem"],
            "package_managers": [PACKAGE1["package_manager"]],
            "service_ids": [service.service_id],
            "ssvc_priority": expected_ssvc_priority.value,
            "updated_at": datetime.isoformat(db_ticket.ticket_status.updated_at),
            "status_count": {
                **{status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)},
                models.TicketHandlingStatusType.alerted.value: 1,
            },
        }
        assert safe_summary == {
            "package_id": str(package.package_id),
            "package_version_id": str(safe_package_version.package_version_id),
            "package_name": PACKAGE1["package_name"],
            "package_version": safe_package_version.version,
            "ecosystem": PACKAGE1["ecosystem"],
            "package_managers": [PACKAGE1["package_manager"]],
            "service_ids": [service.service_id],
            "ssvc_priority": "no_known_vulnerability",
            "updated_at": None,
            "status_count": {
                status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)
            },
        }

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
        create_vuln(USER1, VULN1)  # PACKAGE1
        db_ticket1 = testdb.scalars(select(models.Ticket))
        db_ticket_statuses = testdb.scalars(select(models.TicketStatus))

        # When
        url = f"/pteams/{pteam1.pteam_id}/package_versions/summary"
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
            **self._get_ssvc_priority_count_zero(),
            expected_ssvc_priority: 1,
        }

        assert len(summary["package_versions"][0]["service_ids"]) == 2
        assert set(summary["package_versions"][0]["service_ids"]) == {
            service1.service_id,
            service2.service_id,
        }

        del summary["package_versions"][0]["service_ids"]
        summary["package_versions"][0]["updated_at"] = summary["package_versions"][0][
            "updated_at"
        ].replace("Z", "+00:00")

        updated_time = []
        for ticket_status in db_ticket_statuses:
            updated_time.append(ticket_status.updated_at)

        assert summary["package_versions"] == [
            {
                "package_id": str(package.package_id),
                "package_version_id": str(package_version.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": vulnerable_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(max(updated_time)),
                "status_count": {
                    **{
                        status_type.value: 0
                        for status_type in list(models.TicketHandlingStatusType)
                    },
                    models.TicketHandlingStatusType.alerted.value: 2,  # default status is ALERTED
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
        url = f"/pteams/{self.pteam1.pteam_id}/package_versions/summary"
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
            **self._get_ssvc_priority_count_zero(),
            "no_known_vulnerability": 1,
        }

        assert summary["package_versions"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": test_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"], "pip"],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": "no_known_vulnerability",
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TicketHandlingStatusType)
                },
            }
        ]

    def test_returns_summary_if_having_defer_ticket(self, testdb):
        # Given
        test_service = "test_service"
        test_target = "test target"
        vulnerable_version = "1.2"

        self.package_setup_with_single_service(
            testdb, test_service, test_target, vulnerable_version
        )

        vuln1 = VULN1.copy()
        vuln1["exploitation"] = "none"
        vuln1["automatable"] = "no"
        create_vuln(USER1, vuln1)  # PACKAGE1
        db_ticket1 = testdb.scalars(select(models.Ticket)).one()

        request = {
            "system_exposure": models.SystemExposureEnum.SMALL,
            "service_mission_impact": models.MissionImpactEnum.DEGRADED,
            "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE,
        }
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.put(
            f"/pteams/{self.pteam1.pteam_id}/services/{self.service1.service_id}",
            headers=_headers,
            json=request,
        )

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/package_versions/summary"
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200
        summary = response.json()

        expected_ssvc_priority = calculate_ssvc_priority_by_ticket(db_ticket1)

        assert summary["ssvc_priority_count"] == {
            **self._get_ssvc_priority_count_zero(),
            expected_ssvc_priority.value: 1,
        }
        summary["package_versions"][0]["updated_at"] = summary["package_versions"][0][
            "updated_at"
        ].replace("Z", "+00:00")

        assert summary["package_versions"] == [
            {
                "package_id": str(self.package1.package_id),
                "package_version_id": str(self.package_version1.package_version_id),
                "package_name": PACKAGE1["package_name"],
                "package_version": vulnerable_version,
                "ecosystem": PACKAGE1["ecosystem"],
                "package_managers": [PACKAGE1["package_manager"]],
                "service_ids": [self.service1.service_id],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(db_ticket1.ticket_status.updated_at),
                "status_count": {
                    **{
                        status_type.value: 0
                        for status_type in list(models.TicketHandlingStatusType)
                    },
                    models.TicketHandlingStatusType.alerted.value: 1,  # default status is ALERTED
                },
            }
        ]
