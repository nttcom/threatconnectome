from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.tests.medium.constants import (
    USER1,
)
from app.tests.medium.utils import (
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

        client.put(f"/vulns/{self.new_vuln_id}", headers=headers(USER1), json=self.request1)

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
        number_of_vulns = 3
        for i in range(number_of_vulns):
            self.vuln_id = uuid4()
            self.vuln_request = {
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
            response = client.put(
                f"/vulns/{self.vuln_id}", headers=self.headers_user, json=self.vuln_request
            )
            vuln_ids.append(self.vuln_id)
        print(vuln_ids)
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

    def test_it_should_return_empty_list_when_no_vulns_exist(self):
        # When
        response = client.get("/vulns?offset=0&limit=100", headers=self.headers_user)

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []  # Ensure no vulns are returned
