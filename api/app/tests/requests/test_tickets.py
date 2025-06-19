from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
    VULN1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
    set_ticket_status,
)

client = TestClient(app)


class TestGetTickets:
    @staticmethod
    def create_ticket_with_threat(testdb: Session, user, pteam, service_name: str, vuln):

        # Serviceを作成
        service = models.Service(
            pteam_id=str(pteam.pteam_id),
            service_name=service_name,
        )
        testdb.add(service)
        testdb.flush()

        package_name = f"testpkg_{service_name}"
        package = models.Package(
            name=package_name,
            ecosystem="pypi",
        )
        testdb.add(package)
        testdb.flush()

        # PackageVersionを作成
        package_version = models.PackageVersion(
            version="1.0.0",
            package_id=package.package_id,
        )
        testdb.add(package_version)
        testdb.flush()

        # Dependencyを作成
        dependency = models.Dependency(
            service_id=service.service_id,
            package_version_id=package_version.package_version_id,
            target="default",
            package_manager="pip",
        )
        testdb.add(dependency)
        testdb.flush()

        # Threatを作成
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
            vuln_status=models.VulnStatusType.alerted,  # 初期値として "alerted" など
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

    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        user = create_user(USER1)
        pteam = create_pteam(USER1, PTEAM1)
        vuln = create_vuln(USER1, VULN1)
        self.pteam = pteam

        # 1件目のチケット
        service_name1 = "test_service1"
        self.ticket_response1 = self.create_ticket_with_threat(
            testdb, user, pteam, service_name1, vuln
        )
        json_data1 = {
            "vuln_status": "acknowledged",
            "note": "string",
            "assignees": [str(user.user_id)],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data1,
        )

        # 2件目のチケット
        service_name2 = "test_service2"
        self.ticket_response2 = self.create_ticket_with_threat(
            testdb, user, pteam, service_name2, vuln
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

        # チケットIDを保持
        self.ticket1 = {"ticket_id": self.ticket_response1["ticket_id"]}
        self.ticket2 = {"ticket_id": self.ticket_response2["ticket_id"]}

    def test_it_should_get_all_tickets(self):
        response = client.get("/tickets", headers=headers(user=USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["offset"] == 0
        assert data["limit"] == 100
        assert len(data["tickets"]) == 2
        ticket_ids = {t["ticket_id"] for t in data["tickets"]}
        assert self.ticket1["ticket_id"] in ticket_ids
        assert self.ticket2["ticket_id"] in ticket_ids

    def test_it_should_get_my_tasks(self):
        response = client.get("/tickets?my_tasks=true", headers=headers(user=USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["ticket_id"] == self.ticket1["ticket_id"]

    def test_it_should_paginate(self):
        response = client.get("/tickets?offset=0&limit=1", headers=headers(user=USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["offset"] == 0
        assert data["limit"] == 1
        assert len(data["tickets"]) == 1

        response2 = client.get("/tickets?offset=1&limit=1", headers=headers(user=USER1))
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        assert data2["offset"] == 1
        assert data2["limit"] == 1
        assert len(data2["tickets"]) == 1
        assert data["tickets"][0]["ticket_id"] != data2["tickets"][0]["ticket_id"]

    def test_it_should_filter_by_pteam_ids(self):
        dummy_pteam_id = str(uuid4())
        response = client.get(f"/tickets?pteam_ids={dummy_pteam_id}", headers=headers(user=USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["tickets"]) == 0

        response2 = client.get(
            f"/tickets?pteam_ids={self.pteam.pteam_id}", headers=headers(user=USER1)
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        assert len(data2["tickets"]) == 2
