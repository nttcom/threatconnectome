import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import ERROR, INFO
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.constants import SYSTEM_EMAIL
from app.main import app
from app.notification.alert import (
    create_mail_to_notify_sbom_upload_failed,
    create_mail_to_notify_sbom_upload_succeeded,
)
from app.notification.slack import (
    create_slack_blocks_to_notify_sbom_upload_failed,
    create_slack_blocks_to_notify_sbom_upload_succeeded,
)
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    PTEAM1,
    SAMPLE_SLACK_WEBHOOK_URL,
    USER1,
    VULN1,
    VULN2,
    VULN3,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
    set_ticket_status,
    upload_pteam_packages,
)

client = TestClient(app)


class TestGetVulnIdsTiedToServicePackage:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        # Create 1st ticket
        service_name1 = "test_service1"
        self.ticket_response1 = ticket_utils.create_ticket(
            testdb, USER1, PTEAM1, service_name1, VULN1
        )
        json_data = {
            "vuln_status": "acknowledged",
            "note": "string",
            "assignees": [],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # Create 2st ticket
        service_name2 = "test_service2"
        upload_file_name = "test_trivy_cyclonedx_asynckit.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(
            sbom_json, self.ticket_response1["pteam_id"], service_name2, upload_file_name
        )
        self.vuln2 = create_vuln(USER1, VULN2)

    def test_it_able_to_filter_when_service_id_is_specified_as_query_parameter(self):
        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids?service_id={self.ticket_response1['service_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert len(response1.json()["vuln_ids"]) == 2
        assert set(response1.json()["vuln_ids"]) == {
            self.ticket_response1["vuln_id"],
            str(self.vuln2.vuln_id),
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] == self.ticket_response1["service_id"]
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] is None
        assert len(response2.json()["vuln_ids"]) == 1
        assert set(response2.json()["vuln_ids"]) == {self.ticket_response1["vuln_id"]}

    def test_it_able_to_filter_when_package_id_is_specified_as_query_parameter(self):
        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids?package_id={self.ticket_response1['package_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert len(response1.json()["vuln_ids"]) == 2
        assert set(response1.json()["vuln_ids"]) == {
            self.ticket_response1["vuln_id"],
            str(self.vuln2.vuln_id),
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] == self.ticket_response1["package_id"]
        assert response2.json()["related_ticket_status"] is None
        assert len(response2.json()["vuln_ids"]) == 1
        assert set(response2.json()["vuln_ids"]) == {self.ticket_response1["vuln_id"]}

    def test_it_able_to_filter_when_solved_is_specified_as_query_parameter(self):
        # Given
        # Change status of ticket1
        json_data = {
            "vuln_status": "completed",
            "note": "string",
            "assignees": [self.ticket_response1["user_id"]],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids?related_ticket_status=solved",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert len(response1.json()["vuln_ids"]) == 2
        assert set(response1.json()["vuln_ids"]) == {
            self.ticket_response1["vuln_id"],
            str(self.vuln2.vuln_id),
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] == "solved"
        assert len(response2.json()["vuln_ids"]) == 1
        assert set(response2.json()["vuln_ids"]) == {self.ticket_response1["vuln_id"]}

    def test_it_able_to_filter_when_unsolved_is_specified_as_query_parameter(self):
        # Given
        # Change status of ticket1
        json_data = {
            "vuln_status": "completed",
            "note": "string",
            "assignees": [self.ticket_response1["user_id"]],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids?related_ticket_status=unsolved",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert len(response1.json()["vuln_ids"]) == 2
        assert set(response1.json()["vuln_ids"]) == {
            self.ticket_response1["vuln_id"],
            str(self.vuln2.vuln_id),
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] == "unsolved"
        assert len(response2.json()["vuln_ids"]) == 1
        assert set(response2.json()["vuln_ids"]) == {str(self.vuln2.vuln_id)}

    def test_vuln_ids_are_sorted_correctly(self):
        """
        Memo
        ticket1 ssvc_deployer_priority is IMMEDIATE
        ticket2 ssvc_deployer_priority is IMMEDIATE
        ticket3 ssvc_deployer_priority is SCHEDULED
        """
        # Given
        # Create 3st ticket
        service_name2 = "test_service3"
        upload_file_name = "test_trivy_cyclonedx_combined-stream.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(
            sbom_json, self.ticket_response1["pteam_id"], service_name2, upload_file_name
        )
        vuln3 = create_vuln(USER1, VULN3)

        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/vuln_ids",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert len(response1.json()["vuln_ids"]) == 3
        vuln_ids_sorted = [
            str(self.vuln2.vuln_id),
            self.ticket_response1["vuln_id"],
            str(vuln3.vuln_id),
        ]
        assert response1.json()["vuln_ids"] == vuln_ids_sorted


class TestGetTicketCountsTiedToServicePackage:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        # Given
        # Create 1st ticket
        service_name1 = "test_service1"
        self.ticket_response1 = ticket_utils.create_ticket(
            testdb, USER1, PTEAM1, service_name1, VULN1
        )
        json_data = {
            "vuln_status": "acknowledged",
            "note": "string",
            "assignees": [],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # Create 2st ticket
        service_name2 = "test_service2"
        upload_file_name = "test_trivy_cyclonedx_asynckit.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(
            sbom_json, self.ticket_response1["pteam_id"], service_name2, upload_file_name
        )
        self.vuln2 = create_vuln(USER1, VULN2)

    def test_it_able_to_filter_when_service_id_is_specified_as_query_parameter(self):
        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts?service_id={self.ticket_response1['service_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert response1.json()["ssvc_priority_count"] == {
            "immediate": 2,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] == self.ticket_response1["service_id"]
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] is None
        assert response2.json()["ssvc_priority_count"] == {
            "immediate": 1,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

    def test_it_able_to_filter_when_package_id_is_specified_as_query_parameter(self):
        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts?package_id={self.ticket_response1['package_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert response1.json()["ssvc_priority_count"] == {
            "immediate": 2,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] == self.ticket_response1["package_id"]
        assert response2.json()["related_ticket_status"] is None
        assert response2.json()["ssvc_priority_count"] == {
            "immediate": 1,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

    def test_it_able_to_filter_when_solved_is_specified_as_query_parameter(self):
        # Given
        # Change status of ticket1
        json_data = {
            "vuln_status": "completed",
            "note": "string",
            "assignees": [self.ticket_response1["user_id"]],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts?related_ticket_status=solved",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert response1.json()["ssvc_priority_count"] == {
            "immediate": 2,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] == "solved"
        assert response2.json()["ssvc_priority_count"] == {
            "immediate": 1,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

    def test_it_able_to_filter_when_unsolved_is_specified_as_query_parameter(self):
        # Given
        # Change status of ticket1
        json_data = {
            "vuln_status": "completed",
            "note": "string",
            "assignees": [self.ticket_response1["user_id"]],
            "scheduled_at": None,
        }
        set_ticket_status(
            USER1,
            self.ticket_response1["pteam_id"],
            self.ticket_response1["ticket_id"],
            json_data,
        )

        # When
        response1 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts",
            headers=headers(USER1),
        )
        response2 = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts?related_ticket_status=unsolved",
            headers=headers(USER1),
        )

        # Then
        assert response1.status_code == 200
        assert response1.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response1.json()["service_id"] is None
        assert response1.json()["package_id"] is None
        assert response1.json()["related_ticket_status"] is None
        assert response1.json()["ssvc_priority_count"] == {
            "immediate": 2,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

        assert response2.status_code == 200
        assert response2.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response2.json()["service_id"] is None
        assert response2.json()["package_id"] is None
        assert response2.json()["related_ticket_status"] == "unsolved"
        assert response2.json()["ssvc_priority_count"] == {
            "immediate": 1,
            "out_of_cycle": 0,
            "scheduled": 0,
            "defer": 0,
        }

    @pytest.mark.parametrize(
        "exploitation, automatable, service_mission_impact, expected_ssvc_priority_count",
        [
            (
                "active",
                "yes",
                "mission_failure",
                {"immediate": 1, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
            ),
            (
                "public_poc",
                "yes",
                "mission_failure",
                {"immediate": 0, "out_of_cycle": 1, "scheduled": 0, "defer": 0},
            ),
            (
                "none",
                "no",
                "mission_failure",
                {"immediate": 0, "out_of_cycle": 0, "scheduled": 1, "defer": 0},
            ),
            (
                "none",
                "no",
                "degraded",
                {"immediate": 0, "out_of_cycle": 0, "scheduled": 0, "defer": 1},
            ),
        ],
    )
    def test_it_should_return_correct_ssvc_priority_count_when_ssvc_is_changed(
        self,
        exploitation,
        automatable,
        service_mission_impact,
        expected_ssvc_priority_count,
    ):
        # Given
        vuln = {
            **VULN1,
            "exploitation": exploitation,
            "automatable": automatable,
        }
        data_service = {"service_mission_impact": service_mission_impact}

        create_vuln(USER1, vuln)

        client.put(
            f"/pteams/{self.ticket_response1['pteam_id']}/services/{self.ticket_response1['service_id']}",
            headers=headers(USER1),
            json=data_service,
        )

        # When
        response = client.get(
            f"/pteams/{self.ticket_response1['pteam_id']}/ticket_counts?service_id={self.ticket_response1['service_id']}&package_id={self.ticket_response1['package_id']}",
            headers=headers(USER1),
        )

        # Then
        assert response.status_code == 200
        assert response.json()["pteam_id"] == self.ticket_response1["pteam_id"]
        assert response.json()["service_id"] == self.ticket_response1["service_id"]
        assert response.json()["package_id"] == self.ticket_response1["package_id"]
        assert response.json()["ssvc_priority_count"] == expected_ssvc_priority_count


class TestPostUploadSBOMFileCycloneDX:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            # Note: all tests in this class use USER1 & PTEAM1
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)

        @dataclass(frozen=True, kw_only=True)
        class LibraryParam:
            purl: str | None
            name: str | None
            group: str | None
            version: str | None

            def to_dict(self) -> dict:
                ret = {}
                if self.purl is not None:
                    ret["bom-ref"] = self.purl
                    ret["purl"] = self.purl
                if self.name is not None:
                    ret["name"] = self.name
                if self.group is not None:
                    ret["group"] = self.group
                if self.version is not None:
                    ret["version"] = self.version
                if ret:  # fill type only if not-empty
                    ret["type"] = "library"
                return ret

        @dataclass(frozen=True, kw_only=True)
        class ApplicationParam:
            name: str | None
            type: str | None
            trivy_type: str | None
            trivy_class: str | None

            def to_dict(self) -> dict:
                ret: dict = {}
                properties: list[dict] = []
                if self.name is not None:
                    ret["name"] = self.name
                if self.type is not None:
                    ret["type"] = self.type
                if self.trivy_type is not None:
                    properties.append({"name": "aquasecurity:trivy:Type", "value": self.trivy_type})
                if self.trivy_class is not None:
                    properties.append(
                        {"name": "aquasecurity:trivy:Class", "value": self.trivy_class}
                    )
                if len(properties) > 0:
                    ret["properties"] = properties
                if ret:  # fill type & bom-ref only if not-empty
                    ret["bom-ref"] = str(uuid4())
                return ret

        @staticmethod
        def gen_sbom_json(
            base_json: dict,
            component_params: dict[ApplicationParam, list[LibraryParam]],
        ) -> dict:
            root_ref = base_json.get("metadata", {}).get("component", {}).get("bom-ref", "")
            components = []
            dependencies = []
            root_depends_on = []
            for application_param, library_params in component_params.items():
                application_dict = application_param.to_dict()
                application_ref = application_dict.get("bom-ref")
                components.append(application_dict)

                application_depends_on = []
                for library_param in library_params:
                    if library_dict := library_param.to_dict():
                        if library_ref := library_dict.get("bom-ref"):
                            application_depends_on.append(library_ref)
                        components.append(library_dict)

                if application_ref:
                    root_depends_on.append(application_ref)
                    dependencies.append(
                        {"ref": application_ref, "dependsOn": application_depends_on}
                    )

            if root_ref:
                dependencies.append({"ref": root_ref, "dependsOn": root_depends_on})
            sbom_json = {
                **base_json,
                "components": components,
                "dependencies": dependencies,
            }
            return sbom_json

        def gen_broken_sbom_json(self, base_json: dict) -> dict:
            application_param = self.ApplicationParam(
                **{
                    "name": "threatconnectome/api/Pipfile.lock",
                    "type": "application",
                    "trivy_type": "pipenv",
                    "trivy_class": "lang-pkgs",
                },
            )
            library_param = self.LibraryParam(
                **{
                    "purl": "pkg:pypi/cryptography@39.0.2",
                    "name": "cryptography",
                    "group": None,
                    "version": "39.0.2",
                },
            )
            components_dict = {application_param: [library_param]}
            # gen normal sbom
            sbom_json = self.gen_sbom_json(base_json, components_dict)
            # overwrite bom-ref -- it will cause dependency mismatch error
            for component in sbom_json["components"]:
                component["bom-ref"] += "xxx"  # does not match with "dependsOn" params
            return sbom_json

        def get_services(self) -> dict:
            response = client.get(f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1))
            return response.json().get("services", {})

        def get_service_dependencies(self, service_id: UUID | str) -> dict:
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/dependencies",
                headers=headers(USER1),
                params={"service_id": str(service_id)},
            )
            return response.json()

        def get_package(
            self, testdb, package_version_id: UUID | str
        ) -> models.PackageVersion | None:
            return testdb.scalars(
                select(models.PackageVersion, models.Package)
                .join(models.Package)
                .where(models.PackageVersion.package_version_id == str(package_version_id))
            ).one_or_none()

        def enable_slack(self, webhook_url: str) -> dict:
            request = {"alert_slack": {"enable": True, "webhook_url": webhook_url}}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=request
            )
            return response.json()

        def enable_mail(self, mail_address: str) -> dict:
            request = {"alert_mail": {"enable": True, "address": mail_address}}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=request
            )
            return response.json()

    class TestCycloneDX15WithTrivy(Common):
        @staticmethod
        def gen_base_json(target_name: str) -> dict:
            return {
                "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "serialNumber": "urn:uuid:5bf250f0-d1be-4c1a-96dc-5f6e62c28cb2",
                "version": 1,
                "metadata": {
                    "timestamp": "2024-07-01T00:00:00+09:00",
                    "tools": [{"vendor": "aquasecurity", "name": "trivy", "version": "0.52.0"}],
                    "component": {
                        "bom-ref": "73c936da-ca45-4ffd-a64b-2a78409d6b07",
                        "type": "application",
                        "name": target_name,
                        "properties": [{"name": "aquasecurity:trivy:SchemaVersion", "value": "2"}],
                    },
                },
            }

        @pytest.mark.parametrize(
            "service_name, component_params, expected_dependency_params",
            # Note: components_params: list[tuple[ApplicationParam, list[LibraryParam]]]
            [
                # test case 1: lang-pkgs
                (
                    "sample service1",
                    [  # input
                        (
                            {  # application
                                "name": "threatconnectome/api/Pipfile.lock",
                                "type": "application",
                                "trivy_type": "pipenv",
                                "trivy_class": "lang-pkgs",
                            },
                            [  # libraries
                                {
                                    "purl": "pkg:pypi/cryptography@39.0.2",
                                    "name": "cryptography",
                                    "group": None,
                                    "version": "39.0.2",
                                },
                            ],
                        ),
                    ],
                    [  # expected
                        {
                            "package_name": "cryptography",
                            "ecosystem": "pypi",
                            "package_manager": "pipenv",
                            "target": "threatconnectome/api/Pipfile.lock",
                            "version": "39.0.2",
                        },
                        {
                            "package_name": "cryptography",
                            "ecosystem": "pypi",
                            "package_manager": "pipenv",
                            "target": "sample target1",  # scan root
                            "version": "39.0.2",
                        },
                    ],
                ),
                # test case 2: os-pkgs
                (
                    "sample service1",
                    [  # input
                        (
                            {  # application
                                "name": "ubuntu",
                                "type": "operating-system",
                                "trivy_type": "ubuntu",
                                "trivy_class": "os-pkgs",
                            },
                            [  # libraries
                                {
                                    "purl": (
                                        "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4"
                                        "?distro=ubuntu-20.04"
                                    ),
                                    "name": "libcrypt1",
                                    "group": None,
                                    "version": "1:4.4.10-10ubuntu4",
                                },
                            ],
                        ),
                    ],
                    [  # expected
                        {
                            "package_name": "libcrypt1",
                            "ecosystem": "ubuntu-20.04",
                            "package_manager": "",
                            "target": "ubuntu",
                            "version": "1:4.4.10-10ubuntu4",
                        },
                        {
                            "package_name": "libcrypt1",
                            "ecosystem": "ubuntu-20.04",
                            "package_manager": "",
                            "target": "sample target1",  # scan root
                            "version": "1:4.4.10-10ubuntu4",
                        },
                    ],
                ),
                # test case 3: lang-pkgs with group
                (
                    "sample service1",
                    [  # input
                        (
                            {  # application
                                "name": "web/package-lock.json",
                                "type": "application",
                                "trivy_type": "npm",
                                "trivy_class": "lang-pkgs",
                            },
                            [  # libraries
                                {
                                    "purl": "pkg:npm/%40nextui-org/button@2.0.26",
                                    "name": "button",
                                    "group": "@nextui-org",
                                    "version": "2.0.26",
                                },
                            ],
                        ),
                    ],
                    [  # expected
                        {
                            "package_name": "@nextui-org/button",
                            "ecosystem": "npm",
                            "package_manager": "npm",
                            "target": "web/package-lock.json",
                            "version": "2.0.26",
                        },
                        {
                            "package_name": "@nextui-org/button",
                            "ecosystem": "npm",
                            "package_manager": "npm",
                            "target": "sample target1",  # scan root
                            "version": "2.0.26",
                        },
                    ],
                ),
                # test case 4: (legacy) lang-pkgs without group
                (
                    "sample service1",
                    [  # input
                        (
                            {  # application
                                "name": "web/package-lock.json",
                                "type": "application",
                                "trivy_type": "npm",
                                "trivy_class": "lang-pkgs",
                            },
                            [  # libraries
                                {
                                    "purl": "pkg:npm/%40nextui-org/button@2.0.26",
                                    "name": "@nextui-org/button",
                                    "group": None,
                                    "version": "2.0.26",
                                },
                            ],
                        ),
                    ],
                    [  # expected
                        {
                            "package_name": "@nextui-org/button",
                            "ecosystem": "npm",
                            "package_manager": "npm",
                            "target": "web/package-lock.json",
                            "version": "2.0.26",
                        },
                        {
                            "package_name": "@nextui-org/button",
                            "ecosystem": "npm",
                            "package_manager": "npm",
                            "target": "sample target1",  # scan root
                            "version": "2.0.26",
                        },
                    ],
                ),
            ],
        )
        def test_dependencies_should_ralated_to_expected_package(
            self, testdb, service_name, component_params, expected_dependency_params
        ) -> None:
            target_name = "sample target1"
            components_dict = {
                self.ApplicationParam(**application_param): [
                    self.LibraryParam(**library_param) for library_param in library_params
                ]
                for application_param, library_params in component_params
            }
            sbom_json = self.gen_sbom_json(self.gen_base_json(target_name), components_dict)

            bg_create_tags_from_sbom_json(sbom_json, self.pteam1.pteam_id, service_name, None)

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1
            now = datetime.now()
            datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
            assert datetime.strptime(
                service1["sbom_uploaded_at"], datetime_format
            ) > now - timedelta(seconds=30)
            assert datetime.strptime(service1["sbom_uploaded_at"], datetime_format) < now

            @dataclass(frozen=True, kw_only=True)
            class DependencyParamsToCheck:
                package_name: str
                ecosystem: str
                package_manager: str
                target: str
                version: str

            created_dependencies = set()
            for dependency in self.get_service_dependencies(service1["service_id"]):
                if package_version := self.get_package(testdb, dependency["package_version_id"]):
                    created_dependencies.add(
                        DependencyParamsToCheck(
                            package_name=package_version.package.name,
                            ecosystem=package_version.package.ecosystem,
                            package_manager=dependency["package_manager"],
                            target=dependency["target"],
                            version=package_version.version,
                        )
                    )

            expected_dependencies = {
                DependencyParamsToCheck(**expected_dependency_param)
                for expected_dependency_param in expected_dependency_params
            }
            assert created_dependencies == expected_dependencies

        @pytest.mark.parametrize(
            "enable_slack, expected_notify",
            [
                (True, True),
                (False, False),
            ],
        )
        def test_notify_sbom_upload_succeeded_by_slack(
            self, mocker, enable_slack, expected_notify
        ) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # setup mocker
            send_slack = mocker.patch("app.notification.alert.send_slack")

            # enable pteam notification
            if enable_slack:
                webhook_url = SAMPLE_SLACK_WEBHOOK_URL
                self.enable_slack(webhook_url)
            else:
                webhook_url = None

            # gen sbom with empty components
            target_name = "sample target1"
            sbom_json = self.gen_sbom_json(self.gen_base_json(target_name), {})

            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1

            if expected_notify:
                expected_slack_blocks = create_slack_blocks_to_notify_sbom_upload_succeeded(
                    str(self.pteam1.pteam_id),
                    self.pteam1.pteam_name,
                    service1["service_id"],
                    service_name,
                    upload_filename,
                )
                send_slack.assert_called_once()
                send_slack.assert_called_with(webhook_url, expected_slack_blocks)
            else:
                send_slack.addrt_not_called()

        @pytest.mark.parametrize(
            "enable_slack, expected_notify",
            [
                (True, True),
                (False, False),
            ],
        )
        def test_notify_sbom_upload_failed_by_slack(
            self, mocker, enable_slack, expected_notify
        ) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # setup mocker
            send_slack = mocker.patch("app.notification.alert.send_slack")

            # enable pteam notification
            if enable_slack:
                webhook_url = SAMPLE_SLACK_WEBHOOK_URL
                self.enable_slack(webhook_url)
            else:
                webhook_url = None

            # gen broken sbom which cause background task error
            target_name = "sample target1"
            sbom_json = self.gen_broken_sbom_json(self.gen_base_json(target_name))

            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1

            if expected_notify:
                expected_slack_blocks = create_slack_blocks_to_notify_sbom_upload_failed(
                    service_name, upload_filename
                )
                send_slack.assert_called_once()
                send_slack.assert_called_with(webhook_url, expected_slack_blocks)
            else:
                send_slack.assert_not_called()

        @pytest.mark.parametrize(
            "enable_mail, expected_notify",
            [
                (True, True),
                (False, False),
            ],
        )
        def test_notify_sbom_upload_succeeded_by_mail(
            self, mocker, enable_mail, expected_notify
        ) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # setup mocker
            send_email = mocker.patch("app.notification.alert.send_email")

            # enable pteam notification
            if enable_mail:
                mail_address = "foobar@example.com"
                self.enable_mail(mail_address)
            else:
                mail_address = None

            # gen sbom with empty components
            target_name = "sample target1"
            sbom_json = self.gen_sbom_json(self.gen_base_json(target_name), {})

            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1

            if expected_notify:
                expected_mail_subject, expected_mail_body = (
                    create_mail_to_notify_sbom_upload_succeeded(
                        str(self.pteam1.pteam_id),
                        self.pteam1.pteam_name,
                        service1["service_id"],
                        service_name,
                        upload_filename,
                    )
                )
                send_email.assert_called_once()
                send_email.assert_called_with(
                    mail_address, SYSTEM_EMAIL, expected_mail_subject, expected_mail_body
                )
            else:
                send_email.assert_not_called()

        @pytest.mark.parametrize(
            "enable_mail, expected_notify",
            [
                (True, True),
                (False, False),
            ],
        )
        def test_notify_sbom_upload_failed_by_mail(
            self, mocker, enable_mail, expected_notify
        ) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # setup mocker
            send_email = mocker.patch("app.notification.alert.send_email")

            # enable pteam notification
            if enable_mail:
                mail_address = "foobar@example.com"
                self.enable_mail(mail_address)
            else:
                mail_address = None

            # gen broken sbom which cause background task error
            target_name = "sample target1"
            sbom_json = self.gen_broken_sbom_json(self.gen_base_json(target_name))

            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1

            if expected_notify:
                expected_mail_subject, expected_mail_body = (
                    create_mail_to_notify_sbom_upload_failed(service_name, upload_filename)
                )
                send_email.assert_called_once()
                send_email.assert_called_with(
                    mail_address, SYSTEM_EMAIL, expected_mail_subject, expected_mail_body
                )
            else:
                send_email.assert_not_called()

        def test_notify_sbom_upload_succeeded_by_log(self, caplog) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # gen sbom with empty components
            target_name = "sample target1"
            sbom_json = self.gen_sbom_json(self.gen_base_json(target_name), {})

            caplog.set_level(INFO)
            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )
            assert [
                ("app.routers.pteams", INFO, f"Start SBOM uploade as a service: {service_name}"),
                ("app.routers.pteams", INFO, f"SBOM uploaded as a service: {service_name}"),
            ] == caplog.record_tuples

        def test_notify_sbom_upload_failed_by_log(self, caplog) -> None:
            service_name = "test service"
            upload_filename = "sample-sbom.json"

            # gen broken sbom which cause background task error
            target_name = "sample target1"
            sbom_json = self.gen_broken_sbom_json(self.gen_base_json(target_name))

            caplog.set_level(INFO)
            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, service_name, upload_filename
            )
            assert [
                ("app.routers.pteams", INFO, f"Start SBOM uploade as a service: {service_name}"),
                (
                    "app.routers.pteams",
                    ERROR,
                    f"Failed uploading SBOM as a service: {service_name}",
                ),
            ] == caplog.record_tuples

    class TestCycloneDX16WithTrivy(TestCycloneDX15WithTrivy):
        @staticmethod
        def gen_base_json(target_name: str) -> dict:
            return {
                "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
                "serialNumber": "urn:uuid:e8d7ac21-ced8-4fe8-851c-3325f90d8c18",
                "version": 1,
                "metadata": {
                    "timestamp": "2024-08-05T03:50:17+00:00",
                    "tools": {
                        "components": [
                            {
                                "type": "application",
                                "group": "aquasecurity",
                                "name": "trivy",
                                "version": "0.54.1",
                            }
                        ]
                    },
                    "component": {
                        "bom-ref": "e6cf3443-266e-4ab4-910d-457e31244caa",
                        "type": "application",
                        "name": target_name,
                        "properties": [{"name": "aquasecurity:trivy:SchemaVersion", "value": "2"}],
                    },
                },
            }


class TestPostUploadPackagesFile:
    def test_sbom_uploaded_at_with_called_upload_tags_file(self):
        # when
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        service_name = "test service 1"

        # When
        ext_packages = [
            {
                "package_name": "test_package_name1",
                "ecosystem": "test_ecosystem1",
                "package_manager": "test_package_manager1",
                "references": [{"target": "target1", "version": "1.0"}],
            }
        ]
        upload_pteam_packages(USER1, pteam1.pteam_id, service_name, ext_packages)

        # Then
        response = client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1))
        services = response.json().get("services", {})
        service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
        assert service1
        now = datetime.now()
        datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
        assert datetime.strptime(service1["sbom_uploaded_at"], datetime_format) > now - timedelta(
            seconds=30
        )
        assert datetime.strptime(service1["sbom_uploaded_at"], datetime_format) < now


