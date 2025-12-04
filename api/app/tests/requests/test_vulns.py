import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import PTEAM1, USER1, USER2
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    headers_with_api_key,
)

client = TestClient(app)


class TestUpdateVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        self.user1 = create_user(USER1)
        package = models.Package(
            name="example-lib",
            ecosystem="pypi",
        )
        testdb.add(package)
        testdb.flush()
        self.request1 = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                },
                {
                    "affected_name": "@nextui-org/button",
                    "ecosystem": "npm",
                    "affected_versions": ["<2.0.26"],
                    "fixed_versions": ["2.0.26"],
                },
            ],
        }
        testdb.commit()

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
            affected_versions=["<2.0.0"],
            fixed_versions=["2.0.0"],
            affected_name=self.package1.name,
            ecosystem=self.package1.ecosystem,
        )

        testdb.add(self.affect1)

        testdb.commit()

    def test_return_VulnResponse_when_create_vuln_successfully(self):
        # Given
        new_vuln_id = uuid4()
        current_time = datetime.now(timezone.utc)

        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers_with_api_key(USER1), json=self.request1
        )

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
        pkg_resp = response.json()["vulnerable_packages"][0]
        req_pkg = self.request1["vulnerable_packages"][0]
        assert pkg_resp["affected_name"] == req_pkg["affected_name"]
        assert pkg_resp["ecosystem"] == req_pkg["ecosystem"]
        assert pkg_resp["affected_versions"] == req_pkg["affected_versions"]
        assert pkg_resp["fixed_versions"] == req_pkg["fixed_versions"]

        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"].replace("Z", "+00:00"))
            <= current_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"].replace("Z", "+00:00"))
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
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers_with_api_key(USER1), json=request2
        )
        # Then
        assert response.status_code == 200
        assert response.json()["exploitation"] == models.ExploitationEnum.NONE
        assert response.json()["automatable"] == models.AutomatableEnum.NO

    def test_return_VulnResponse_when_update_vuln_successfully(self, update_setup):
        # Given
        created_time = self.vuln1.created_at.replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers_with_api_key(USER1), json=self.request1
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
        pkg_resp = response.json()["vulnerable_packages"][0]
        req_pkg = self.request1["vulnerable_packages"][0]
        assert pkg_resp["affected_name"] == req_pkg["affected_name"]
        assert pkg_resp["ecosystem"] == req_pkg["ecosystem"]
        assert pkg_resp["affected_versions"] == req_pkg["affected_versions"]
        assert pkg_resp["fixed_versions"] == req_pkg["fixed_versions"]

        assert (
            created_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"].replace("Z", "+00:00"))
            <= created_time + timedelta(seconds=10)
        )
        assert (
            current_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"].replace("Z", "+00:00"))
            <= current_time + timedelta(seconds=10)
        )

    def test_raise_400_if_given_vuln_id_is_default_vuln_id(self):
        # Given
        default_vuln_id = UUID(int=0)

        # When
        response = client.put(
            f"/vulns/{default_vuln_id}", headers=headers_with_api_key(USER1), json=self.request1
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot create default vuln"

    def test_raise_400_if_requested_title_is_not_specified(self):
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
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers_with_api_key(USER1), json=title_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_requested_detail_is_not_specified(self):
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
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers_with_api_key(USER1), json=detail_none_request
        )

        # Then
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Both 'title' and 'detail' are required when creating a vuln."
        )

    def test_raise_400_if_duplicates_vulnerable_packages(self):
        # Given
        new_vuln_id = uuid4()
        out_of_range_cvss_request = {
            "title": "Example vuln",
            "detail": "This vuln is example.",
            "vulnerable_packages": [
                {
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                },
                {
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<3.0.0"],
                    "fixed_versions": ["3.0.0"],
                },
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}",
            headers=headers_with_api_key(USER1),
            json=out_of_range_cvss_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "Duplicate package example-lib in ecosystem pypi"

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
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        # When
        response = client.put(
            f"/vulns/{new_vuln_id}",
            headers=headers_with_api_key(USER1),
            json=out_of_range_cvss_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"

    def test_raise_403_if_current_user_is_not_vuln_creator(self, update_setup):
        # Given
        create_user(USER2)

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}", headers=headers_with_api_key(USER2), json=self.request1
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
    def test_raise_400_when_create_if_field_with_none(self, field_name) -> None:
        # Given
        new_vuln_id = uuid4()
        request = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        request[f"{field_name}"] = None

        # When
        response = client.put(
            f"/vulns/{new_vuln_id}", headers=headers_with_api_key(USER1), json=request
        )

        assert response.status_code == 400
        assert response.json()["detail"] == f"Cannot specify None for {field_name}"

    @pytest.mark.parametrize(
        "field_name",
        [
            "title",
            "detail",
            "exploitation",
            "automatable",
        ],
    )
    def test_raise_400_when_update_if_field_with_none(self, update_setup, field_name):
        # Given
        invalid_request = {
            f"{field_name}": None,
        }

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}",
            headers=headers_with_api_key(USER1),
            json=invalid_request,
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
            f"/vulns/{self.vuln1.vuln_id}",
            headers=headers_with_api_key(USER1),
            json=invalid_request,
        )

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "cvss_v3_score is out of range"

    def test_raise_401_if_invalid_api_key(self, testdb: Session, update_setup):
        # Given
        invalid_headers = headers(USER1)
        invalid_headers["X-API-Key"] = "invalid"

        # When
        response = client.put(
            f"/vulns/{self.vuln1.vuln_id}",
            headers=invalid_headers,
            json=self.request1,
        )

        # Then
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API Key"


