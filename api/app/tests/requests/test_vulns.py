from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
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
            "content_fingerprint" in response.json()
            and response.json()["content_fingerprint"] is not None
        )
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
            "content_fingerprint" in response.json()
            and response.json()["content_fingerprint"] is not None
        )
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
            "content_fingerprint" in response.json()
            and response.json()["content_fingerprint"] is not None
        )
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
        self.user2 = create_user(USER2)
        self.headers_user = headers(USER1)

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
                    "name": f"example-lib-{index}",
                    "ecosystem": f"ecosystem-{index}",
                    "affected_versions": ["<2.0.0"],
                    "fixed_versions": ["2.0.0"],
                }
            ],
        }

    def assert_vuln_response(self, actual_vuln, expected_vuln_id, expected_request):
        assert actual_vuln["vuln_id"] == str(expected_vuln_id)
        assert actual_vuln["title"] == expected_request["title"]
        assert actual_vuln["cve_id"] == expected_request["cve_id"]
        assert actual_vuln["detail"] == expected_request["detail"]
        assert actual_vuln["exploitation"] == expected_request["exploitation"]
        assert actual_vuln["automatable"] == expected_request["automatable"]
        assert actual_vuln["cvss_v3_score"] == expected_request["cvss_v3_score"]
        assert (
            actual_vuln["vulnerable_packages"][0]["name"]
            == expected_request["vulnerable_packages"][0]["name"]
        )
        assert (
            actual_vuln["vulnerable_packages"][0]["ecosystem"]
            == expected_request["vulnerable_packages"][0]["ecosystem"]
        )
        assert (
            actual_vuln["vulnerable_packages"][0]["affected_versions"]
            == expected_request["vulnerable_packages"][0]["affected_versions"]
        )
        assert (
            actual_vuln["vulnerable_packages"][0]["fixed_versions"]
            == expected_request["vulnerable_packages"][0]["fixed_versions"]
        )

    def test_it_should_return_200_and_vulns_list(self, testdb: Session):
        # Given
        vuln_ids = []
        number_of_vulns = 10
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)
            created_times.append(datetime.fromisoformat(response.json()["created_at"]))
            updated_times.append(datetime.fromisoformat(response.json()["updated_at"]))
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == number_of_vulns

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            reversed_index = len(response_data) - 1 - i
            self.assert_vuln_response(
                vuln, vuln_ids[reversed_index], self.create_vuln_request(reversed_index)
            )

    def test_it_should_return_empty_list_when_no_vulns_exist(self):
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []

    def test_it_should_return_correct_number_of_vulns_with_limit(self, testdb: Session):
        # Given
        number_of_vulns = 5
        for i in range(number_of_vulns):
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{uuid4()}", headers=self.headers_user, json=vuln_request)

        # When
        response = client.get("/vulns?offset=0&limit=2", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2

    def test_it_should_return_correct_vulns_with_offset(self, testdb: Session):
        # Given
        number_of_vulns = 5
        vuln_ids = []
        created_times = []
        updated_times = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)
            created_times.append(datetime.fromisoformat(response.json()["created_at"]))
            updated_times.append(datetime.fromisoformat(response.json()["updated_at"]))

        # When
        response = client.get("/vulns?offset=1&limit=4", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 4

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            reversed_index = len(response_data) - 1 - i
            self.assert_vuln_response(
                vuln, vuln_ids[reversed_index], self.create_vuln_request(reversed_index)
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
            client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            f"/vulns?min_cvss_v3_score={min_cvss_v3_score}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == count
        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(
                vuln, vuln_ids[i + 1], self.create_vuln_request(i + 1, scores[i + 1])
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
            client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(
            f"/vulns?max_cvss_v3_score={max_cvss_v3_score}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == count

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i, scores[i]))

    def test_it_should_filter_by_vuln_ids(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)

        # When
        response = client.get(f"/vulns?vuln_ids={vuln_ids[0]}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        # Check the details of the filtered vuln
        self.assert_vuln_response(response_data[0], vuln_ids[0], self.create_vuln_request(0))

    def test_it_should_filter_by_title_words(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
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
        assert len(response_data) == 1

        self.assert_vuln_response(response_data[0], vuln_ids[0], self.create_vuln_request(0))

    def test_it_should_filter_by_detail_words(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
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
        assert len(response_data) == 1

        self.assert_vuln_response(response_data[0], vuln_ids[0], self.create_vuln_request(0))

    def test_it_should_filter_by_cve_ids(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
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
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_filter_by_created_and_updated_timestamps(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []

        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
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
        assert len(response_data) == 2
        # Filter vuln_ids based on the created_after condition
        filtered_vuln_ids = [
            vuln_ids[i] for i in range(number_of_vulns) if created_at_list[i] > created_after
        ]

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            reversed_index = len(response_data) - 1 - i
            self.assert_vuln_response(
                vuln,
                filtered_vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index + 1),
            )

        created_before = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?created_before={created_before}", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

        updated_after = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?updated_after={updated_after}", headers=self.headers_user)
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2

        # Filter vuln_ids based on the created_after condition
        filtered_vuln_ids = [
            vuln_ids[i] for i in range(number_of_vulns) if created_at_list[i] > created_after
        ]

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            reversed_index = len(response_data) - 1 - i
            self.assert_vuln_response(
                vuln,
                filtered_vuln_ids[reversed_index],
                self.create_vuln_request(reversed_index + 1),
            )

        updated_before = "2023-01-15 00:00:00"
        # When
        response = client.get(f"/vulns?updated_before={updated_before}", headers=self.headers_user)
        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_filter_by_creator_ids(self, testdb: Session):
        # Given
        vuln_ids = []
        put_response_data = []
        for i in range(2):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            if i == 0:
                put_response = client.put(
                    f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
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
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_filter_by_package_name(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
            )
            vuln_ids.append(vuln_id)
            put_response_data.append(put_response.json())

        # When
        response = client.get(
            f"/vulns?package_name={put_response_data[0]['vulnerable_packages'][0]['name']}",
            headers=self.headers_user,
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_filter_by_ecosystem(self, testdb: Session):
        # Given
        number_of_vulns = 2
        vuln_ids = []
        put_response_data = []
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            put_response = client.put(
                f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request
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
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_filter_by_package_manager(self, testdb: Session):
        # Given
        package_manager = "package-manager-0"
        number_of_vulns = 2
        vuln_ids = []

        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i)
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)

            if i == 0:  # Get the package_id of the first record
                response_data = response.json()
                # Get the package_id from the database
                package = testdb.execute(
                    text(
                        """
                        SELECT package_id FROM package
                        WHERE name = 'example-lib-0' AND ecosystem = 'ecosystem-0';
                        """
                    )
                ).fetchone()

                if package:
                    package_id = package._mapping["package_id"]
                else:
                    raise ValueError("package_id could not be determined.")

        if not package_id:
            raise ValueError("package_id could not be determined.")

        pteam_id = uuid4()
        testdb.execute(
            text(
                f"""
                INSERT INTO pteam (pteam_id, pteam_name, contact_info)
                VALUES ('{pteam_id}', 'example-pteam', 'contact@example.com');
                """
            )
        )

        service_id = uuid4()
        testdb.execute(
            text(
                f"""
                INSERT INTO service (service_id, pteam_id, service_name)
                VALUES ('{service_id}', '{pteam_id}', 'example-service');
                """
            )
        )

        # Add a dependency with the specified package_manager
        package_version_id = uuid4()
        dependency_id = uuid4()

        testdb.execute(
            text(
                f"""
            INSERT INTO packageversion (package_version_id, package_id, version)
            VALUES ('{package_version_id}', '{package_id}', '1.0.0');
            """
            )
        )
        testdb.execute(
            text(
                f"""
            INSERT INTO dependency (dependency_id, service_id, package_version_id, target, package_manager)
            VALUES ('{dependency_id}', '{service_id}', '{package_version_id}', 'target', '{package_manager}');
            """
            )
        )

        # When
        response = client.get(
            f"/vulns?package_manager={package_manager}", headers=self.headers_user
        )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

        # Check the details of each vuln
        for i, vuln in enumerate(response_data):
            self.assert_vuln_response(vuln, vuln_ids[i], self.create_vuln_request(i))

    def test_it_should_sort_by_sort_key(self, testdb: Session):
        # Given
        number_of_vulns = 3
        vuln_ids = []
        created_times = []
        updated_times = []
        cvss_scores = [7.5, 8.0, 6.5]
        for i in range(number_of_vulns):
            vuln_id = uuid4()
            vuln_request = self.create_vuln_request(i, cvss_scores[i])
            response = client.put(f"/vulns/{vuln_id}", headers=self.headers_user, json=vuln_request)
            vuln_ids.append(vuln_id)
            created_times.append(datetime.fromisoformat(response.json()["created_at"]))
            updated_times.append(datetime.fromisoformat(response.json()["updated_at"]))

        # When: Sort by updated_at descending
        response = client.get("/vulns?sort_key=updated_at_desc", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == number_of_vulns

        # Check if the vulns are sorted by updated_at in descending order
        response_updated_times = [
            datetime.fromisoformat(vuln["updated_at"]) for vuln in response_data
        ]
        assert response_updated_times == sorted(response_updated_times, reverse=True)

        # When: Sort by updated_at ascending
        response = client.get("/vulns?sort_key=updated_at", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == number_of_vulns

        # Check if the vulns are sorted by updated_at in ascending order
        response_updated_times = [
            datetime.fromisoformat(vuln["updated_at"]) for vuln in response_data
        ]
        assert response_updated_times == sorted(response_updated_times)

        # When: Sort by cvss_v3_score descending
        response = client.get("/vulns?sort_key=cvss_v3_score_desc", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == number_of_vulns

        # Check if the vulns are sorted by cvss_v3_score in descending order
        response_cvss_scores = [vuln["cvss_v3_score"] for vuln in response_data]
        assert response_cvss_scores == sorted(cvss_scores, reverse=True)

        # When: Sort by cvss_v3_score ascending
        response = client.get("/vulns?sort_key=cvss_v3_score", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == number_of_vulns

        # Check if the vulns are sorted by cvss_v3_score in ascending order
        response_cvss_scores = [vuln["cvss_v3_score"] for vuln in response_data]
        assert response_cvss_scores == sorted(cvss_scores)


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
