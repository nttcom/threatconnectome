from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import persistence
from app.main import app
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
    get_service_by_service_name,
    get_tickets_related_to_vuln_package,
    headers,
    invite_to_pteam,
    set_ticket_status,
    upload_pteam_packages,
)

client = TestClient(app)

SSVC_PRIORITY_ORDER = {
    "immediate": 4,
    "out_of_cycle": 3,
    "scheduled": 2,
    "defer": 1,
}


@pytest.fixture(scope="function", autouse=True)
def ticket_setup(testdb):
    # user・PTeam
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER2, PTEAM2)
    PTEAM3 = {
        "pteam_name": "pteam charlie",
        "contact_info": "charlie@ml.com",
        "alert_slack": {"enable": True, "webhook_url": ""},
        "alert_ssvc_priority": "scheduled",
        "alert_mail": {"enable": False, "address": "charlie@ml.com"},
    }
    pteam3 = create_pteam(USER3, PTEAM3)

    # vuln
    VULN1_FIX = {**VULN1, "package_name": "axios"}
    VULN2_FIX = {
        **VULN2,
        "exploitation": "public_poc",
        "automatable": "no",
        "package_name": "asynckit",
    }
    VULN3_FIX = {
        **VULN3,
        "package_name": "leftpad",
        "vulnerable_packages": [
            {
                "affected_name": "leftpad",
                "ecosystem": "npm",
                "affected_versions": ["<2.0"],
                "fixed_versions": ["2.0"],
            }
        ],
    }
    vuln1 = create_vuln(USER1, VULN1_FIX)
    vuln2 = create_vuln(USER2, VULN2_FIX)
    vuln3 = create_vuln(USER3, VULN3_FIX)

    # refs
    refs1 = [
        {
            "package_name": "axios",
            "ecosystem": "npm",
            "package_manager": "npm",
            "references": [{"target": "target1", "version": "1.0"}],
        }
    ]
    refs2 = [
        {
            "package_name": "asynckit",
            "ecosystem": "npm",
            "package_manager": "npm",
            "references": [{"target": "target2", "version": "1.0"}],
        }
    ]
    refs3 = [
        {
            "package_name": "leftpad",
            "ecosystem": "npm",
            "package_manager": "npm",
            "references": [{"target": "target3", "version": "1.0"}],
        }
    ]

    service_name1 = "test_service1"
    service_name2 = "test_service2"
    service_name3 = "test_service3"
    upload_pteam_packages(USER1, pteam1.pteam_id, service_name1, refs1)
    upload_pteam_packages(USER2, pteam2.pteam_id, service_name2, refs2)
    upload_pteam_packages(USER3, pteam3.pteam_id, service_name3, refs3)

    service1 = get_service_by_service_name(USER1, pteam1.pteam_id, service_name1)
    service2 = get_service_by_service_name(USER2, pteam2.pteam_id, service_name2)
    service3 = get_service_by_service_name(USER3, pteam3.pteam_id, service_name3)

    package1 = persistence.get_package_by_name_and_ecosystem_and_source_name(
        testdb, "axios", "npm", None
    )
    package2 = persistence.get_package_by_name_and_ecosystem_and_source_name(
        testdb, "asynckit", "npm", None
    )
    package3 = persistence.get_package_by_name_and_ecosystem_and_source_name(
        testdb, "leftpad", "npm", None
    )

    # tickets
    tickets1 = get_tickets_related_to_vuln_package(  # ssvc_deployer_priority: immediate
        USER1, pteam1.pteam_id, service1["service_id"], vuln1.vuln_id, package1.package_id
    )
    tickets2 = get_tickets_related_to_vuln_package(  # ssvc_deployer_priority: out_of_cycle
        USER2, pteam2.pteam_id, service2["service_id"], vuln2.vuln_id, package2.package_id
    )
    tickets3 = get_tickets_related_to_vuln_package(  # ssvc_deployer_priority: scheduled
        USER3, pteam3.pteam_id, service3["service_id"], vuln3.vuln_id, package3.package_id
    )

    ticket1 = tickets1[0]
    ticket2 = tickets2[0]
    ticket3 = tickets3[0]

    # ticket_status
    set_ticket_status(
        USER1,
        pteam1.pteam_id,
        ticket1["ticket_id"],
        {
            "vuln_status": "acknowledged",
            "assignees": [str(user1.user_id)],
            "note": "",
            "scheduled_at": None,
        },
    )
    set_ticket_status(
        USER2,
        pteam2.pteam_id,
        ticket2["ticket_id"],
        {"vuln_status": "acknowledged", "assignees": [], "note": "", "scheduled_at": None},
    )
    set_ticket_status(
        USER3,
        pteam3.pteam_id,
        ticket3["ticket_id"],
        {"vuln_status": "acknowledged", "assignees": [], "note": "", "scheduled_at": None},
    )

    return {
        "user1": user1,
        "user2": user2,
        "user3": user3,
        "pteam1": pteam1,
        "pteam2": pteam2,
        "pteam3": pteam3,
        "service1": service1,
        "service2": service2,
        "service3": service3,
        "package1": package1,
        "package2": package2,
        "package3": package3,
        "vuln1": vuln1,
        "vuln2": vuln2,
        "vuln3": vuln3,
        "ticket1": ticket1,
        "ticket2": ticket2,
        "ticket3": ticket3,
    }