class TestGetVuln:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb: Session):
        # Given
        self.user1 = create_user(USER1)
        self.new_vuln_id = uuid4()
        package = models.Package(
            name="example-lib",
            ecosystem="pypi",
        )
        testdb.add(package)
        testdb.flush()
        self.request1 = {
            "title": "Example vuln",
            "cve_id": "CVE-0000-0001",
            "detail": "This vuln is example.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.8,
            "vulnerable_packages": [
                {
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

        response = client.put(
            f"/vulns/{self.new_vuln_id}", headers=headers_with_api_key(USER1), json=self.request1
        )
        self.created_time = datetime.fromisoformat(
            response.json()["created_at"].replace("Z", "+00:00")
        )
        self.updated_time = datetime.fromisoformat(
            response.json()["updated_at"].replace("Z", "+00:00")
        )

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
        pkg_resp = response.json()["vulnerable_packages"][0]
        req_pkg = self.request1["vulnerable_packages"][0]
        assert pkg_resp["affected_name"] == req_pkg["affected_name"]
        assert pkg_resp["ecosystem"] == req_pkg["ecosystem"]
        assert pkg_resp["affected_versions"] == req_pkg["affected_versions"]
        assert pkg_resp["fixed_versions"] == req_pkg["fixed_versions"]

        assert (
            self.created_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["created_at"].replace("Z", "+00:00"))
            <= self.created_time + timedelta(seconds=10)
        )
        assert (
            self.updated_time - timedelta(seconds=10)
            <= datetime.fromisoformat(response.json()["updated_at"].replace("Z", "+00:00"))
            <= self.updated_time + timedelta(seconds=10)
        )

    def test_it_should_return_404_when_vuln_id_is_not_registered(self):
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
        self.user2 = create_user(USER2)
        self.headers_user = headers(USER1)
        self.headers_with_api_key = headers_with_api_key(USER1)

    def create_vuln_request(self, index: int, cvss_v3_score: float = 7.5) -> dict:
        return {
            "title": f"Example-vuln-{index}",
            "cve_id": f"CVE-0000-000{index}",
            "detail": f"This is example vuln {index}.",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": cvss_v3_score,
            "vulnerable_packages": [
                {
                    "affected_name": f"example-lib-{index}",
                    "ecosystem": f"ecosystem-{index}",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

    def assert_vuln_response(
        self, actual_vuln, expected_vuln_id, expected_request, testdb: Session
    ):
        assert actual_vuln["vuln_id"] == str(expected_vuln_id)
        assert actual_vuln["title"] == expected_request["title"]
        assert actual_vuln["cve_id"] == expected_request["cve_id"]
        assert actual_vuln["detail"] == expected_request["detail"]
        assert actual_vuln["exploitation"] == expected_request["exploitation"]
        assert actual_vuln["automatable"] == expected_request["automatable"]
        assert actual_vuln["cvss_v3_score"] == expected_request["cvss_v3_score"]
        pkg_resp = actual_vuln["vulnerable_packages"][0]
        req_pkg = expected_request["vulnerable_packages"][0]
        assert pkg_resp["affected_name"] == req_pkg["affected_name"]
        assert pkg_resp["ecosystem"] == req_pkg["ecosystem"]
        assert pkg_resp["affected_versions"] == req_pkg["affected_versions"]
        assert pkg_resp["fixed_versions"] == req_pkg["fixed_versions"]

    def test_it_should_return_200_and_vulns_list(self, testdb: Session):
        # Given
        vuln_ids = []
        number_of_vulns = 10
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            created_times.append(
                datetime.fromisoformat(response.json()["created_at"].replace("Z", "+00:00"))
            )
            updated_times.append(
                datetime.fromisoformat(response.json()["updated_at"].replace("Z", "+00:00"))
            )

        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == number_of_vulns
        assert len(response_data["vulns"]) == number_of_vulns

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            reversed_index = len(response_data["vulns"]) - 1 - i
            self.assert_vuln_response(
                vuln,
                vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index),
                testdb,
            )
            assert (
                created_times[i] - timedelta(seconds=10)
                <= datetime.fromisoformat(vuln["created_at"].replace("Z", "+00:00"))
                <= created_times[i] + timedelta(seconds=10)
            )
            assert (
                updated_times[i] - timedelta(seconds=10)
                <= datetime.fromisoformat(vuln["updated_at"].replace("Z", "+00:00"))
                <= updated_times[i] + timedelta(seconds=10)
            )

    def test_it_should_return_empty_list_when_no_vulns_exist(self):
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == 0
        assert response_data["vulns"] == []

    def test_it_should_return_correct_number_of_vulns_with_limit(self, testdb: Session):
        # Given
        number_of_vulns = 5
        for i in range(number_of_vulns):
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{uuid4()}", headers=self.headers_with_api_key, json=vuln_request)

        # When
        response = client.get("/vulns?offset=0&limit=2", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == number_of_vulns
        assert len(response_data["vulns"]) == 2

    def test_it_should_return_correct_vulns_with_offset(self, testdb: Session):
        # Given
        number_of_vulns = 5
        vuln_ids = []
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            created_times.append(
                datetime.fromisoformat(response.json()["created_at"].replace("Z", "+00:00"))
            )
            updated_times.append(
                datetime.fromisoformat(response.json()["updated_at"].replace("Z", "+00:00"))
            )

        # When
        response = client.get("/vulns?offset=1&limit=4", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == number_of_vulns
        assert len(response_data["vulns"]) == 4

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            reversed_index = len(response_data["vulns"]) - 1 - i
            self.assert_vuln_response(
                vuln,
                vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index),
                testdb,
            )
        assert (
            created_times[3] - timedelta(seconds=10)
            <= datetime.fromisoformat(
                response_data["vulns"][0]["created_at"].replace("Z", "+00:00")
            )
            <= created_times[3] + timedelta(seconds=10)
        )

    def test_it_should_filter_by_min_cvss_v3_score(self, testdb: Session):
        # Given
        scores = [3.0, 8.0]
        min_cvss_v3_score = 5.0
        count = sum(1 for score in scores if score >= min_cvss_v3_score)
        vuln_ids = []

        for i in range(len(scores)):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i, scores[i])
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            f"/vulns?min_cvss_v3_score={min_cvss_v3_score}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == count
        assert len(response_data["vulns"]) == count
        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i + 1],
                self.create_vuln_request(i + 1, scores[i + 1]),
                testdb,
            )

    def test_it_should_filter_by_max_cvss_v3_score(self, testdb: Session):
        # Given
        scores = [3.0, 8.0]
        max_cvss_v3_score = 5.0
        count = sum(1 for score in scores if score >= max_cvss_v3_score)
        vuln_ids = []

        for i in range(len(scores)):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i, scores[i])
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            f"/vulns?max_cvss_v3_score={max_cvss_v3_score}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == count
        assert len(response_data["vulns"]) == count

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i, scores[i]),
                testdb,
            )

    def test_it_should_filter_by_vuln_ids(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(f"/vulns?vuln_ids={vuln_ids[0]}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["num_vulns"] == 1
        assert len(response_data["vulns"]) == 1

        # Check the details of the filtered vuln
        self.assert_vuln_response(
            response_data["vulns"][0],
            vuln_ids[0],
            self.create_vuln_request(0),
            testdb,
        )

    def test_it_should_filter_by_title_words(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?title_words={put_response_data[0]['title']}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        self.assert_vuln_response(
            response_data["vulns"][0],
            vuln_ids[0],
            self.create_vuln_request(0),
            testdb,
        )

    def test_it_should_return_vulns_when_title_words_include_empty(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            if i == 0:
                vuln_request: dict[str, Any] = {
                    "title": "",
                    "cve_id": f"CVE-0000-000{i}",
                    "detail": f"This is example vuln {i}.",
                    "exploitation": "active",
                    "automatable": "yes",
                    "cvss_v3_score": 7.5,
                    "vulnerable_packages": [
                        {
                            "affected_name": f"example-lib-{i}",
                            "ecosystem": f"ecosystem-{i}",
                            "affected_versions": ["<2.0.0"],
                            "fixed_versions": ["2.0.0"],
                        }
                    ],
                }
            else:
                vuln_request = {
                    "title": f"Example-vuln-{i}",
                    "cve_id": f"CVE-0000-000{i}",
                    "detail": f"This is example vuln {i}.",
                    "exploitation": "active",
                    "automatable": "yes",
                    "cvss_v3_score": 7.5,
                    "vulnerable_packages": [
                        {
                            "affected_name": f"example-lib-{i}",
                            "ecosystem": f"ecosystem-{i}",
                            "affected_versions": ["<2.0.0"],
                            "fixed_versions": ["2.0.0"],
                        }
                    ],
                }
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            "/vulns?title_words=&title_words=Example-vuln-1&title_words=Example-vuln-2",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == number_of_vulns
        assert response_data["num_vulns"] == number_of_vulns

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            if i == 2:
                assert vuln["title"] == ""
                assert vuln["cve_id"] == "CVE-0000-0000"
                assert vuln["detail"] == "This is example vuln 0."
                assert vuln["exploitation"] == "active"
                assert vuln["automatable"] == "yes"
                assert vuln["cvss_v3_score"] == 7.5
                assert vuln["vulnerable_packages"][0]["affected_name"] == "example-lib-0"
                assert vuln["vulnerable_packages"][0]["ecosystem"] == "ecosystem-0"
                assert vuln["vulnerable_packages"][0]["affected_versions"] == ["<2.0.0"]
                assert vuln["vulnerable_packages"][0]["fixed_versions"] == ["2.0.0"]
            else:
                reversed_index = len(response_data["vulns"]) - 1 - i
                self.assert_vuln_response(
                    vuln,
                    vuln_ids[reversed_index],
                    self.create_vuln_request(reversed_index),
                    testdb,
                )

    def test_it_should_filter_by_detail_words(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?detail_words={put_response_data[0]['detail']}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        self.assert_vuln_response(
            response_data["vulns"][0],
            vuln_ids[0],
            self.create_vuln_request(0),
            testdb,
        )

    def test_it_should_return_all_vulns_when_detail_words_include_empty(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            if i == 0:
                vuln_request: dict[str, Any] = {
                    "title": f"Example-vuln-{i}",
                    "cve_id": f"CVE-0000-000{i}",
                    "detail": "",
                    "exploitation": "active",
                    "automatable": "yes",
                    "cvss_v3_score": 7.5,
                    "vulnerable_packages": [
                        {
                            "affected_name": f"example-lib-{i}",
                            "ecosystem": f"ecosystem-{i}",
                            "affected_versions": ["<2.0.0"],
                            "fixed_versions": ["2.0.0"],
                        }
                    ],
                }
            else:
                vuln_request = {
                    "title": f"Example-vuln-{i}",
                    "cve_id": f"CVE-0000-000{i}",
                    "detail": f"This is example vuln {i}.",
                    "exploitation": "active",
                    "automatable": "yes",
                    "cvss_v3_score": 7.5,
                    "vulnerable_packages": [
                        {
                            "affected_name": f"example-lib-{i}",
                            "ecosystem": f"ecosystem-{i}",
                            "affected_versions": ["<2.0.0"],
                            "fixed_versions": ["2.0.0"],
                        }
                    ],
                }
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            "/vulns?detail_words=&detail_words=This is example vuln 1"
            "&detail_words=This is example vuln 2",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == number_of_vulns
        assert response_data["num_vulns"] == number_of_vulns

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            if i == 2:
                assert vuln["title"] == "Example-vuln-0"
                assert vuln["cve_id"] == "CVE-0000-0000"
                assert vuln["detail"] == ""
                assert vuln["exploitation"] == "active"
                assert vuln["automatable"] == "yes"
                assert vuln["cvss_v3_score"] == 7.5
                assert vuln["vulnerable_packages"][0]["affected_name"] == "example-lib-0"
                assert vuln["vulnerable_packages"][0]["ecosystem"] == "ecosystem-0"
                assert vuln["vulnerable_packages"][0]["affected_versions"] == ["<2.0.0"]
                assert vuln["vulnerable_packages"][0]["fixed_versions"] == ["2.0.0"]
            else:
                reversed_index = len(response_data["vulns"]) - 1 - i
                self.assert_vuln_response(
                    vuln,
                    vuln_ids[reversed_index],
                    self.create_vuln_request(reversed_index),
                    testdb,
                )

    def test_it_should_filter_by_pteam_id(self, testdb: Session):
        # Given
        pteam1 = create_pteam(USER1, PTEAM1)
        service_name = "test-service"
        upload_file_name = "test_trivy_cyclonedx_axios.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = sbom.read()
        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name, upload_file_name)

        # Get the package name and ecosystem included in the SBOM
        component = json.loads(sbom_json)["components"][1]
        package_name = component["name"]

        ecosystem = None
        for prop in component.get("properties", []):
            if prop.get("name") == "aquasecurity:trivy:PkgType":
                ecosystem = prop.get("value")
                break

        # Create two vulnerabilities (one for the SBOM package, and one for an unrelated package)
        vuln_ids = []
        vuln_request_sbom: dict[str, Any] = {
            "title": "SBOM-related vulnerability",
            "cve_id": "CVE-2025-0001",
            "detail": "A vulnerability associated with a package created from the SBOM",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 7.5,
            "vulnerable_packages": [
                {
                    "affected_name": package_name,
                    "ecosystem": ecosystem,
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }
        vuln_id_sbom = uuid4()
        client.put(
            f"/vulns/{vuln_id_sbom}", headers=self.headers_with_api_key, json=vuln_request_sbom
        )
        vuln_ids.append(vuln_id_sbom)

        vuln_request_other: dict[str, Any] = {
            "title": "Unrelated vulnerability",
            "cve_id": "CVE-2025-0002",
            "detail": "A vulnerability associated with a package unrelated to the SBOM",
            "exploitation": "active",
            "automatable": "yes",
            "cvss_v3_score": 5.0,
            "vulnerable_packages": [
                {
                    "affected_name": "other-lib",
                    "ecosystem": "other-eco",
                    "affected_versions": ["<1.0.0"],
                    "fixed_versions": ["1.0.0"],
                }
            ],
        }
        vuln_id_other = uuid4()
        client.put(
            f"/vulns/{vuln_id_other}", headers=self.headers_with_api_key, json=vuln_request_other
        )
        vuln_ids.append(vuln_id_other)

        # When: filter pteam_id
        response = client.get(f"/vulns?pteam_id={pteam1.pteam_id}", headers=self.headers_user)

        # Then:
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1
        self.assert_vuln_response(
            response_data["vulns"][0],
            vuln_id_sbom,
            vuln_request_sbom,
            testdb,
        )

    def test_it_should_filter_by_cve_ids(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?cve_ids={put_response_data[0]['cve_id']}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

    def test_it_should_return_400_when_cve_ids_is_empty(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get("/vulns?cve_ids=", headers=self.headers_user)

        # Then
        assert response.status_code == 400

    def test_it_should_filter_by_created_and_updated_timestamps(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []

        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)

        created_at_list = ["2023-01-01 00:00:00", "2023-02-01 00:00:00", "2023-03-01 00:00:00"]
        updated_at_list = ["2023-01-01 00:00:00", "2023-02-01 00:00:00", "2023-03-01 00:00:00"]
        for i in range(number_of_vulns):
            testdb.execute(
                text(
                    """
                UPDATE vuln
                SET created_at = :created_at, updated_at = :updated_at
                WHERE vuln_id = :vuln_id
                """
                ),
                {
                    "vuln_id": str(vuln_ids[i]),
                    "created_at": created_at_list[i],
                    "updated_at": updated_at_list[i],
                },
            )

        created_after = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?created_after={created_after}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 2
        assert response_data["num_vulns"] == 2
        # Filter vuln_ids based on the created_after condition
        filtered_vuln_ids = [
            vuln_ids[i] for i in range(number_of_vulns) if created_at_list[i] > created_after
        ]

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            reversed_index = len(response_data["vulns"]) - 1 - i
            self.assert_vuln_response(
                vuln,
                filtered_vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index + 1),
                testdb,
            )

        created_before = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?created_before={created_before}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

        updated_after = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?updated_after={updated_after}", headers=self.headers_user)
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 2
        assert response_data["num_vulns"] == 2

        # Filter vuln_ids based on the created_after condition
        filtered_vuln_ids = [
            vuln_ids[i] for i in range(number_of_vulns) if created_at_list[i] > created_after
        ]

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            reversed_index = len(response_data["vulns"]) - 1 - i
            self.assert_vuln_response(
                vuln,
                filtered_vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index + 1),
                testdb,
            )

        updated_before = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?updated_before={updated_before}", headers=self.headers_user)
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

    def test_it_should_filter_by_creator_ids(self, testdb: Session):
        # Given
        vuln_ids = []
        put_response_data = []
        for i in range(2):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            if i == 0:
                put_response = client.put(
                    f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
                )
            else:
                put_response = client.put(
                    f"/vulns/{vuln_id}",
                    headers=headers(USER2),
                    json=vuln_request,
                )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?creator_ids={put_response_data[0]['created_by']}",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

    def test_it_should_return_no_vulns_when_creator_ids_is_empty(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get("/vulns?creator_ids=", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 0
        assert response_data["num_vulns"] == 0

    def test_it_should_filter_by_package_name(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?package_name={put_response_data[0]['vulnerable_packages'][0]['affected_name']}",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

    def test_it_should_filter_by_ecosystem(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?ecosystem={put_response_data[0]['vulnerable_packages'][0]['ecosystem']}",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 1
        assert response_data["num_vulns"] == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data["vulns"]):
            self.assert_vuln_response(
                vuln,
                vuln_ids[i],
                self.create_vuln_request(i),
                testdb,
            )

    # Test sort_key
    def setup_vulns(self, testdb: Session, vulns_data):
        testdb.execute(text("DELETE FROM vuln"))
        testdb.commit()

        for i, data in enumerate(vulns_data):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i, data["cvss_v3_score"])
            if "cve_id" in data:
                vuln_request["cve_id"] = data["cve_id"]
            client.put(f"/vulns/{vuln_id}", headers=self.headers_with_api_key, json=vuln_request)

            update_params = {"vuln_id": str(vuln_id)}
            update_fields = []

            if "updated_at" in data:
                update_fields.append("updated_at = :updated_at")
                update_params["updated_at"] = data["updated_at"]

            if "created_at" in data:
                update_fields.append("created_at = :created_at")
                update_params["created_at"] = data["created_at"]

            if update_fields:
                testdb.execute(
                    text(
                        f"""
                        UPDATE vuln
                        SET {", ".join(update_fields)}
                        WHERE vuln_id = :vuln_id
                        """
                    ),
                    update_params,
                )

    # A: sortkey is CVSS_V3_SCORE
    # A1
    def test_it_should_sort_by_cvss_v3_score_ascending(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-02T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [3.0, 5.0, 8.0]

    # A2
    def test_it_should_sort_by_cvss_v3_score_with_null(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 3.0, "updated_at": "2025-01-02T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": None, "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [3.0, 8.0, None]

    # A3
    def test_it_should_sort_by_descending_updated_at_when_cvss_v3_scores_are_equal(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2024-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["updated_at"] for vuln in response_data["vulns"]] == [
            "2024-01-01T00:00:00Z",
            "2023-01-01T00:00:00Z",
        ]

    # A4
    def test_it_should_sort_by_ascending_cvss_v3_score_and_by_descending_updated_at_with_null(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": None, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-02T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [5.0, 5.0, 8.0, None]
        assert [
            vuln["updated_at"] for vuln in response_data["vulns"] if vuln["cvss_v3_score"] == 5.0
        ] == [
            "2025-01-02T00:00:00Z",
            "2023-01-01T00:00:00Z",
        ]

    # B: sortkey is CVSS_V3_SCORE_DESC
    # B1
    def test_it_should_sort_by_cvss_v3_score_descending(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-02T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [8.0, 5.0, 3.0]

    # B2
    def test_it_should_sort_by_cvss_v3_score_descending_with_null(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-02T00:00:00Z"},
            {"cvss_v3_score": None, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [8.0, 5.0, None]

    # B3
    def test_sort_by_cvss_v3_score_descending_updated_at_when_cvss_v3_scores_are_equal(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2022-01-01T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2023-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["updated_at"] for vuln in response_data["vulns"]] == [
            "2023-01-01T00:00:00Z",
            "2022-01-01T00:00:00Z",
        ]

    # B4
    def test_it_should_sort_by_descending_cvss_v3_score_and_by_descending_updated_at_with_null(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-03T00:00:00Z"},
            {"cvss_v3_score": None, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-02T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-cvss_v3_score", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [8.0, 5.0, 5.0, None]
        assert [
            vuln["updated_at"] for vuln in response_data["vulns"] if vuln["cvss_v3_score"] == 5.0
        ] == [
            "2025-01-02T00:00:00Z",
            "2023-01-01T00:00:00Z",
        ]

    # C: sortkey isUPDATED_AT
    # C1
    def test_it_should_sort_by_updated_at_ascending(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2024-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2023-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["updated_at"] for vuln in response_data["vulns"]] == [
            "2023-01-01T00:00:00Z",
            "2024-01-01T00:00:00Z",
            "2025-01-01T00:00:00Z",
        ]

    # C2
    def test_it_should_sort_by_cvss_v3_score_descending_when_updated_at_are_equal(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2024-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2024-01-01T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2024-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [8.0, 5.0, 3.0]

    # C3
    def test_it_should_sort_by_ascending_updated_at_and_by_descending_cvss_v3_score(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2022-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2023-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [3.0, 8.0, 5.0]

    # D: sortkey is UPDATED_AT_DESC
    # D1
    def test_it_should_sort_by_updated_at_descending(self, testdb: Session):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2022-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2021-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["updated_at"] for vuln in response_data["vulns"]] == [
            "2023-01-01T00:00:00Z",
            "2022-01-01T00:00:00Z",
            "2021-01-01T00:00:00Z",
        ]

    # D2
    def test_sort_by_cvss_v3_score_desc_when_updated_at_are_equal_and_sort_key_is_updated_at_desc(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2025-01-01T00:00:00Z"},
            {"cvss_v3_score": 8.0, "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [8.0, 5.0, 3.0]

    # D3
    def test_it_should_sort_by_descending_updated_at_and_by_descending_cvss_v3_score(
        self, testdb: Session
    ):
        vulns_data = [
            {"cvss_v3_score": 8.0, "updated_at": "2024-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2024-01-01T00:00:00Z"},
            {"cvss_v3_score": 5.0, "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)
        response = client.get("/vulns?sort_keys=-updated_at", headers=self.headers_user)
        assert response.status_code == 200
        response_data = response.json()
        assert [vuln["cvss_v3_score"] for vuln in response_data["vulns"]] == [5.0, 8.0, 3.0]

    @pytest.mark.parametrize(
        "sort_keys,vulns_data,expected_cvss_scores,expected_updated_at,expected_created_at,expected_cve_ids",
        [
            # Test case 1: cvss_v3_score ascending, updated_at descending
            (
                ["cvss_v3_score", "-updated_at"],
                [
                    {  # 3
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2023-01-01T00:00:00Z",
                        "cve_id": "CVE-2023-0001",
                    },
                    {  # 2
                        "cvss_v3_score": 5.0,
                        "updated_at": "2025-01-01T00:00:00Z",
                        "created_at": "2023-01-02T00:00:00Z",
                        "cve_id": "CVE-2023-0002",
                    },
                    {  # 1
                        "cvss_v3_score": 3.0,
                        "updated_at": "2024-01-01T00:00:00Z",
                        "created_at": "2023-01-03T00:00:00Z",
                        "cve_id": "CVE-2023-0003",
                    },
                    {  # 4
                        "cvss_v3_score": 8.0,
                        "updated_at": "2022-01-01T00:00:00Z",
                        "created_at": "2023-01-04T00:00:00Z",
                        "cve_id": "CVE-2023-0004",
                    },
                ],
                [3.0, 5.0, 5.0, 8.0],
                [
                    "2024-01-01T00:00:00Z",
                    "2025-01-01T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                    "2022-01-01T00:00:00Z",
                ],
                [
                    "2023-01-03T00:00:00Z",
                    "2023-01-02T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                    "2023-01-04T00:00:00Z",
                ],
                ["CVE-2023-0003", "CVE-2023-0002", "CVE-2023-0001", "CVE-2023-0004"],
            ),
            # Test case 2: created_at ascending, cvss_v3_score descending
            (
                ["created_at", "-cvss_v3_score"],
                [
                    {  # 2
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2022-01-02T00:00:00Z",
                        "cve_id": "CVE-2022-0001",
                    },
                    {  # 1
                        "cvss_v3_score": 8.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2022-01-01T00:00:00Z",
                        "cve_id": "CVE-2022-0002",
                    },
                    {  # 3
                        "cvss_v3_score": 3.0,
                        "updated_at": "2023-01-03T00:00:00Z",
                        "created_at": "2022-01-02T00:00:00Z",
                        "cve_id": "CVE-2022-0003",
                    },
                    {  # 4
                        "cvss_v3_score": 7.0,
                        "updated_at": "2023-01-04T00:00:00Z",
                        "created_at": "2022-01-03T00:00:00Z",
                        "cve_id": "CVE-2022-0004",
                    },
                ],
                [8.0, 5.0, 3.0, 7.0],
                [
                    "2023-01-02T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                    "2023-01-03T00:00:00Z",
                    "2023-01-04T00:00:00Z",
                ],
                [
                    "2022-01-01T00:00:00Z",
                    "2022-01-02T00:00:00Z",
                    "2022-01-02T00:00:00Z",
                    "2022-01-03T00:00:00Z",
                ],
                ["CVE-2022-0002", "CVE-2022-0001", "CVE-2022-0003", "CVE-2022-0004"],
            ),
            # Test case 3: cve_id ascending, created_at descending
            (
                ["cve_id", "-created_at"],
                [
                    {  # 3
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2021-01-01T00:00:00Z",
                        "cve_id": "CVE-2021-0002",
                    },
                    {  # 2
                        "cvss_v3_score": 8.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2021-01-02T00:00:00Z",
                        "cve_id": "CVE-2021-0001",
                    },
                    {  # 4
                        "cvss_v3_score": 3.0,
                        "updated_at": "2023-01-03T00:00:00Z",
                        "created_at": "2021-01-03T00:00:00Z",
                        "cve_id": "CVE-2021-0003",
                    },
                    {  # 1
                        "cvss_v3_score": 7.0,
                        "updated_at": "2023-01-04T00:00:00Z",
                        "created_at": "2021-01-04T00:00:00Z",
                        "cve_id": "CVE-2021-0001",
                    },
                ],
                [7.0, 8.0, 5.0, 3.0],
                [
                    "2023-01-04T00:00:00Z",
                    "2023-01-02T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                    "2023-01-03T00:00:00Z",
                ],
                [
                    "2021-01-04T00:00:00Z",
                    "2021-01-02T00:00:00Z",
                    "2021-01-01T00:00:00Z",
                    "2021-01-03T00:00:00Z",
                ],
                ["CVE-2021-0001", "CVE-2021-0001", "CVE-2021-0002", "CVE-2021-0003"],
            ),
            # Test case 4: updated_at descending, cve_id ascending
            (
                ["-updated_at", "cve_id"],
                [
                    {  # 4
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2021-01-01T00:00:00Z",
                        "cve_id": "CVE-2020-0003",
                    },
                    {  # 1
                        "cvss_v3_score": 8.0,
                        "updated_at": "2023-01-03T00:00:00Z",
                        "created_at": "2021-01-02T00:00:00Z",
                        "cve_id": "CVE-2020-0001",
                    },
                    {  # 3
                        "cvss_v3_score": 3.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2021-01-03T00:00:00Z",
                        "cve_id": "CVE-2020-0002",
                    },
                    {  # 2
                        "cvss_v3_score": 7.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2021-01-04T00:00:00Z",
                        "cve_id": "CVE-2020-0001",
                    },
                ],
                [8.0, 7.0, 3.0, 5.0],
                [
                    "2023-01-03T00:00:00Z",
                    "2023-01-02T00:00:00Z",
                    "2023-01-02T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                ],
                [
                    "2021-01-02T00:00:00Z",
                    "2021-01-04T00:00:00Z",
                    "2021-01-03T00:00:00Z",
                    "2021-01-01T00:00:00Z",
                ],
                ["CVE-2020-0001", "CVE-2020-0001", "CVE-2020-0002", "CVE-2020-0003"],
            ),
            # Test case 5: cve_id ascending when cve_id contains None
            (
                ["cve_id"],
                [
                    {  # 3
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2021-01-01T00:00:00Z",
                        "cve_id": "CVE-2020-10000",
                    },
                    {  # 1
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2021-01-02T00:00:00Z",
                        "cve_id": "CVE-2020-0001",
                    },
                    {  # 2
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-03T00:00:00Z",
                        "created_at": "2021-01-03T00:00:00Z",
                        "cve_id": "CVE-2020-2000",
                    },
                    {  # 4
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-04T00:00:00Z",
                        "created_at": "2021-01-04T00:00:00Z",
                        "cve_id": None,
                    },
                ],
                [5.0, 5.0, 5.0, 5.0],
                [
                    "2023-01-02T00:00:00Z",
                    "2023-01-03T00:00:00Z",
                    "2023-01-01T00:00:00Z",
                    "2023-01-04T00:00:00Z",
                ],
                [
                    "2021-01-02T00:00:00Z",
                    "2021-01-03T00:00:00Z",
                    "2021-01-01T00:00:00Z",
                    "2021-01-04T00:00:00Z",
                ],
                ["CVE-2020-0001", "CVE-2020-2000", "CVE-2020-10000", None],
            ),
            # Test case 5: cve_id descending when cve_id contains None
            (
                ["-cve_id"],
                [
                    {  # 1
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-01T00:00:00Z",
                        "created_at": "2021-01-01T00:00:00Z",
                        "cve_id": "CVE-2020-10000",
                    },
                    {  # 3
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-02T00:00:00Z",
                        "created_at": "2021-01-02T00:00:00Z",
                        "cve_id": "CVE-2020-0001",
                    },
                    {  # 2
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-03T00:00:00Z",
                        "created_at": "2021-01-03T00:00:00Z",
                        "cve_id": "CVE-2020-2000",
                    },
                    {  # 4
                        "cvss_v3_score": 5.0,
                        "updated_at": "2023-01-04T00:00:00Z",
                        "created_at": "2021-01-04T00:00:00Z",
                        "cve_id": None,
                    },
                ],
                [5.0, 5.0, 5.0, 5.0],
                [
                    "2023-01-01T00:00:00Z",
                    "2023-01-03T00:00:00Z",
                    "2023-01-02T00:00:00Z",
                    "2023-01-04T00:00:00Z",
                ],
                [
                    "2021-01-01T00:00:00Z",
                    "2021-01-03T00:00:00Z",
                    "2021-01-02T00:00:00Z",
                    "2021-01-04T00:00:00Z",
                ],
                ["CVE-2020-10000", "CVE-2020-2000", "CVE-2020-0001", None],
            ),
        ],
    )
    def test_it_should_sort_by_multiple_sort_keys(
        self,
        testdb: Session,
        sort_keys,
        vulns_data,
        expected_cvss_scores,
        expected_updated_at,
        expected_created_at,
        expected_cve_ids,
    ):
        # Given
        self.setup_vulns(testdb, vulns_data)
        sort_keys_param = "&".join([f"sort_keys={key}" for key in sort_keys])

        # When
        response = client.get(f"/vulns?{sort_keys_param}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        actual_cvss_scores = [vuln["cvss_v3_score"] for vuln in response_data["vulns"]]
        actual_updated_at = [vuln["updated_at"] for vuln in response_data["vulns"]]
        actual_created_at = [vuln["created_at"] for vuln in response_data["vulns"]]
        actual_cve_ids = [vuln["cve_id"] for vuln in response_data["vulns"]]

        assert actual_cvss_scores == expected_cvss_scores
        assert actual_updated_at == expected_updated_at
        assert actual_created_at == expected_created_at
        assert actual_cve_ids == expected_cve_ids

    # Test for invalid sort_key
    def test_it_should_return_400_when_invalid_sort_key_is_specified(self, testdb: Session):
        # Given
        vulns_data = [
            {"cvss_v3_score": 5.0, "updated_at": "2023-01-01T00:00:00Z"},
            {"cvss_v3_score": 3.0, "updated_at": "2023-01-02T00:00:00Z"},
        ]
        self.setup_vulns(testdb, vulns_data)

        # When: Request with invalid sort key
        response = client.get("/vulns?sort_keys=invalid_key", headers=self.headers_user)

        # Then
        assert response.status_code == 400

    def test_num_vulns_and_len_vulns_differ_when_limit_is_less_than_total(self, testdb: Session):
        # Given
        number_of_vulns = 5
        for i in range(number_of_vulns):
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{uuid4()}", headers=self.headers_with_api_key, json=vuln_request)

        # When: Get with limit=2
        response = client.get("/vulns?offset=0&limit=2", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["vulns"]) == 2
        assert response_data["num_vulns"] == number_of_vulns
        assert response_data["num_vulns"] > len(response_data["vulns"])


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
                    "affected_name": "example-lib",
                    "ecosystem": "pypi",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

        # Create a vuln to delete
        client.put(
            f"/vulns/{self.new_vuln_id}", headers=headers_with_api_key(USER1), json=self.request1
        )

    def test_it_should_delete_vuln_when_vuln_id_exists(self):
        # When
        response = client.delete(f"/vulns/{self.new_vuln_id}", headers=headers_with_api_key(USER1))

        # Then
        assert response.status_code == 204  # No Content
        get_response = client.get(f"/vulns/{self.new_vuln_id}", headers=headers(USER1))
        assert get_response.status_code == 404  # Not Found
        assert get_response.json()["detail"] == "No such vuln"

    def test_it_should_return_404_when_vuln_id_does_not_exist(self):
        # Given
        non_existent_vuln_id = uuid4()

        # When
        response = client.delete(
            f"/vulns/{non_existent_vuln_id}", headers=headers_with_api_key(USER1)
        )

        # Then
        assert response.status_code == 404
        assert response.json()["detail"] == "No such vuln"

    def test_raise_401_if_invalid_api_key(self):
        # Given
        invalid_headers = headers(USER1)
        invalid_headers["X-API-Key"] = "invalid"

        # When
        response = client.delete(f"/vulns/{self.new_vuln_id}", headers=invalid_headers)

        # Then
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API Key"
