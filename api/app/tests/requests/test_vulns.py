from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.constants import PTEAM1, USER1, USER2
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
        self.request1 = {
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
            created_at=datetime(2025, 4, 15, 12, 0, 0),
            updated_at=datetime(2025, 4, 15, 12, 0, 0),
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

        self.affect1 = models.Affect(
            vuln_id=self.vuln1.vuln_id,
            package_id=self.package1.package_id,
            affected_versions=["<2.0.0"],
            fixed_versions=["2.0.0"],
        )

        testdb.add(self.affect1)

        testdb.commit()

    def test_return_VulnResponse_when_create_vuln_successfully(self):
        # Given
        new_vuln_id = uuid4()
        current_time = datetime.now()

        # When
        response = client.put(f"/vulns/{new_vuln_id}", headers=headers(USER1), json=self.request1)

        # Then
        assert response.status_code == 200
        assert response.json()["vuln_id"] == str(new_vuln_id)
        assert response.json()["title"] == self.request1["title"]
        assert response.json()["created_by"] == str(self.user1.user_id)
        assert response.json()["cve_id"] == self.request1["cve_id"]
        assert response.json()["detail"] == self.request1["detail"]
        assert response.json()["exploitation"] == self.request1["exploitation"]
        assert response.json()["automatable"] == self.request1["automatable"]
        assert response.json()["cvss_v3_score"] == self.request1["cvss_v3_score"]
        assert (
            response.json()["vulnerable_packages"][0]["name"]
            == self.request1["vulnerable_packages"][0]["name"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["ecosystem"]
            == self.request1["vulnerable_packages"][0]["ecosystem"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["affected_versions"]
            == self.request1["vulnerable_packages"][0]["affected_versions"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["fixed_versions"]
            == self.request1["vulnerable_packages"][0]["fixed_versions"]
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"])
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"])
            <= current_time + timedelta(seconds=10)
        )

    def test_return_default_value_when_exploitation_and_automatable_are_missing(self):
        # Given
        new_vuln_id = uuid4()
        request2 = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
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
        # When
        response = client.put(f"/vulns/{new_vuln_id}", headers=headers(USER1), json=request2)
        # Then
        assert response.status_code == 200
        assert response.json()["exploitation"] == models.ExploitationEnum.NONE
        assert response.json()["automatable"] == models.AutomatableEnum.NO

    def test_return_VulnResponse_when_update_vuln_successfully(self, update_setup):
        # Given
        created_time = self.vuln1.created_at
        current_time = datetime.now()
        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=self.request1
        )

        # Then
        assert response.status_code == 200
        assert response.json()["vuln_id"] == str(self.vuln1.vuln_id)
        assert response.json()["title"] == self.request1["title"]
        assert response.json()["created_by"] == str(self.user1.user_id)
        assert response.json()["cve_id"] == self.request1["cve_id"]
        assert response.json()["detail"] == self.request1["detail"]
        assert response.json()["exploitation"] == self.request1["exploitation"]
        assert response.json()["automatable"] == self.request1["automatable"]
        assert response.json()["cvss_v3_score"] == self.request1["cvss_v3_score"]
        assert (
            response.json()["vulnerable_packages"][0]["name"]
            == self.request1["vulnerable_packages"][0]["name"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["ecosystem"]
            == self.request1["vulnerable_packages"][0]["ecosystem"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["affected_versions"]
            == self.request1["vulnerable_packages"][0]["affected_versions"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["fixed_versions"]
            == self.request1["vulnerable_packages"][0]["fixed_versions"]
        )

        assert (
            created_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"])
            <= created_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"])
            <= current_time + timedelta(seconds=10)
        )

    def test_raise_400_if_given_vuln_id_is_default_vuln_id(self):
        # Given
        default_vuln_id = UUID(int=0)

        # When
        response = client.put(
            f"/vulns/{default_vuln_id}", headers=headers(USER1), json=self.request1
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot create default vuln"

    def test_raise_400_if_requested_title_is_None(self):
        # Given
        new_vuln_id = uuid4()
        title_none_request = {
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
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=title_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_requested_detail_is_None(self):
        # Given
        new_vuln_id = uuid4()
        detail_none_request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
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
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=detail_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_cvss_v3_score_is_out_of_range(self):
        # Given
        new_vuln_id = uuid4()
        out_of_range_cvss_request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 9999.9999,
            "vulnerable_packages": [
                {
                    "name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers(USER1), json=out_of_range_cvss_request
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"

    def test_raise_403_if_current_user_is_not_vuln_creator(self, update_setup):
        # Given
        create_user(USER2)

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER2), json=self.request1
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "You are not vuln creator"

    @pytest.mark.parametrize(
        "field_name",
        [
            "title",
            "detail",
            "exploitation",
            "automatable",
        ],
    )
    def test_raise_400_if_field_update_with_none(self, update_setup, field_name):
        # Given
        invalid_request: dict[str, Any] = {
            f"{field_name}": None,
        }

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=invalid_request
        )

        assert response.status_code == 400
        assert response.json()["detail"] == f"Cannot specify None for {field_name}"

    def test_raise_400_if_cvss_v3_score_update_with_out_of_range(
        self, testdb: Session, update_setup
    ):
        # Given
        invalid_request: dict[str, Any] = {
            "cvss_v3_score": 9999.9999,
        }

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers(USER1), json=invalid_request
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"


class TestGetVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # Given
        self.user1 = create_user(USER1)
        self.new_vuln_id = uuid4()
        self.request1 = {
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
            f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=self.request1
        )
        self.created_time = datetime.fromisoformat(response.json()["created_at"])
        self.updated_time = datetime.fromisoformat(response.json()["updated_at"])

    def test_it_should_return_200_when_vuln_id_is_correctly_registered(self):
        # When
        response = client.get(f"/vulns/{self.new_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        assert response.json()["vuln_id"] == str(self.new_vuln_id)
        assert response.json()["title"] == self.request1["title"]
        assert response.json()["cve_id"] == self.request1["cve_id"]
        assert response.json()["detail"] == self.request1["detail"]
        assert response.json()["exploitation"] == self.request1["exploitation"]
        assert response.json()["automatable"] == self.request1["automatable"]
        assert response.json()["cvss_v3_score"] == self.request1["cvss_v3_score"]
        assert (
            response.json()["vulnerable_packages"][0]["name"]
            == self.request1["vulnerable_packages"][0]["name"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["ecosystem"]
            == self.request1["vulnerable_packages"][0]["ecosystem"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["affected_versions"]
            == self.request1["vulnerable_packages"][0]["affected_versions"]
        )
        assert (
            response.json()["vulnerable_packages"][0]["fixed_versions"]
            == self.request1["vulnerable_packages"][0]["fixed_versions"]
        )

        assert (
            self.created_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"])
            <= self.created_time + timedelta(seconds=10)
        )
        assert (
            self.updated_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"])
            <= self.updated_time + timedelta(seconds=10)
        )

    def test_it_should_return_400_when_vuln_id_is_not_registered(self):
        # Given
        not_registered_vuln_id = str(uuid4())

        # When
        response = client.get(f"/vulns/{not_registered_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such vuln"


class TestGetVulns:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        # Given
        self.user1 = create_user(USER1)
        self.headers_user = headers(USER1)

    def test_it_should_return_200_and_vulns_list(self, testdb: Session):
        # Given
        vuln_ids = []
        number_of_vulns = 10
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = {
                "title": f"Example vuln {i}",
                "cve_id": f"CVE-0000-000{i}",
                "detail": f"This is example vuln {i}.",
                "exploitation": "active",
                "automatable": "yes",
                "cvss_v3_score": 7.5,
                "vulnerable_packages": [
                    {
                        "name": f"example-lib-{i}",
                        "ecosystem": "pypi",
                        "affected_versions": ["<2.0.0"],
                        "fixed_versions": ["2.0.0"],
                    }
                ],
            }
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)
            created_times.append(datetime.fromisoformat(response.json()["created_at"]))
            updated_times.append(datetime.fromisoformat(response.json()["updated_at"]))
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        response_data.reverse()
        assert len(response_data) == number_of_vulns  # Ensure all created vulns are returned

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            assert vuln["vuln_id"] == str(vuln_ids[i])
            assert vuln["title"] == f"Example vuln {i}"
            assert vuln["cve_id"] == f"CVE-0000-000{i}"
            assert vuln["detail"] == f"This is example vuln {i}."
            assert vuln["exploitation"] == "active"
            assert vuln["automatable"] == "yes"
            assert vuln["cvss_v3_score"] == 7.5
            assert vuln["vulnerable_packages"][0]["name"] == f"example-lib-{i}"
            assert vuln["vulnerable_packages"][0]["ecosystem"] == "pypi"
            assert vuln["vulnerable_packages"][0]["affected_versions"] == ["<2.0.0"]
            assert vuln["vulnerable_packages"][0]["fixed_versions"] == ["2.0.0"]
            assert (
                created_times[i] - timedelta(seconds=10)
                <= datetime.fromisoformat(vuln["created_at"])
                <= created_times[i] + timedelta(seconds=10)
            )
            assert (
                updated_times[i] - timedelta(seconds=10)
                <= datetime.fromisoformat(vuln["updated_at"])
                <= updated_times[i] + timedelta(seconds=10)
            )

    def test_it_should_return_empty_list_when_no_vulns_exist(self):
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []  # Ensure no vulns are returned

    def test_it_should_return_correct_number_of_vulns_with_limit(self, testdb: Session):
        # Given
        number_of_vulns = 5
        for i in range(number_of_vulns):
            vuln_request = {
                "title": f"Example vuln {i}",
                "cve_id": f"CVE-0000-000{i}",
                "detail": f"This is example vuln {i}.",
                "exploitation": "active",
                "automatable": "yes",
                "cvss_v3_score": 7.5,
                "vulnerable_packages": [
                    {
                        "name": f"example-lib-{i}",
                        "ecosystem": "pypi",
                        "affected_versions": ["<2.0.0"],
                        "fixed_versions": ["2.0.0"],
                    }
                ],
            }
            client.put(f"/vulns/{uuid4()}", headers=self.headers_user, json=vuln_request)

        # When
        response = client.get("/vulns?offset=0&limit=2", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2  # Ensure only 2 vulns are returned

    def test_it_should_return_correct_vulns_with_offset(self, testdb: Session):
        # Given
        number_of_vulns = 5
        vuln_ids = []
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = {
                "title": f"Example vuln {i}",
                "cve_id": f"CVE-0000-000{i}",
                "detail": f"This is example vuln {i}.",
                "exploitation": "active",
                "automatable": "yes",
                "cvss_v3_score": 7.5,
                "vulnerable_packages": [
                    {
                        "name": f"example-lib-{i}",
                        "ecosystem": "pypi",
                        "affected_versions": ["<2.0.0"],
                        "fixed_versions": ["2.0.0"],
                    }
                ],
            }
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)
            created_times.append(datetime.fromisoformat(response.json()["created_at"]))
            updated_times.append(datetime.fromisoformat(response.json()["updated_at"]))

        # When
        response = client.get("/vulns?offset=1&limit=4", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 4  # Ensure 4 vulns are returned
        assert response_data[0]["vuln_id"] == str(vuln_ids[3])  # Ensure offset is applied
        assert response_data[0]["title"] == f"Example vuln {3}"
        assert response_data[0]["cve_id"] == f"CVE-0000-000{3}"
        assert response_data[0]["detail"] == f"This is example vuln {3}."
        assert response_data[0]["exploitation"] == "active"
        assert response_data[0]["automatable"] == "yes"
        assert response_data[0]["cvss_v3_score"] == 7.5
        assert response_data[0]["vulnerable_packages"][0]["name"] == f"example-lib-{3}"
        assert response_data[0]["vulnerable_packages"][0]["ecosystem"] == "pypi"
        assert response_data[0]["vulnerable_packages"][0]["affected_versions"] == ["<2.0.0"]
        assert response_data[0]["vulnerable_packages"][0]["fixed_versions"] == ["2.0.0"]
        assert (
            created_times[3] - timedelta(seconds=10)
            <= datetime.fromisoformat(response_data[0]["created_at"])
            <= created_times[3] + timedelta(seconds=10)
        )
        assert (
            updated_times[3] - timedelta(seconds=10)
            <= datetime.fromisoformat(response_data[0]["updated_at"])
            <= updated_times[3] + timedelta(seconds=10)
        )


class TestDeleteVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # Given
        self.user1 = create_user(USER1)
        self.new_vuln_id = uuid4()
        self.request1 = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.5,
            "vulnerable_packages": [
                {
                    "name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

        # Create a vuln to delete
        client.put(f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=self.request1)

    def test_it_should_delete_vuln_when_vuln_id_exists(self):
        # When
        response = client.delete(f"/vulns/{self.new_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 204  # No Content
        get_response = client.get(f"/vulns/{self.new_vuln_id}", headers=headers(USER1))
        assert get_response.status_code == 404  # Not Found
        assert get_response.json()["detail"] == "No such vuln"

    def test_it_should_return_404_when_vuln_id_does_not_exist(self):
        # Given
        non_existent_vuln_id = uuid4()

        # When
        response = client.delete(f"/vulns/{non_existent_vuln_id}", headers=headers(USER1))

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such vuln"


class TestGetVulnActions:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        # Given
        self.user1 = create_user(USER1)
        self.headers_user = headers(USER1)
        self.vuln_id = uuid4()
        self.vuln_request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.5,
            "vulnerable_packages": [
                {
                    "name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # Create a vulnerability
        response = client.put(
            f"/vulns/{self.vuln_id}", headers=self.headers_user, json=self.vuln_request
        )
        assert response.status_code == 200

    def test_it_should_return_200_and_vuln_actions_list(self, testdb: Session):
        # Given
        action_request = {
            "vuln_id": str(self.vuln_id),
            "action": "Mitigate vulnerability",
            "action_type": "mitigation",
            "recommended": True,
        }
        # Add an action to the vulnerability
        response = client.post("/actions", headers=self.headers_user, json=action_request)
        action_id = response.json()["action_id"]

        # When
        response = client.get(f"/vulns/{self.vuln_id}/actions", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        actions = response.json()
        assert len(actions) == 1
        assert actions[0]["vuln_id"] == str(self.vuln_id)
        assert actions[0]["action_id"] == action_id
        assert actions[0]["action"] == action_request["action"]
        assert actions[0]["action_type"] == action_request["action_type"]
        assert actions[0]["recommended"] == action_request["recommended"]

        now = datetime.now()
        created_at = datetime.fromisoformat(actions[0]["created_at"])
        assert created_at > now - timedelta(seconds=30)
        assert created_at < now

    def test_it_should_return_empty_list_when_no_vuln_actions_exist(self):
        # When
        response = client.get(f"/vulns/{self.vuln_id}/actions", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        assert response.json() == []  # No actions yet

    def test_it_should_return_404_when_vuln_id_does_not_exist(self):
        # Given
        non_existent_vuln_id = uuid4()

        # When
        response = client.get(f"/vulns/{non_existent_vuln_id}/actions", headers=self.headers_user)

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such vuln"
