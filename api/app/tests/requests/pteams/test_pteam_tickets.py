from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    VULN1,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    headers,
    headers_with_api_key,
    invite_to_pteam,
    set_ticket_status,
)

client = TestClient(app)


class TestGetTicketCountsTiedToServicePackage:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        service_name = "test_service1"
        self.ticket_response = ticket_utils.create_ticket(
            testdb, USER1, PTEAM1, service_name, VULN1
        )

        json_data = {
            "ticket_status": {
                "ticket_handling_status": "acknowledged",
                "note": "string",
                "assignees": [],
                "scheduled_at": None,
            }
        }
        set_ticket_status(
            USER1,
            self.ticket_response["pteam_id"],
            self.ticket_response["ticket_id"],
            json_data,
        )

    def test_it_should_return_404_with_wrong_pteam_id(self):
        # Given
        wrong_pteam_id = str(uuid4())

        # When
        response = client.get(
            f"/pteams/{wrong_pteam_id}/ticket_counts?service_id={self.ticket_response['service_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such pteam"}

    def test_it_should_return_403_with_wrong_pteam_member(self):
        # Given
        create_user(USER2)  # with wrong pteam member

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?service_id={self.ticket_response['service_id']}",
            headers=headers(USER2),
        )

        # Then
        assert response.status_code == 403
        assert response.json() == {"detail": "Not a pteam member"}

    def test_it_should_return_404_with_wrong_service_id(self):
        # Given
        wrong_service_id = str(uuid4())  # with wrong service_id

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?service_id={wrong_service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service"}

    def test_it_should_return_404_with_service_not_in_pteam(self, testdb):
        # Given
        pteam2 = create_pteam(USER1, PTEAM2)
        service2 = models.Service(
            service_name="test_service2",
            pteam_id=str(pteam2.pteam_id),
        )
        testdb.add(service2)
        testdb.flush()

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?service_id={service2.service_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service"}

    def test_it_should_return_404_with_wrong_package_id(self):
        # Given
        wrong_package_id = str(uuid4())  # with wrong tag_id

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?service_id={self.ticket_response['service_id']}&package_id={wrong_package_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such package"}

    def test_it_should_return_404_with_valid_but_not_service_package(self, testdb):
        # Given
        # with valid but not service package
        package = models.Package(
            name="a1",
            ecosystem="a2",
        )
        persistence.create_package(testdb, package)

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?service_id={self.ticket_response['service_id']}&package_id={package.package_id}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        assert response.json() == {"detail": "No such service package"}

    def test_it_should_return_404_with_wrong_related_ticket_status(self, testdb):
        # Given
        related_ticket_status = "wrong_status"

        # When
        response = client.get(
            f"/pteams/{self.ticket_response['pteam_id']}/ticket_counts?related_ticket_status={related_ticket_status}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Input should be 'solved' or 'unsolved'"


class TestGetTickets:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            # Given
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)

            test_service = "test_service1"
            test_target = "test target"
            test_version = "1.0.0"

            # Todo: Replace when API is created.
            self.service1 = models.Service(
                service_name=test_service,
                pteam_id=str(self.pteam1.pteam_id),
            )
            testdb.add(self.service1)
            testdb.flush()

            self.package1 = models.Package(
                name="test_package1",
                ecosystem="test_ecosystem1",
            )
            persistence.create_package(testdb, self.package1)

            self.package_version1 = models.PackageVersion(
                package_id=self.package1.package_id,
                version=test_version,
            )
            persistence.create_package_version(testdb, self.package_version1)

            self.dependency1 = models.Dependency(
                target=test_target,
                package_manager="npm",
                package_version_id=self.package_version1.package_version_id,
                service=self.service1,
            )
            testdb.add(self.dependency1)
            testdb.flush()

            self.vuln1 = models.Vuln(
                title="Test Vulnerability1",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                created_by=self.user1.user_id,
                created_at="2023-10-01T00:00:00Z",
                updated_at="2023-10-01T00:00:00Z",
            )
            persistence.create_vuln(testdb, self.vuln1)

            affect1 = models.Affect(
                vuln_id=self.vuln1.vuln_id,
                affected_versions=["<=1.0.0"],
                fixed_versions=["2.0.0"],
                affected_name=self.package1.name,
                ecosystem=self.package1.ecosystem,
            )
            persistence.create_affect(testdb, affect1)

            self.threat1 = models.Threat(
                package_version_id=self.package_version1.package_version_id,
                vuln_id=self.vuln1.vuln_id,
            )
            persistence.create_threat(testdb, self.threat1)

            ticket_business.fix_ticket_by_threat(testdb, self.threat1)

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

    class TestQueryParameter(Common):
        @pytest.fixture(scope="function", autouse=True)
        def common_setup_for_test_query_parameter(self, testdb):
            # Given
            db_ticket1 = testdb.scalars(select(models.Ticket)).one()
            db_status1 = testdb.scalars(select(models.TicketStatus)).one()
            self.expected_ticket_response1 = {
                "ticket_id": str(db_ticket1.ticket_id),
                "vuln_id": str(self.vuln1.vuln_id),
                "dependency_id": str(self.dependency1.dependency_id),
                "service_id": str(self.service1.service_id),
                "pteam_id": str(self.pteam1.pteam_id),
                "ssvc_deployer_priority": (
                    None
                    if db_ticket1.ssvc_deployer_priority is None
                    else db_ticket1.ssvc_deployer_priority.value
                ),
                "ticket_safety_impact": (
                    None
                    if db_ticket1.ticket_safety_impact is None
                    else db_ticket1.ticket_safety_impact.value
                ),
                "ticket_safety_impact_change_reason": None,
                "ticket_status": {
                    "status_id": db_status1.status_id,  # do not check
                    "ticket_handling_status": models.TicketHandlingStatusType.alerted.value,
                    "user_id": None,
                    "created_at": datetime.isoformat(db_status1.created_at).replace(
                        "+00:00", "Z"
                    ),  # check later
                    "updated_at": datetime.isoformat(db_status1.updated_at).replace(
                        "+00:00", "Z"
                    ),  # check later
                    "assignees": [],
                    "note": None,
                    "scheduled_at": None,
                    "action_logs": [],
                },
            }

        def test_it_should_return_200_when_ticket_exists(self):
            # When
            response = client.get(f"/pteams/{self.pteam1.pteam_id}/tickets", headers=headers(USER1))

            # Then
            assert response.status_code == 200
            assert response.json()[0] == self.expected_ticket_response1

        def test_it_should_return_200_when_all_queries_are_specified(self):
            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?service_id={self.service1.service_id}"
                f"&package_id={self.package1.package_id}&vuln_id={self.vuln1.vuln_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json()[0] == self.expected_ticket_response1

        def test_it_should_return_200_when_package_id_is_specified(self):
            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?package_id={self.package1.package_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json()[0] == self.expected_ticket_response1

        def test_it_should_return_200_when_vuln_id_is_specified(self):
            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?vuln_id={self.vuln1.vuln_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json()[0] == self.expected_ticket_response1

        def test_it_should_return_200_when_service_id_is_specified(self):
            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?service_id={self.service1.service_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json()[0] == self.expected_ticket_response1

        def test_it_should_return_no_ticket_when_wrong_package_id(self, testdb):
            # Given
            package2 = models.Package(
                name="test_package2",
                ecosystem="test_ecosystem2",
            )
            persistence.create_package(testdb, package2)

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?package_id={package2.package_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json() == []

        def test_it_should_return_no_ticket_when_wrong_vuln_id(self, testdb):
            # Given
            vuln2 = models.Vuln(
                title="Test Vulnerability2",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                created_by=self.user1.user_id,
                created_at="2023-10-01T00:00:00Z",
                updated_at="2023-10-01T00:00:00Z",
            )
            persistence.create_vuln(testdb, vuln2)

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?vuln_id={vuln2.vuln_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json() == []

        def test_it_should_return_no_ticket_when_wrong_service_id(self, testdb):
            # Given
            service2 = models.Service(
                service_name="test_service2",
                pteam_id=str(self.pteam1.pteam_id),
            )
            testdb.add(service2)
            testdb.flush()

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?service_id={service2.service_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json() == []

        def _setup_tickets_with_two_users_and_assignees(self, testdb):
            """Set up test environment with two tickets and two users for assignee tests"""
            # Create second pteam member
            user2 = create_user(USER2)
            invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
            accept_pteam_invitation(USER2, invitation1.invitation_id)

            # Get first ticket
            ticket1 = persistence.get_ticket_by_threat_id_and_dependency_id(
                testdb, self.threat1.threat_id, self.dependency1.dependency_id
            )

            # Create second ticket with new vulnerability
            vuln2_id = uuid4()
            vuln_request2 = {
                "title": "Test Vulnerability2",
                "cve_id": "CVE-0000-0001",
                "detail": "This is a test vulnerability.",
                "exploitation": "active",
                "automatable": "yes",
                "cvss_v3_score": 7.5,
                "vulnerable_packages": [
                    {
                        "affected_name": self.package1.name,
                        "ecosystem": self.package1.ecosystem,
                        "affected_versions": ["<=1.0.0"],
                        "fixed_versions": ["2.0.0"],
                    }
                ],
            }

            vuln_response2 = client.put(
                f"/vulns/{vuln2_id}", headers=headers_with_api_key(USER1), json=vuln_request2
            )
            vuln_data2 = vuln_response2.json()

            threat2 = persistence.get_threat_by_package_version_id_and_vuln_id(
                testdb, self.package_version1.package_version_id, vuln_data2["vuln_id"]
            )

            ticket2 = persistence.get_ticket_by_threat_id_and_dependency_id(
                testdb, threat2.threat_id, self.dependency1.dependency_id
            )

            # Prepare ticket status request objects
            status_request1 = {"ticket_status": {"assignees": [str(self.user1.user_id)]}}
            status_request2 = {
                "ticket_status": {"assignees": [str(self.user1.user_id), str(user2.user_id)]}
            }

            # Prepare API endpoint URLs
            url1 = f"/pteams/{self.pteam1.pteam_id}/tickets/{ticket1.ticket_id}"
            url2 = f"/pteams/{self.pteam1.pteam_id}/tickets/{ticket2.ticket_id}"

            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            client.put(url1, headers=_headers, json=status_request1)
            client.put(url2, headers=_headers, json=status_request2)

            return user2

        def test_it_should_return_all_assigned_tickets_when_assigned_to_me_is_true_for_user1(
            self, testdb
        ):
            # Given
            # user1 is assigned to all tickets
            self._setup_tickets_with_two_users_and_assignees(testdb)

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?assigned_to_me=true",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert len(response.json()) == 2

            # Check ticket assignees
            tickets_data = response.json()
            for ticket in tickets_data:
                ticket_status = ticket["ticket_status"]
                assert str(self.user1.user_id) in ticket_status["assignees"]

        def test_it_should_return_only_one_ticket_when_assigned_to_me_is_true_for_user2(
            self, testdb
        ):
            # Given
            # user2 is assigned to one ticket
            user2 = self._setup_tickets_with_two_users_and_assignees(testdb)

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?assigned_to_me=true",
                headers=headers(USER2),
            )

            # Then
            assert response.status_code == 200
            # There are two tickets in db but only one has user2 assigned
            assert len(response.json()) == 1

            # Check ticket assignees
            tickets_data = response.json()
            for ticket in tickets_data:
                ticket_status = ticket["ticket_status"]
                assert str(user2.user_id) in ticket_status["assignees"]

        def test_it_should_return_empty_list_when_querying_unassigned_user(self):
            # no tickets have been assigned to user1 yet
            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?assigned_to_me=true",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 200
            assert response.json() == []

    class TestWrongId(Common):
        def test_it_should_return_404_when_pteam_id_does_not_exist(self):
            # Given
            pteam_id = str(uuid4())

            # When
            response = client.get(
                f"/pteams/{pteam_id}/tickets",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 404
            assert response.json()["detail"] == "No such pteam"

        def test_it_should_return_404_when_service_id_does_not_exist(self):
            # Given
            setvice_id = str(uuid4())

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?service_id={setvice_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 404
            assert response.json()["detail"] == "No such service"

        def test_it_should_return_404_when_vuln_id_does_not_exist(self):
            # Given
            vuln_id = str(uuid4())

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?vuln_id={vuln_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 404
            assert response.json()["detail"] == "No such vuln"

        def test_it_should_return_404_when_package_id_does_not_exist(self):
            # Given
            package_id = str(uuid4())

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets?package_id={package_id}",
                headers=headers(USER1),
            )

            # Then
            assert response.status_code == 404
            assert response.json()["detail"] == "No such package"

        def test_it_should_return_403_when_not_pteam_member(self):
            # Given
            create_user(USER2)

            # When
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/tickets",
                headers=headers(USER2),
            )

            # Then
            assert response.status_code == 403
            assert response.json()["detail"] == "Not a pteam member"


class TestGetTicket:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, testdb):
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        self.service1 = models.Service(
            service_name="test_service",
            pteam_id=str(self.pteam1.pteam_id),
        )
        testdb.add(self.service1)
        testdb.flush()
        self.package1 = models.Package(
            name="test_package",
            ecosystem="test_ecosystem",
        )
        persistence.create_package(testdb, self.package1)
        self.package_version1 = models.PackageVersion(
            package_id=self.package1.package_id,
            version="1.0.0",
        )
        persistence.create_package_version(testdb, self.package_version1)
        self.dependency1 = models.Dependency(
            target="test_target",
            package_manager="npm",
            package_version_id=self.package_version1.package_version_id,
            service=self.service1,
        )
        testdb.add(self.dependency1)
        testdb.flush()
        self.vuln1 = models.Vuln(
            title="Test Vulnerability",
            detail="This is a test vulnerability.",
            cvss_v3_score=7.5,
            created_by=self.user1.user_id,
            created_at="2023-10-01T00:00:00Z",
            updated_at="2023-10-01T00:00:00Z",
        )
        persistence.create_vuln(testdb, self.vuln1)
        affect1 = models.Affect(
            vuln_id=self.vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=["2.0.0"],
            affected_name=self.package1.name,
            ecosystem=self.package1.ecosystem,
        )
        persistence.create_affect(testdb, affect1)
        self.threat1 = models.Threat(
            package_version_id=self.package_version1.package_version_id,
            vuln_id=self.vuln1.vuln_id,
        )
        persistence.create_threat(testdb, self.threat1)
        ticket_business.fix_ticket_by_threat(testdb, self.threat1)
        self.ticket1 = testdb.scalars(select(models.Ticket)).one()
        self.ticket_status1 = testdb.scalars(select(models.TicketStatus)).one()

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        data = response.json()
        return data["access_token"]

    def _set_ticket_status(self, pteam_id: str, ticket_id: str, request: dict) -> dict:
        url = f"/pteams/{pteam_id}/tickets/{ticket_id}"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        return client.put(url, headers=_headers, json=request).json()

    def test_it_should_return_correct_initial_ticket_detail(self):
        # Given
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        # when
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
            headers=_headers,
        )

        # Then
        expected_ticket_status = {
            "status_id": self.ticket_status1.status_id,
            "ticket_handling_status": models.TicketHandlingStatusType.alerted.value,
            "user_id": None,
            "created_at": datetime.isoformat(self.ticket_status1.created_at).replace("+00:00", "Z"),
            "updated_at": datetime.isoformat(self.ticket_status1.updated_at).replace("+00:00", "Z"),
            "assignees": [],
            "note": None,
            "scheduled_at": None,
            "action_logs": [],
        }
        assert response.status_code == 200
        data = response.json()
        assert data["ticket_id"] == str(self.ticket1.ticket_id)
        assert data["vuln_id"] == str(self.vuln1.vuln_id)
        assert data["dependency_id"] == str(self.dependency1.dependency_id)
        assert data["ssvc_deployer_priority"] == (
            None
            if self.ticket1.ssvc_deployer_priority is None
            else self.ticket1.ssvc_deployer_priority.value
        )
        assert data["ticket_status"] == expected_ticket_status

    def test_returns_current_status_if_status_created(self):
        # Given
        status_request = {
            "ticket_status": {
                "ticket_handling_status": models.TicketHandlingStatusType.scheduled.value,
                "assignees": [str(self.user1.user_id)],
                "note": "assign user2 and schedule at 2345/6/7",
                "scheduled_at": "2345-06-07T08:09:10Z",
            }
        }
        set_response = self._set_ticket_status(
            self.pteam1.pteam_id, self.ticket1.ticket_id, status_request
        )

        # When
        url = f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)

        # Then
        assert response.status_code == 200

        data = response.json()
        expected_status = {
            "status_id": set_response["ticket_status"]["status_id"],
            "user_id": str(self.user1.user_id),
            "created_at": set_response["ticket_status"]["created_at"],
            "updated_at": set_response["ticket_status"]["updated_at"],
            "action_logs": [],
            **status_request["ticket_status"],
        }

        if data["ticket_status"].get("scheduled_at") and expected_status.get("scheduled_at"):
            assert data["ticket_status"]["scheduled_at"].replace("Z", "") == expected_status[
                "scheduled_at"
            ].replace("Z", "")
            del data["ticket_status"]["scheduled_at"]
            del expected_status["scheduled_at"]
        assert data["ticket_status"] == expected_status

    def test_it_should_return_404_when_wrong_ticket_id(self):
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        wrong_ticket_id = str(uuid4())
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/tickets/{wrong_ticket_id}",
            headers=_headers,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "No such ticket"

    def test_it_should_return_404_when_pteam_not_found(self):
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        wrong_pteam_id = str(uuid4())
        response = client.get(
            f"/pteams/{wrong_pteam_id}/tickets/{self.ticket1.ticket_id}",
            headers=_headers,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "No such pteam"

    def test_it_should_return_403_when_not_pteam_member(self):
        create_user(USER2)
        user2_access_token = self._get_access_token(USER2)
        _headers = {
            "Authorization": f"Bearer {user2_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(
            f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
            headers=_headers,
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"


class TestPutTicket:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def setup(self, testdb):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            self.service1 = models.Service(
                service_name="test_service",
                pteam_id=str(self.pteam1.pteam_id),
            )
            testdb.add(self.service1)
            testdb.flush()
            self.package1 = models.Package(
                name="test_package",
                ecosystem="test_ecosystem",
            )
            persistence.create_package(testdb, self.package1)
            self.package_version1 = models.PackageVersion(
                package_id=self.package1.package_id,
                version="1.0.0",
            )
            persistence.create_package_version(testdb, self.package_version1)
            self.dependency1 = models.Dependency(
                target="test_target",
                package_manager="npm",
                package_version_id=self.package_version1.package_version_id,
                service=self.service1,
            )
            testdb.add(self.dependency1)
            testdb.flush()
            self.vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                created_by=self.user1.user_id,
                created_at="2023-10-01T00:00:00Z",
                updated_at="2023-10-01T00:00:00Z",
            )
            persistence.create_vuln(testdb, self.vuln1)
            affect1 = models.Affect(
                vuln_id=self.vuln1.vuln_id,
                affected_versions=["<=1.0.0"],
                fixed_versions=["2.0.0"],
                affected_name=self.package1.name,
                ecosystem=self.package1.ecosystem,
            )
            persistence.create_affect(testdb, affect1)
            self.threat1 = models.Threat(
                package_version_id=self.package_version1.package_version_id,
                vuln_id=self.vuln1.vuln_id,
            )
            persistence.create_threat(testdb, self.threat1)
            ticket_business.fix_ticket_by_threat(testdb, self.threat1)
            self.ticket1 = testdb.scalars(select(models.Ticket)).one()
            self.ticket_status1 = testdb.scalars(select(models.TicketStatus)).one()

        @staticmethod
        def _get_access_token(user: dict) -> str:
            body = {
                "username": user["email"],
                "password": user["pass"],
            }
            response = client.post("/auth/token", data=body)
            if response.status_code != 200:
                raise Exception(f"Failed to get access token: {response.text}")
            data = response.json()
            return data["access_token"]

    class TestTicket(Common):
        def test_it_should_update_ticket_safety_impact(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "Test reason for safety impact",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            data = response.json()

            assert data["ticket_id"] == str(self.ticket1.ticket_id)
            assert data["vuln_id"] == str(self.vuln1.vuln_id)
            assert data["dependency_id"] == str(self.dependency1.dependency_id)
            assert data["ssvc_deployer_priority"] == models.TicketHandlingStatusType.scheduled.value
            assert data["ticket_safety_impact"] == request["ticket_safety_impact"]
            assert (
                data["ticket_safety_impact_change_reason"]
                == request["ticket_safety_impact_change_reason"]
            )
            assert data["ticket_status"]["status_id"] == self.ticket_status1.status_id
            assert (
                data["ticket_status"]["ticket_handling_status"]
                == models.TicketHandlingStatusType.alerted.value
            )
            assert data["ticket_status"]["user_id"] is None
            assert data["ticket_status"][
                "created_at"
            ] == self.ticket_status1.created_at.isoformat().replace("+00:00", "Z")
            assert data["ticket_status"][
                "updated_at"
            ] == self.ticket_status1.updated_at.isoformat().replace("+00:00", "Z")
            assert data["ticket_status"]["assignees"] == []
            assert data["ticket_status"]["note"] is None
            assert data["ticket_status"]["scheduled_at"] is None
            assert data["ticket_status"]["action_logs"] == []

        def test_it_should_update_ticket_safety_impact_change_reason(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {
                "ticket_safety_impact_change_reason": "Updated reason for safety impact",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_safety_impact_change_reason"] == "Updated reason for safety impact"

        def test_it_should_set_ticket_safety_impact_change_reason_none_when_blank(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            # Add a value to ticket_safety_impact_change_reason in advance
            set_request = {
                "ticket_safety_impact_change_reason": "sample",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=set_request,
            )

            # In case of an empty string
            request = {
                "ticket_safety_impact_change_reason": "",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_safety_impact_change_reason"] is None

            # Add a value to ticket_safety_impact_change_reason in advance
            set_request = {
                "ticket_safety_impact_change_reason": "sample",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=set_request,
            )

            # In case of whitespace characters
            request = {
                "ticket_safety_impact_change_reason": "   ",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_safety_impact_change_reason"] is None

        def test_it_should_keep_previous_values_when_ticket_safety_impact_and_reason_not_specified(
            self,
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            initial_request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "first reason",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=initial_request,
            )

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json={},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_safety_impact"] == initial_request["ticket_safety_impact"]
            assert (
                data["ticket_safety_impact_change_reason"]
                == initial_request["ticket_safety_impact_change_reason"]
            )

        def test_it_should_update_ticket_safety_impact_and_reason_to_none(self, testdb: Session):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            initial_request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "some reason",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=initial_request,
            )
            assert response.status_code == 200

            request = {
                "ticket_safety_impact": None,
                "ticket_safety_impact_change_reason": None,
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["ticket_safety_impact"] is None
            assert data["ticket_safety_impact_change_reason"] is None

        def test_it_should_return_400_when_ticket_safety_impact_change_reason_too_long(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            # 2001 half-width characters（max is 2000）
            too_long_reason = "a" * 2001
            request = {
                "ticket_safety_impact_change_reason": too_long_reason,
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 400
            assert (
                "Too long ticket_safety_impact_change_reason."
                + " Max length is 2000 in half-width or 1000 in full-width"
                in response.json()["detail"]
            )

        def test_it_should_return_404_when_wrong_ticket_id(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            wrong_ticket_id = str(uuid4())
            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "Test reason",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{wrong_ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 404
            assert response.json()["detail"] == "No such ticket"

        def test_it_should_return_404_when_pteam_not_found(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            wrong_pteam_id = str(uuid4())
            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "Test reason",
            }
            response = client.put(
                f"/pteams/{wrong_pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 404
            assert response.json()["detail"] == "No such pteam"

        def test_it_should_return_403_when_not_pteam_member(self):
            create_user(USER2)
            user2_access_token = self._get_access_token(USER2)
            _headers = {
                "Authorization": f"Bearer {user2_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "Test reason",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 403
            assert response.json()["detail"] == "Not a pteam member"

        def test_it_should_not_fix_ssvc_priority_when_not_changed(self, testdb: Session):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            initial_priority = self.ticket1.ssvc_deployer_priority

            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": (
                    self.ticket1.ticket_safety_impact_change_reason
                ),
            }

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200

            updated_ticket = (
                testdb.query(models.Ticket)
                .filter(models.Ticket.ticket_id == self.ticket1.ticket_id)
                .one()
            )

            assert updated_ticket.ssvc_deployer_priority == initial_priority

        def test_it_should_fix_ssvc_priority_when_ticket_safety_impact_changed(
            self, testdb: Session
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            self.ticket1.ssvc_deployer_priority = models.SSVCDeployerPriorityEnum.IMMEDIATE.value
            testdb.commit()
            initial_priority = self.ticket1.ssvc_deployer_priority

            request = {
                "ticket_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
                "ticket_safety_impact_change_reason": "update for test",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200

            updated_ticket = (
                testdb.query(models.Ticket)
                .filter(models.Ticket.ticket_id == self.ticket1.ticket_id)
                .one()
            )
            assert updated_ticket.ssvc_deployer_priority != initial_priority
            assert (
                updated_ticket.ssvc_deployer_priority == models.TicketHandlingStatusType.scheduled
            )

        def test_it_should_return_422_when_invalid_ticket_safety_impact(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {
                "ticket_safety_impact": "invalid_value",
                "ticket_safety_impact_change_reason": "Test reason",
            }
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 422
            assert any(
                "ticket_safety_impact" in err["loc"] for err in response.json().get("detail", [])
            )

    class TestTicketStatus(Common):
        def common_setup_for_set_ticket_status(
            self, ticket_handling_status, need_scheduled_at, scheduled_at
        ):
            status_request = {"ticket_status": {"assignees": [str(self.user1.user_id)]}}
            if ticket_handling_status is not None:
                status_request["ticket_status"]["ticket_handling_status"] = ticket_handling_status
            if need_scheduled_at:
                status_request["ticket_status"]["scheduled_at"] = scheduled_at
            url = f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}"
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            return response

        def test_set_requested_status(self):
            status_request = {
                "ticket_status": {
                    "ticket_handling_status": models.TicketHandlingStatusType.scheduled.value,
                    "assignees": [str(self.user1.user_id)],
                    "note": "assign user2 and schedule at 2345/6/7",
                    "scheduled_at": "2345-06-07T08:09:10Z",
                }
            }
            url = f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}"
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            assert response.status_code == 200

            data = response.json()
            # check not-none only because we do not have values to compare
            for key in {"status_id", "created_at", "updated_at"}:
                assert data["ticket_status"][key] is not None
                del data["ticket_status"][key]
            expected_status = {
                "user_id": str(self.user1.user_id),
                "action_logs": [],
                **status_request["ticket_status"],
            }
            if data["ticket_status"].get("scheduled_at") and expected_status.get("scheduled_at"):
                assert data["ticket_status"]["scheduled_at"].replace("Z", "") == expected_status[
                    "scheduled_at"
                ].replace("Z", "")
                del data["ticket_status"]["scheduled_at"]
                del expected_status["scheduled_at"]

            assert data["ticket_status"] == expected_status

        @pytest.mark.parametrize(
            "field_name, expected_response_detail",
            [
                ("ticket_handling_status", "Cannot specify None for ticket_handling_status"),
                ("logging_ids", "Cannot specify None for logging_ids"),
                ("assignees", "Cannot specify None for assignees"),
            ],
        )
        def test_it_should_return_400_when_required_fields_is_None(
            self,
            field_name,
            expected_response_detail,
        ):
            status_request = {"ticket_status": {field_name: None}}
            url = f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}"
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "ticket_handling_status, scheduled_at, expected_response_detail",
            [
                (models.TicketHandlingStatusType.alerted.value, None, "Wrong topic status"),
                (
                    models.TicketHandlingStatusType.alerted.value,
                    None,
                    "Wrong topic status",
                ),
                (
                    models.TicketHandlingStatusType.alerted.value,
                    "2000-01-01T00:00:00",
                    "Wrong topic status",
                ),
                (
                    models.TicketHandlingStatusType.alerted.value,
                    "2345-06-07T08:09:10",
                    "Wrong topic status",
                ),
            ],
        )
        def test_it_should_return_400_when_ticket_handling_status_is_alerted(
            self,
            ticket_handling_status,
            scheduled_at,
            expected_response_detail,
        ):
            response = self.common_setup_for_set_ticket_status(
                ticket_handling_status, True, scheduled_at
            )
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "ticket_handling_status, scheduled_at, expected_response_detail",
            [
                (
                    models.TicketHandlingStatusType.acknowledged.value,
                    "2000-01-01T00:00:00Z",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.acknowledged.value,
                    "2345-06-07T08:09:10Z",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.completed.value,
                    "2000-01-01T00:00:00Z",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.completed.value,
                    "2345-06-07T08:09:10Z",
                    "If status is not scheduled, do not specify schduled_at",
                ),
            ],
        )
        def test_it_should_return_400_when_handling_status_is_not_scheduled_and_schduled_at_is_time(
            self,
            ticket_handling_status,
            scheduled_at,
            expected_response_detail,
        ):
            response = self.common_setup_for_set_ticket_status(
                ticket_handling_status, True, scheduled_at
            )
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "ticket_handling_status, need_scheduled_at, scheduled_at, expected_response_detail",
            [
                (
                    models.TicketHandlingStatusType.scheduled.value,
                    False,
                    None,
                    "If status is scheduled, specify schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.scheduled.value,
                    True,
                    None,
                    "If status is scheduled, unable to reset schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.scheduled.value,
                    True,
                    "2000-01-01T00:00:00Z",
                    "If status is scheduled, schduled_at must be a future time",
                ),
            ],
        )
        def test_it_should_return_400_when_schduled_at_is_not_future_time(
            self,
            ticket_handling_status,
            need_scheduled_at,
            scheduled_at,
            expected_response_detail,
        ):
            # when ticket_handling_status is scheduled and scheduled at is not future time,
            # return 200.

            response = self.common_setup_for_set_ticket_status(
                ticket_handling_status, need_scheduled_at, scheduled_at
            )
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            (
                "ticket_handling_status",
                "need_scheduled_at",
                "scheduled_at",
                "expected_response_status_code",
            ),
            [
                (models.TicketHandlingStatusType.acknowledged.value, False, None, 200),
                (
                    models.TicketHandlingStatusType.acknowledged.value,
                    True,
                    None,
                    200,
                ),
                (
                    models.TicketHandlingStatusType.scheduled.value,
                    True,
                    "2345-06-07T08:09:10Z",
                    200,
                ),
                (models.TicketHandlingStatusType.completed.value, False, None, 200),
                (models.TicketHandlingStatusType.completed.value, True, None, 200),
            ],
        )
        def test_it_should_return_200_when_handling_status_and_schduled_at_have_the_correct_values(
            self,
            ticket_handling_status,
            need_scheduled_at,
            scheduled_at,
            expected_response_status_code,
        ):
            response = self.common_setup_for_set_ticket_status(
                ticket_handling_status, need_scheduled_at, scheduled_at
            )
            assert response.status_code == expected_response_status_code
            set_response = response.json()
            if set_response["ticket_status"].get("scheduled_at") and scheduled_at:
                assert set_response["ticket_status"]["scheduled_at"].replace(
                    "Z", ""
                ) == scheduled_at.replace("Z", "")
            else:
                assert set_response["ticket_status"]["scheduled_at"] == scheduled_at
            assert set_response["ticket_status"]["ticket_handling_status"] == ticket_handling_status
            assert set_response["ticket_status"]["user_id"] == str(self.user1.user_id)
            assert set_response["ticket_status"]["assignees"] == [str(self.user1.user_id)]

        @pytest.mark.parametrize(
            "current_ticket_handling_status, current_scheduled_at, expected_response_detail",
            [
                (
                    models.TicketHandlingStatusType.completed.value,
                    None,
                    "If current status is not scheduled and previous status is scheduled, "
                    "need to reset schduled_at",
                ),
                (
                    models.TicketHandlingStatusType.acknowledged.value,
                    None,
                    "If current status is not scheduled and previous status is scheduled, "
                    "need to reset schduled_at",
                ),
            ],
        )
        def test_it_should_return_400_when_previous_status_is_schduled_and_schduled_at_is_reset(
            self,
            current_ticket_handling_status,
            current_scheduled_at,
            expected_response_detail,
        ):
            # When previous ticket_handling_status is scheduled and current ticket_handling_status
            # is not scheduled, return 400 if current_scheduled_at does not contain
            # a value to reset None.

            previous_ticket_handling_status = models.TicketHandlingStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10Z"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_ticket_handling_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_ticket_handling_status, False, current_scheduled_at
            )
            assert current_response.status_code == 400
            assert current_response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "current_ticket_handling_status, current_scheduled_at, expected_response_detail",
            [
                (
                    None,
                    None,
                    "If status is scheduled, unable to reset schduled_at",
                ),
                (
                    None,
                    "2000-01-01T00:00:00Z",
                    "If status is scheduled, schduled_at must be a future time",
                ),
            ],
        )
        def test_it_should_return_400_when_handling_status_and_scheduled_at_is_not_appropriate(
            self,
            current_ticket_handling_status,
            current_scheduled_at,
            expected_response_detail,
        ):
            # When previous ticket_handling_status is scheduled and current ticket_handling_status
            #  is None, return 400 if current_scheduled_at does not contain
            # future time or None.

            previous_ticket_handling_status = models.TicketHandlingStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10Z"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_ticket_handling_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_ticket_handling_status, True, current_scheduled_at
            )
            assert current_response.status_code == 400
            assert current_response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "current_ticket_handling_status, need_scheduled_at, "
            + "current_scheduled_at, expected_response_status_code",
            [
                (
                    None,
                    False,
                    None,
                    200,
                ),
                (
                    models.TicketHandlingStatusType.completed.value,
                    True,
                    None,
                    200,
                ),
            ],
        )
        def test_it_should_return_200_when_previous_and_current_status_have_the_correct_values(
            self,
            current_ticket_handling_status,
            need_scheduled_at,
            current_scheduled_at,
            expected_response_status_code,
        ):
            # When previous ticket_handling_status is scheduled and current ticket_handling_status
            # is None, return 200 if current_scheduled_at contain None.

            # When previous ticket_handling_status is scheduled and current ticket_handling_status
            # is completed, return 200 if current_scheduled_at contain
            # a value to reset None.

            previous_ticket_handling_status = models.TicketHandlingStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10Z"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_ticket_handling_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_ticket_handling_status, need_scheduled_at, current_scheduled_at
            )
            assert current_response.status_code == expected_response_status_code

            set_response = current_response.json()
            assert set_response["ticket_id"] == self.ticket1.ticket_id
            assert set_response["ticket_status"]["user_id"] == str(self.user1.user_id)
            assert set_response["ticket_status"]["assignees"] == [str(self.user1.user_id)]

            _current_ticket_handling_status = current_ticket_handling_status
            if current_ticket_handling_status is None:
                _current_ticket_handling_status = models.TicketHandlingStatusType.scheduled.value
            assert (
                set_response["ticket_status"]["ticket_handling_status"]
                == _current_ticket_handling_status
            )

            if need_scheduled_at:
                _scheduled_at = current_scheduled_at
            else:
                _scheduled_at = previous_scheduled_at
            if set_response["ticket_status"].get("scheduled_at") and _scheduled_at:
                assert set_response["ticket_status"]["scheduled_at"].replace(
                    "Z", ""
                ) == _scheduled_at.replace("Z", "")
            else:
                assert set_response["ticket_status"]["scheduled_at"] == _scheduled_at

        def test_it_should_set_requester_if_assignee_is_not_specify_and_saved_current_user(self):
            status_request = {
                "ticket_status": {
                    "ticket_handling_status": models.TicketHandlingStatusType.completed.value,
                    "note": "assign None",
                }
            }
            url = f"/pteams/{self.pteam1.pteam_id}/tickets/{self.ticket1.ticket_id}"
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)

            assert response.status_code == 200
            assert response.json()["ticket_status"]["assignees"] == [str(self.user1.user_id)]

        def test_it_should_return_400_when_there_is_no_time_zone_in_scheduled_at_time(self):
            ticket_handling_status = models.TicketHandlingStatusType.scheduled.value
            scheduled_at = "2345-06-07T08:09:10"  # without time zone
            response = self.common_setup_for_set_ticket_status(
                ticket_handling_status, True, scheduled_at
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "Unwise expiration (grant timezone)"