class TestGetTickets:
    def test_it_should_return_all_ticket_related_pteam_user_belongs(self, ticket_setup):
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        ticket1 = ticket_setup["ticket1"]
        ticket2 = ticket_setup["ticket2"]

        response = client.get("/tickets", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tickets"]) == 2

        expected_ticket_ids = {
            ticket1["ticket_id"],
            ticket2["ticket_id"],
        }
        actual_ticket_ids = {t["ticket_id"] for t in data["tickets"]}
        assert actual_ticket_ids == expected_ticket_ids

        expected_tickets = {
            ticket1["ticket_id"]: {
                "pteam_id": str(pteam1.pteam_id),
                "vuln_id": str(ticket_setup["vuln1"].vuln_id),
            },
            ticket2["ticket_id"]: {
                "pteam_id": str(pteam2.pteam_id),
                "vuln_id": str(ticket_setup["vuln2"].vuln_id),
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

    def test_it_should_not_get_tickets_for_other_pteams(self, ticket_setup):
        pteam3 = ticket_setup["pteam3"]
        ticket3 = ticket_setup["ticket3"]

        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={"pteam_ids": str(pteam3.pteam_id)},
        )
        data = response.json()
        ticket_ids = {t["ticket_id"] for t in data.get("tickets", [])}
        assert ticket3["ticket_id"] not in ticket_ids

    def test_it_should_get_my_tasks(self, ticket_setup):
        ticket1 = ticket_setup["ticket1"]

        response = client.get(
            "/tickets?", headers=headers(USER1), params={"assigned_to_me": "true"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["ticket_id"] == ticket1["ticket_id"]

    def test_it_should_paginate(self, ticket_setup):
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        response = client.get("/tickets?", headers=headers(USER1), params={"offset": 0, "limit": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tickets"]) == 1

        response2 = client.get(
            "/tickets?", headers=headers(USER1), params={"offset": 1, "limit": 1}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        assert len(data2["tickets"]) == 1

    def test_it_should_filter_by_pteam_ids(self, ticket_setup):
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        dummy_pteam_id = str(uuid4())
        response = client.get(
            "/tickets?", headers=headers(USER1), params={"pteam_ids": dummy_pteam_id}
        )
        assert response.status_code == 400

        response2 = client.get(
            "/tickets?", headers=headers(USER1), params={"pteam_ids": pteam1.pteam_id}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert len(data2["tickets"]) == 1

    def test_it_should_get_tickets_for_multiple_pteam_ids(self, ticket_setup):
        pteam2 = ticket_setup["pteam2"]
        pteam2 = ticket_setup["pteam2"]
        ticket1 = ticket_setup["ticket1"]
        ticket2 = ticket_setup["ticket2"]
        ticket3 = ticket_setup["ticket3"]

        # Invite USER1 to pteam2 and accept the invitation
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={"pteam_ids": [str(ticket_setup["pteam1"].pteam_id), str(pteam2.pteam_id)]},
        )
        assert response.status_code == 200
        data = response.json()
        ticket_ids = {t["ticket_id"] for t in data["tickets"]}
        # Tickets for pteam1 and pteam2 should be included
        assert ticket1["ticket_id"] in ticket_ids
        assert ticket2["ticket_id"] in ticket_ids
        # Ticket for pteam3 should NOT be included
        assert ticket3["ticket_id"] not in ticket_ids
        # There should be a total of 3 tickets (after invitation acceptance and ticket creation)
        assert data["total"] == 2
        assert len(data["tickets"]) == 2

    def test_it_should_sort_asc(self, ticket_setup):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        pteam3 = ticket_setup["pteam3"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        invitation = invite_to_pteam(USER3, pteam3.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "sort_keys": ["ssvc_deployer_priority"],
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id), str(pteam3.pteam_id)],
            },
        )

        # Then
        assert response.status_code == 200
        tickets = response.json()["tickets"]

        # SSVC priority ascending
        sorted_tickets = sorted(
            tickets,
            key=lambda t: (SSVC_PRIORITY_ORDER.get(t["ssvc_deployer_priority"], 99)),
        )
        assert tickets == sorted_tickets

    def test_it_should_sort_desc(self, ticket_setup):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        pteam3 = ticket_setup["pteam3"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        invitation = invite_to_pteam(USER3, pteam3.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "sort_keys": ["-ssvc_deployer_priority"],
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id), str(pteam3.pteam_id)],
            },
        )

        # Then
        assert response.status_code == 200
        tickets = response.json()["tickets"]

        # SSVC priority descending
        sorted_tickets = sorted(
            tickets,
            key=lambda t: (SSVC_PRIORITY_ORDER.get(t["ssvc_deployer_priority"], 99)),
            reverse=True,
        )
        assert tickets == sorted_tickets

    def test_it_should_sort_multiple(self, ticket_setup):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        pteam3 = ticket_setup["pteam3"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        invitation = invite_to_pteam(USER3, pteam3.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "sort_keys": [
                    "ssvc_deployer_priority",
                    "created_at",
                    "scheduled_at",
                    "cve_id",
                    "package_name",
                    "pteam_name",
                    "service_name",
                ],
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id), str(pteam3.pteam_id)],
            },
        )

        # Then
        assert response.status_code == 200
        tickets = response.json()["tickets"]

        sorted_tickets = sorted(
            tickets,
            key=lambda t: (
                SSVC_PRIORITY_ORDER.get(
                    t["ssvc_deployer_priority"],
                    99,
                )
            ),
        )
        assert tickets == sorted_tickets

    @pytest.mark.parametrize(
        "cve_ids, expected_tickets, expected_count",
        [
            # Filter by single CVE ID - VULN1
            (["CVE-0000-0001"], ["ticket1"], 1),
            # Filter by multiple CVE IDs - both exist
            (["CVE-0000-0001", "CVE-0000-0002"], ["ticket1", "ticket2"], 2),
            # Filter by non-existent CVE ID
            (["CVE-9999-9999"], [], 0),
        ],
    )
    def test_it_should_filter_by_cve_ids(
        self, ticket_setup, cve_ids, expected_tickets, expected_count
    ):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id)],
                "cve_ids": cve_ids,
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == expected_count
        assert len(data["tickets"]) == expected_count

        for ticket in data["tickets"]:
            assert ticket["ticket_id"] in {
                ticket_setup[key]["ticket_id"] for key in expected_tickets
            }

    @pytest.mark.parametrize(
        "cve_ids, expected_error",
        [
            (["INVALID-CVE-ID"], "Invalid input: Invalid CVE ID format: INVALID-CVE-ID"),
            (
                ["CVE-0000-0001", "INVALID-CVE-ID"],
                "Invalid input: Invalid CVE ID format: INVALID-CVE-ID",
            ),
        ],
    )
    def test_it_should_return_400_for_invalid_cve_id_format(
        self, ticket_setup, cve_ids, expected_error
    ):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)
        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id)],
                "cve_ids": cve_ids,
            },
        )
        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert error_data["detail"] == expected_error

    def test_it_should_return_400_for_invalid_sort_keys(self, ticket_setup):
        # Given
        pteam1 = ticket_setup["pteam1"]
        pteam2 = ticket_setup["pteam2"]
        invitation = invite_to_pteam(USER2, pteam2.pteam_id)
        accept_pteam_invitation(USER1, invitation.invitation_id)

        # When
        response = client.get(
            "/tickets",
            headers=headers(USER1),
            params={
                "sort_keys": ["wrong_sort_key"],
                "pteam_ids": [str(pteam1.pteam_id), str(pteam2.pteam_id)],
            },
        )

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert error_data["detail"] == "Invalid input: Invalid sort key: wrong_sort_key"