class TestDeletePteam:
    def test_it_should_delete_package_when_delete_pteam(self, testdb: Session):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        # Uploaded sbom file.
        # Create package, package_version, service and dependency table
        service_name1 = "test_service1"
        upload_file_name = "test_trivy_cyclonedx_axios.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

        # Saerch service table
        service_id = testdb.scalars(
            select(models.Service.service_id).where(
                models.Service.pteam_id == str(pteam1.pteam_id),
                models.Service.service_name == service_name1,
            )
        ).one()

        dependencies_response = client.get(
            f"/pteams/{pteam1.pteam_id}/dependencies?service_id={service_id}",
            headers=headers(USER1),
        )
        created_dependency = dependencies_response.json()[0]
        package_version_id = created_dependency["package_version_id"]
        package_id = created_dependency["package_id"]

        # When
        client.delete(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1))

        # Then
        package_version = testdb.scalars(
            select(models.PackageVersion).where(
                models.PackageVersion.package_version_id == str(package_version_id)
            )
        ).one_or_none()
        assert package_version is None
        package = testdb.scalars(
            select(models.Package).where(models.Package.package_id == str(package_id))
        ).one_or_none()
        assert package is None


class TestDeleteService:
    def test_it_should_delete_package_when_delete_service(self, testdb: Session):
        # Given
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        # Uploaded sbom file.
        # Create package, package_version, service and dependency table
        service_name1 = "test_service1"
        upload_file_name = "test_trivy_cyclonedx_axios.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = json.load(sbom)

        bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

        # Saerch service table
        service_id = testdb.scalars(
            select(models.Service.service_id).where(
                models.Service.pteam_id == str(pteam1.pteam_id),
                models.Service.service_name == service_name1,
            )
        ).one()

        dependencies_response = client.get(
            f"/pteams/{pteam1.pteam_id}/dependencies?service_id={service_id}",
            headers=headers(USER1),
        )
        created_dependency = dependencies_response.json()[0]
        package_version_id = created_dependency["package_version_id"]
        package_id = created_dependency["package_id"]

        # When
        client.delete(f"/pteams/{pteam1.pteam_id}/services/{service_id}", headers=headers(USER1))

        # Then
        package_version = testdb.scalars(
            select(models.PackageVersion).where(
                models.PackageVersion.package_version_id == str(package_version_id)
            )
        ).one_or_none()
        assert package_version is None
        package = testdb.scalars(
            select(models.Package).where(models.Package.package_id == str(package_id))
        ).one_or_none()
        assert package is None
