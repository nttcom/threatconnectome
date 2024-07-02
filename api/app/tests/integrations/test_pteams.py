from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    ACTION1,
    PTEAM1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_service_topicstatus,
    create_user,
    headers,
)

client = TestClient(app)


@pytest.mark.parametrize(
    "topic_status, solved_num, unsolved_num",
    [
        (models.TopicStatusType.completed, 1, 0),
    ],
)
def test_it_should_return_solved_number_based_on_ticket_status(
    testdb, topic_status, solved_num, unsolved_num
):

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["solved"]["topic_ticket_ids"]) == solved_num
    assert (
        ticket_response["ticket_id"] in response["solved"]["topic_ticket_ids"][0]["ticket_ids"][0]
    )
    assert response["solved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["unsolved"]["topic_ticket_ids"]) == unsolved_num


@pytest.mark.parametrize(
    "topic_status, solved_num, unsolved_num",
    [
        (models.TopicStatusType.acknowledged, 0, 1),
        (models.TopicStatusType.scheduled, 0, 1),
    ],
)
def test_it_should_return_unsolved_number_based_on_ticket_status(
    testdb, topic_status, solved_num, unsolved_num
):

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1, ACTION1)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["solved"]["topic_ticket_ids"]) == solved_num

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert len(response["unsolved"]["topic_ticket_ids"]) == unsolved_num
    assert (
        ticket_response["ticket_id"] in response["unsolved"]["topic_ticket_ids"][0]["ticket_ids"][0]
    )
    assert response["unsolved"]["topic_ticket_ids"][0]["topic_id"] == ticket_response["topic_id"]


@pytest.mark.parametrize(
    "threat_impact, topic_status, solved_threat_impact_count, unsolved_threat_impact_count",
    [
        (
            1,
            models.TopicStatusType.completed,
            {"1": 1, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            2,
            models.TopicStatusType.completed,
            {"1": 0, "2": 1, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            3,
            models.TopicStatusType.completed,
            {"1": 0, "2": 0, "3": 1, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            4,
            models.TopicStatusType.completed,
            {"1": 0, "2": 0, "3": 0, "4": 1},
            {"1": 0, "2": 0, "3": 0, "4": 0},
        ),
        (
            1,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 1, "2": 0, "3": 0, "4": 0},
        ),
        (
            2,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 1, "3": 0, "4": 0},
        ),
        (
            3,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 1, "4": 0},
        ),
        (
            4,
            models.TopicStatusType.acknowledged,
            {"1": 0, "2": 0, "3": 0, "4": 0},
            {"1": 0, "2": 0, "3": 0, "4": 1},
        ),
    ],
)
def test_it_shoud_return_threat_impact_count_num_based_on_tickte_status(
    testdb, threat_impact, topic_status, solved_threat_impact_count, unsolved_threat_impact_count
):
    topic = {
        **TOPIC1,
        "threat_impact": threat_impact,
    }

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic, ACTION1)

    json_data = {
        "topic_status": topic_status,
        "note": "string",
        "assignees": [],
        "scheduled_at": str(datetime.now()),
    }
    create_service_topicstatus(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["topic_id"],
        ticket_response["tag_id"],
        json_data,
    )

    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/ticket_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # solved
    assert response["solved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["solved"]["service_id"] == ticket_response["service_id"]
    assert response["solved"]["tag_id"] == ticket_response["tag_id"]
    assert response["solved"]["threat_impact_count"] == solved_threat_impact_count

    # unsolved
    assert response["unsolved"]["pteam_id"] == ticket_response["pteam_id"]
    assert response["unsolved"]["service_id"] == ticket_response["service_id"]
    assert response["unsolved"]["tag_id"] == ticket_response["tag_id"]
    assert response["unsolved"]["threat_impact_count"] == unsolved_threat_impact_count


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

        def get_services(self) -> dict:
            response = client.get(f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1))
            return response.json().get("services", {})

        def get_service_dependencies(self, service_id: UUID | str) -> dict:
            response = client.get(
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}/dependencies",
                headers=headers(USER1),
            )
            return response.json()

        def get_tag(self, tag_id: UUID | str) -> dict:
            response = client.get(f"/tags/{tag_id}", headers=headers(USER1))
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
                            "tag_name": "cryptography:pypi:pipenv",
                            "target": "threatconnectome/api/Pipfile.lock",
                            "version": "39.0.2",
                        },
                        {
                            "tag_name": "cryptography:pypi:pipenv",
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
                            "tag_name": "libcrypt1:ubuntu-20.04:",
                            "target": "ubuntu",
                            "version": "1:4.4.10-10ubuntu4",
                        },
                        {
                            "tag_name": "libcrypt1:ubuntu-20.04:",
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
                        {  # FIXME: should be "@nextui-org/button:npm:npm" ?
                            "tag_name": "@nextui-org:button:npm:npm",
                            "target": "web/package-lock.json",
                            "version": "2.0.26",
                        },
                        {
                            "tag_name": "@nextui-org:button:npm:npm",
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
                            "tag_name": "@nextui-org/button:npm:npm",
                            "target": "web/package-lock.json",
                            "version": "2.0.26",
                        },
                        {
                            "tag_name": "@nextui-org/button:npm:npm",
                            "target": "sample target1",  # scan root
                            "version": "2.0.26",
                        },
                    ],
                ),
            ],
        )
        def test_create_dependencies_based_on_sbom(
            self, service_name, component_params, expected_dependency_params
        ) -> None:
            target_name = "sample target1"
            components_dict = {
                self.ApplicationParam(**application_param): [
                    self.LibraryParam(**library_param) for library_param in library_params
                ]
                for application_param, library_params in component_params
            }
            sbom_json = self.gen_sbom_json(self.gen_base_json(target_name), components_dict)

            bg_create_tags_from_sbom_json(sbom_json, self.pteam1.pteam_id, service_name, True)

            services = self.get_services()
            service1 = next(filter(lambda x: x["service_name"] == service_name, services), None)
            assert service1

            @dataclass(frozen=True, kw_only=True)
            class DependencyParamsToCheck:
                tag_name: str
                target: str
                version: str

            created_dependencies = {
                DependencyParamsToCheck(
                    tag_name=self.get_tag(dependency["tag_id"])["tag_name"],
                    target=dependency["target"],
                    version=dependency["version"],
                )
                for dependency in self.get_service_dependencies(service1["service_id"])
            }
            expected_dependencies = {
                DependencyParamsToCheck(**expected_dependency_param)
                for expected_dependency_param in expected_dependency_params
            }
            assert created_dependencies == expected_dependencies