class TestCreateInsight:
    def test_it_should_create_insight(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
            "threat_scenarios": [
                {
                    "impact_category": "denial_of_control",
                    "title": "example threat_scenario title1",
                    "description": "example threat_scenario description1",
                },
                {
                    "impact_category": "manipulation_of_view",
                    "title": "example threat_scenario title2",
                    "description": "example threat_scenario description2",
                },
            ],
            "affected_objects": [
                {
                    "object_category": "person",
                    "name": "example affected_object name1",
                    "description": "example affected_object description1",
                },
                {
                    "object_category": "mobile_device",
                    "name": "example affected_object name2",
                    "description": "example affected_object description2",
                },
            ],
            "insight_references": [
                {
                    "link_text": "example link_text1",
                    "url": "example url1",
                },
                {
                    "link_text": "example link_text2",
                    "url": "example url2",
                },
            ],
        }

        # When
        ticket_id = ticket1["ticket_id"]
        response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["ticket_id"] == ticket_id

        now = datetime.now(timezone.utc)
        assert (
            now - timedelta(seconds=3)
            <= datetime.fromisoformat(response_data["created_at"].replace("Z", "+00:00"))
            <= now
        )
        assert (
            now - timedelta(seconds=3)
            <= datetime.fromisoformat(response_data["updated_at"].replace("Z", "+00:00"))
            <= now
        )

        response_data.pop("ticket_id", None)
        response_data.pop("created_at", None)
        response_data.pop("updated_at", None)
        assert response_data == insight_request

    def test_raise_404_if_ticket_id_does_not_exist(self):
        # Given
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
        }

        # When
        ticket_id = str(uuid4())
        response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such ticket"

    def test_it_should_return_403_when_not_pteam_member(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
        }

        # When
        ticket_id = ticket1["ticket_id"]
        response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER2),
            json=insight_request,
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"

    def test_it_should_return_409_when_specified_duplicate_ticlket_id(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
        }
        ticket_id = ticket1["ticket_id"]
        response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        # When
        response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        # Then
        assert response.status_code == 409
        assert response.json()["detail"] == "Insight is already registered for this ticket"


