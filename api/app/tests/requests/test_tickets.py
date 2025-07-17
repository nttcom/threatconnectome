import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    USER3,
    VULN1,
    VULN2,
    VULN3,
)
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    create_vuln,
    headers,
    invite_to_pteam,
    set_ticket_status,
)

client = TestClient(app)


class TestGetTickets:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, testdb):
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        self.vuln1 = create_vuln(USER1, VULN1)

        # Ticket1
        self.service_name1 = "test_service1"
        self.ticket_response1 = self._create_ticket_with_threat(
            testdb, self.user1, self.pteam1, self.service_name1, self.vuln1
        )
        json_data1 = {
            "vuln_status": "acknowledged",
            "note": "string",
            "assignees": [str(self.user1.user_id)],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data1,
        )

        # Ticket2
        self.service_name2 = "test_service2"
        self.ticket_response2 = self._create_ticket_with_threat(
            testdb, self.user1, self.pteam1, self.service_name2, self.vuln1
        )
        json_data2 = {
            "vuln_status": "acknowledged",
            "note": "string",
            "assignees": [],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response2["pteam_id"],
            self.ticket_response2["ticket_id"],
            json_data2,
        )

    @staticmethod
    def _create_ticket_with_threat(testdb, user, pteam, service_name, vuln):
        # 1. Load the SBOM file and create service, dependency, and package from it.
        upload_file_name = "trivy-ubuntu2004.cdx.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)
        bg_create_tags_from_sbom_json(sbom_json, pteam.pteam_id, service_name, upload_file_name)

        # 2. Retrieve service, dependency, and package_version from the database.
        service = (
            testdb.query(models.Service)
            .filter_by(pteam_id=str(pteam.pteam_id), service_name=service_name)
            .one()
        )
        dependency = (
            testdb.query(models.Dependency).filter_by(service_id=service.service_id).first()
        )
        package_version = (
            testdb.query(models.PackageVersion)
            .filter_by(package_version_id=dependency.package_version_id)
            .one()
        )

        # 3. Find or create Threat, then create Ticket and TicketStatus.
        threat = (
            testdb.query(models.Threat)
            .filter_by(
                package_version_id=package_version.package_version_id,
                vuln_id=str(vuln.vuln_id),
            )
            .first()
        )

        if not threat:
            threat = models.Threat(
                package_version_id=package_version.package_version_id,
                vuln_id=vuln.vuln_id,
            )
            testdb.add(threat)
            testdb.flush()

        ticket = models.Ticket(
            threat_id=threat.threat_id,
            dependency_id=dependency.dependency_id,
        )
        testdb.add(ticket)
        testdb.flush()

        ticket_status = models.TicketStatus(
            ticket_id=ticket.ticket_id,
            user_id=user.user_id,
            vuln_status=models.VulnStatusType.alerted,
            note="",
            assignees=[],
            scheduled_at=None,
        )
        testdb.add(ticket_status)
        testdb.commit()
        testdb.refresh(ticket)
        return {
            "user_id": str(user.user_id),
            "pteam_id": str(pteam.pteam_id),
            "vuln_id": str(vuln.vuln_id),
            "threat_id": str(threat.threat_id),
            "ticket_id": str(ticket.ticket_id),
        }

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        assert response.status_code == 200
        return response.json()["access_token"]

    def test_it_should_return_all_ticket_related_pteam_user_belongs(self):
        response = client.get("/tickets", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tickets"]) == 2

        # Expected set of ticket IDs
        expected_ticket_ids = {
            self.ticket_response1["ticket_id"],
            self.ticket_response2["ticket_id"],
        }
        actual_ticket_ids = {t["ticket_id"] for t in data["tickets"]}
        assert actual_ticket_ids == expected_ticket_ids

        # Expected ticket information
        expected_tickets = {
            self.ticket_response1["ticket_id"]: {
                "pteam_id": self.ticket_response1["pteam_id"],
                "vuln_id": self.ticket_response1["vuln_id"],
            },
            self.ticket_response2["ticket_id"]: {
                "pteam_id": self.ticket_response2["pteam_id"],
                "vuln_id": self.ticket_response2["vuln_id"],
            },
        }

        for ticket in data["tickets"]:
            assert ticket["ticket_id"] in expected_tickets
            expected = expected_tickets[ticket["ticket_id"]]
            assert ticket["pteam_id"] == expected["pteam_id"]
            assert ticket["vuln_id"] == expected["vuln_id"]
            for field in [
                "ticket_id",
                "vuln_id",
                "dependency_id",
                "service_id",
                "pteam_id",
                "created_at",
                "ssvc_deployer_priority",
                "ticket_status",
            ]:
                assert field in ticket

    def test_it_should_not_get_tickets_for_other_pteams(self, testdb):
        # Setup: create a third pteam and ticket
        PTEAM3 = {
            "pteam_name": "pteam charlie",
            "contact_info": "charlie@ml.com",
            "alert_slack": {"enable": True, "webhook_url": ""},
            "alert_ssvc_priority": "scheduled",
            "alert_mail": {"enable": False, "address": "charlie@ml.com"},
        }
        user3 = create_user(USER3)
        pteam3 = create_pteam(USER3, PTEAM3)
        vuln3 = create_vuln(USER3, VULN3)
        ticket_response4 = self._create_ticket_with_threat(testdb, user3, pteam3, "service4", vuln3)

        # Try to get tickets for pteam3 (not a member)
        response = client.get(
            f"/tickets?pteam_ids={pteam3.pteam_id}",
            headers=headers(USER1),
        )
        # Should not return the ticket for pteam3
        data = response.json()
        ticket_ids = {t["ticket_id"] for t in data.get("tickets", [])}
        assert ticket_response4["ticket_id"] not in ticket_ids

    def test_it_should_get_my_tasks(self):
        response = client.get("/tickets?assigned_to_me=true", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["ticket_id"] == self.ticket_response1["ticket_id"]

    def test_it_should_paginate(self):
        response = client.get("/tickets?offset=0&limit=1", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tickets"]) == 1

        response2 = client.get("/tickets?offset=1&limit=1", headers=headers(USER1))
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        assert len(data2["tickets"]) == 1

    def test_it_should_filter_by_pteam_ids(self):
        dummy_pteam_id = str(uuid4())
        response = client.get(f"/tickets?pteam_ids={dummy_pteam_id}", headers=headers(USER1))
        assert response.status_code == 400

        response2 = client.get(f"/tickets?pteam_ids={self.pteam1.pteam_id}", headers=headers(USER1))
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        assert len(data2["tickets"]) == 2

    def test_it_should_get_tickets_for_multiple_pteam_ids(self, testdb):
        # Create the second PTeam and its ticket
        user2 = create_user(USER2)
        pteam2 = create_pteam(USER2, PTEAM2)
        # Invite USER1 to pteam2 and accept the invitation
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        vuln2 = create_vuln(USER2, VULN2)
        ticket_response3 = self._create_ticket_with_threat(testdb, user2, pteam2, "service3", vuln2)

        # Define and create the third PTeam and its ticket within the test
        PTEAM3 = {
            "pteam_name": "pteam charlie",
            "contact_info": "charlie@ml.com",
            "alert_slack": {"enable": True, "webhook_url": ""},
            "alert_ssvc_priority": "scheduled",
            "alert_mail": {"enable": False, "address": "charlie@ml.com"},
        }
        user3 = create_user(USER3)
        pteam3 = create_pteam(USER3, PTEAM3)
        vuln3 = create_vuln(USER3, VULN3)
        ticket_response4 = self._create_ticket_with_threat(testdb, user3, pteam3, "service4", vuln3)

        # Get tickets by specifying two pteam_ids (self.pteam1, pteam2)
        response = client.get(
            f"/tickets?pteam_ids={self.pteam1.pteam_id}&pteam_ids={pteam2.pteam_id}",
            headers=headers(USER1),
        )
        assert response.status_code == 200
        data = response.json()
        ticket_ids = {t["ticket_id"] for t in data["tickets"]}
        # Tickets for self.pteam1 and pteam2 should be included
        assert self.ticket_response1["ticket_id"] in ticket_ids
        assert self.ticket_response2["ticket_id"] in ticket_ids
        assert ticket_response3["ticket_id"] in ticket_ids
        # Ticket for pteam3 should NOT be included
        assert ticket_response4["ticket_id"] not in ticket_ids
        # There should be a total of 3 tickets
        assert data["total"] == 3
        assert len(data["tickets"]) == 3