class TestGetInsight:
    def test_it_should_get_insight(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        ticket_id = ticket1["ticket_id"]

        insight_request = {
            "description": "Detailed insight description",
            "reasoning_and_planning": "Comprehensive reasoning and planning",
            "threat_scenarios": [
                {
                    "impact_category": "denial_of_control",
                    "title": "Scenario 1",
                    "description": "Description 1",
                },
                {
                    "impact_category": "manipulation_of_view",
                    "title": "Scenario 2",
                    "description": "Description 2",
                },
            ],
            "affected_objects": [
                {
                    "object_category": "person",
                    "name": "Object 1",
                    "description": "Object Description 1",
                },
                {
                    "object_category": "mobile_device",
                    "name": "Object 2",
                    "description": "Object Description 2",
                },
            ],
            "insight_references": [
                {
                    "link_text": "Reference 1",
                    "url": "https://example1.com",
                },
                {
                    "link_text": "Reference 2",
                    "url": "https://example2.com",
                },
            ],
        }

        # Create insight
        client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        # When
        response = client.get(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()

        assert response_data["ticket_id"] == ticket_id
        assert response_data["description"] == insight_request["description"]
        assert response_data["reasoning_and_planning"] == insight_request["reasoning_and_planning"]

        # Verify threat scenarios
        assert len(response_data["threat_scenarios"]) == 2
        for i, scenario in enumerate(response_data["threat_scenarios"]):
            expected = insight_request["threat_scenarios"][i]
            assert scenario["impact_category"] == expected["impact_category"]
            assert scenario["title"] == expected["title"]
            assert scenario["description"] == expected["description"]

        # Verify affected objects
        assert len(response_data["affected_objects"]) == 2
        for i, obj in enumerate(response_data["affected_objects"]):
            expected = insight_request["affected_objects"][i]
            assert obj["object_category"] == expected["object_category"]
            assert obj["name"] == expected["name"]
            assert obj["description"] == expected["description"]

        # Verify insight references
        assert len(response_data["insight_references"]) == 2
        for i, ref in enumerate(response_data["insight_references"]):
            expected = insight_request["insight_references"][i]
            assert ref["link_text"] == expected["link_text"]
            assert ref["url"] == expected["url"]

    def test_it_should_return_404_when_insight_not_exists(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        ticket_id = ticket1["ticket_id"]

        # When - get Insight for a ticket that does not have one
        response = client.get(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "No insight found for this ticket"

    def test_it_should_return_403_when_not_pteam_member(self, ticket_setup):
        # Given
        ticket1 = ticket_setup["ticket1"]
        ticket_id = ticket1["ticket_id"]

        # Create insight as USER1 (pteam member)
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
            "threat_scenarios": [],
            "affected_objects": [],
            "insight_references": [],
        }

        create_response = client.post(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER1),
            json=insight_request,
        )
        assert create_response.status_code == 200

        # When - USER2 (not a pteam member) tries to get insight
        response = client.get(
            f"/tickets/{ticket_id}/insight",
            headers=headers(USER2),
        )

        # Then
        assert response.status_code == 403
        error_data = response.json()
        assert error_data["detail"] == "Not a pteam member"

    def test_it_should_return_404_when_ticket_not_exists(self, ticket_setup):
        # Given
        non_existent_ticket_id = str(uuid4())

        # When
        response = client.get(
            f"/tickets/{non_existent_ticket_id}/insight",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "No such ticket"


class TestDeleteInsight:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, ticket_setup):
        ticket1 = ticket_setup["ticket1"]
        insight_request = {
            "description": "example insight description",
            "reasoning_and_planning": "example reasoning and planning",
            "threat_scenarios": [
                {
                    "impact_category": "denial_of_control",
                    "title": "example threat_scenario title1",
                    "description": "example threat_scenario description1",
                },
                {
                    "impact_category": "manipulation_of_view",
                    "title": "example threat_scenario title2",
                    "description": "example threat_scenario description2",
                },
            ],
            "affected_objects": [
                {
                    "object_category": "person",
                    "name": "example affected_object name1",
                    "description": "example affected_object description1",
                },
                {
                    "object_category": "mobile_device",
                    "name": "example affected_object name2",
                    "description": "example affected_object description2",
                },
            ],
            "insight_references": [
                {
                    "link_text": "example link_text1",
                    "url": "example url1",
                },
                {
                    "link_text": "example link_text2",
                    "url": "example url2",
                },
            ],
        }

        response = client.post(
            f"/tickets/{ticket1['ticket_id']}/insight",
            headers=headers(USER1),
            json=insight_request,
        )

        self.response_insight = response.json()

    def test_it_should_return_204_for_delete_insight(self):
        # When
        response = client.delete(
            f"/tickets/{self.response_insight['ticket_id']}/insight", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 204

        # Todo: get API created and implemented
        # delete_insight = client.get(
        #     f"/tickets/{self.response_insight['ticket_id']}/insight", headers=headers(USER1)
        # )
        # assert delete_insight is None

    def test_it_should_return_404_for_non_existent_ticket(self):
        # Given
        non_existent_ticket_id = str(uuid4())

        # When
        response = client.delete(
            f"/tickets/{non_existent_ticket_id}/insight", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such ticket"

    def test_it_should_return_404_When_there_is_no_insight_associated_with_ticket_id(self):
        # Given
        client.delete(
            f"/tickets/{self.response_insight['ticket_id']}/insight", headers=headers(USER1)
        )

        # When
        response = client.delete(
            f"/tickets/{self.response_insight['ticket_id']}/insight", headers=headers(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No insight associated with this ticket"

    def test_it_should_return_403_for_insight_deletion_by_non_pteam_member(self):
        # When
        response = client.delete(
            f"/tickets/{self.response_insight['ticket_id']}/insight", headers=headers(USER2)
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Not a pteam member"
