from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import ERROR, INFO
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

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
    TAG1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    upload_pteam_tags,
)

client = TestClient(app)


@pytest.mark.parametrize(
    "exploitation, topic_status1, topic_status2, expected_solved_count, expected_unsolved_count",
    [
        (
            "none",
            models.TopicStatusType.completed,
            models.TopicStatusType.completed,
            {"immediate": 0, "out_of_cycle": 2, "scheduled": 0, "defer": 0},
            {"immediate": 0, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
        ),
        (
            "none",
            models.TopicStatusType.completed,
            models.TopicStatusType.acknowledged,
            {"immediate": 0, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
            {"immediate": 0, "out_of_cycle": 1, "scheduled": 0, "defer": 0},
        ),
        (
            "public_poc",
            models.TopicStatusType.acknowledged,
            models.TopicStatusType.completed,
            {"immediate": 0, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
            {"immediate": 0, "out_of_cycle": 1, "scheduled": 0, "defer": 0},
        ),
        (
            "active",
            models.TopicStatusType.acknowledged,
            models.TopicStatusType.acknowledged,
            {"immediate": 0, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
            {"immediate": 2, "out_of_cycle": 0, "scheduled": 0, "defer": 0},
        ),
    ],
)
def test_it_should_return_ssvc_priority_count_num_based_on_tickte_status(
    testdb,
    exploitation,
    topic_status1,
    topic_status2,
    expected_solved_count,
    expected_unsolved_count,
):
    @staticmethod
    def _set_ticket_status(
        user: dict,
        pteam_id: str,
        service_id: str,
        ticket_id: str,
        topic_status: models.TopicStatusType,
    ) -> None:
        post_topicstatus_url = f"/pteams/{pteam_id}/services/{service_id}/ticketstatus/{ticket_id}"
        status_request = {
            "topic_status": topic_status,
            "assignees": [],
            "note": "",
            "scheduled_at": None,
        }
        client.put(
            post_topicstatus_url,
            headers=headers(user),
            json=status_request,
        )

    # Given
    # create ticket
    topic = {
        **TOPIC1,
        "exploitation": exploitation,
    }

    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, topic)

    # set topic_status
    get_tickets_url = (
        f"/pteams/{ticket_response['pteam_id']}/services/"
        f"{ticket_response['service_id']}/topics/{ticket_response['topic_id']}/tags/{ticket_response['tag_id']}/tickets"
    )
    tickets = client.get(get_tickets_url, headers=headers(USER1)).json()
    _set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        tickets[0]["ticket_id"],
        topic_status1,
    )
    _set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        tickets[1]["ticket_id"],
        topic_status2,
    )

    # When
    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    response = response.json()

    # Then
    # common
    assert response["pteam_id"] == ticket_response["pteam_id"]
    assert response["service_id"] == ticket_response["service_id"]
    assert response["tag_id"] == ticket_response["tag_id"]
    # solved
    assert response["solved"]["ssvc_priority_count"] == expected_solved_count
    # unsolved
    assert response["unsolved"]["ssvc_priority_count"] == expected_unsolved_count


def test_sbom_uploaded_at_with_called_upload_tags_file():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service_name = "test service 1"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_name, {TAG1: [("Pipfile.lock", "1.0.0")]})

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
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}/dependencies",
                headers=headers(USER1),
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

        @pytest.mark.skip(reason="it is not able to make threat at the time of sbom upload.")
        # @pytest.mark.parametrize(
        #     "service_name, component_params, vulnerable_versions, expected_threat_params",
        #     # Note: components_params: list[tuple[ApplicationParam, list[LibraryParam]]]
        #     #       vulnerable_versions: {str: list[str]} -- {tag_name: ["< 2.0", ...]}
        #     [
        #         # test case 1: lang-pkgs
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "threatconnectome/api/Pipfile.lock",
        #                         "type": "application",
        #                         "trivy_type": "pipenv",
        #                         "trivy_class": "lang-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": "pkg:pypi/cryptography@39.0.2",
        #                             "name": "cryptography",
        #                             "group": None,
        #                             "version": "39.0.2",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "cryptography:pypi:pipenv": ["<40.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "cryptography:pypi:pipenv",
        #                     "target": "threatconnectome/api/Pipfile.lock",
        #                     "version": "39.0.2",
        #                 },
        #                 {
        #                     "tag_name": "cryptography:pypi:pipenv",
        #                     "target": "sample target1",  # scan root
        #                     "version": "39.0.2",
        #                 },
        #             ],
        #         ),
        #         # test case 1b: lang-pkgs with not vulnerable version
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "threatconnectome/api/Pipfile.lock",
        #                         "type": "application",
        #                         "trivy_type": "pipenv",
        #                         "trivy_class": "lang-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": "pkg:pypi/cryptography@39.0.2",
        #                             "name": "cryptography",
        #                             "group": None,
        #                             "version": "39.0.2",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "cryptography:pypi:pipenv": ["<30.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "cryptography:pypi:pipenv",
        #                     "target": "threatconnectome/api/Pipfile.lock",
        #                     "version": "39.0.2",
        #                 },
        #                 {
        #                     "tag_name": "cryptography:pypi:pipenv",
        #                     "target": "sample target1",  # scan root
        #                     "version": "39.0.2",
        #                 },
        #             ],
        #         ),
        #         # test case 2: os-pkgs
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "ubuntu",
        #                         "type": "operating-system",
        #                         "trivy_type": "ubuntu",
        #                         "trivy_class": "os-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": (
        #                                 "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4"
        #                                 "?distro=ubuntu-20.04"
        #                             ),
        #                             "name": "libcrypt1",
        #                             "group": None,
        #                             "version": "1:4.4.10-10ubuntu4",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "libcrypt1:ubuntu-20.04:": ["<4.5.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "libcrypt1:ubuntu-20.04:",
        #                     "target": "ubuntu",
        #                     "version": "1:4.4.10-10ubuntu4",
        #                 },
        #                 {
        #                     "tag_name": "libcrypt1:ubuntu-20.04:",
        #                     "target": "sample target1",  # scan root
        #                     "version": "1:4.4.10-10ubuntu4",
        #                 },
        #             ],
        #         ),
        #         # test case 2b: os-pkgs with not vulnerable version
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "ubuntu",
        #                         "type": "operating-system",
        #                         "trivy_type": "ubuntu",
        #                         "trivy_class": "os-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": (
        #                                 "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4"
        #                                 "?distro=ubuntu-20.04"
        #                             ),
        #                             "name": "libcrypt1",
        #                             "group": None,
        #                             "version": "1:4.4.10-10ubuntu4",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "libcrypt1:ubuntu-20.04:": ["<4.3.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "libcrypt1:ubuntu-20.04:",
        #                     "target": "ubuntu",
        #                     "version": "1:4.4.10-10ubuntu4",
        #                 },
        #                 {
        #                     "tag_name": "libcrypt1:ubuntu-20.04:",
        #                     "target": "sample target1",  # scan root
        #                     "version": "1:4.4.10-10ubuntu4",
        #                 },
        #             ],
        #         ),
        #         # test case 3: lang-pkgs with group
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "web/package-lock.json",
        #                         "type": "application",
        #                         "trivy_type": "npm",
        #                         "trivy_class": "lang-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": "pkg:npm/%40nextui-org/button@2.0.26",
        #                             "name": "button",
        #                             "group": "@nextui-org",
        #                             "version": "2.0.26",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "@nextui-org/button:npm:npm": ["< 2.1.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "@nextui-org/button:npm:npm",
        #                     "target": "web/package-lock.json",
        #                     "version": "2.0.26",
        #                 },
        #                 {
        #                     "tag_name": "@nextui-org/button:npm:npm",
        #                     "target": "sample target1",  # scan root
        #                     "version": "2.0.26",
        #                 },
        #             ],
        #         ),
        #         # test case 4: (legacy) lang-pkgs without group
        #         (
        #             "sample service1",
        #             [  # input
        #                 (
        #                     {  # application
        #                         "name": "web/package-lock.json",
        #                         "type": "application",
        #                         "trivy_type": "npm",
        #                         "trivy_class": "lang-pkgs",
        #                     },
        #                     [  # libraries
        #                         {
        #                             "purl": "pkg:npm/%40nextui-org/button@2.0.26",
        #                             "name": "@nextui-org/button",
        #                             "group": None,
        #                             "version": "2.0.26",
        #                         },
        #                     ],
        #                 ),
        #             ],
        #             {  # vulnerable_versions
        #                 "@nextui-org/button:npm:npm": ["< 2.1.0"],
        #             },
        #             [  # expected
        #                 {
        #                     "tag_name": "@nextui-org/button:npm:npm",
        #                     "target": "web/package-lock.json",
        #                     "version": "2.0.26",
        #                 },
        #                 {
        #                     "tag_name": "@nextui-org/button:npm:npm",
        #                     "target": "sample target1",  # scan root
        #                     "version": "2.0.26",
        #                 },
        #             ],
        #         ),
        #     ],
        # )
        def test_create_threats_based_on_sbom(
            self,
            service_name,
            component_params,
            vulnerable_versions,
            expected_threat_params,
            testdb,
        ) -> None:
            tag_names = list(vulnerable_versions.keys())
            actions = [
                {
                    "action": "sample action 1",
                    "action_type": models.ActionType.elimination,
                    "recommended": True,
                    "ext": {
                        "tags": tag_names,
                        "vulnerable_versions": vulnerable_versions,
                    },
                }
            ]
            topic1 = create_topic(USER1, {**TOPIC1, "tags": tag_names, "actions": actions})

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

            @dataclass(frozen=True, kw_only=True)
            class ThreatParamsToCheck:
                tag_name: str
                target: str
                version: str
                title: str

            db_threats = testdb.execute(
                select(
                    models.Threat.dependency_id,
                    models.Dependency.version,
                    models.Dependency.target,
                    models.Tag.tag_name,
                    models.Topic.title,
                )
                .join(
                    models.Dependency,
                    models.Dependency.dependency_id == models.Threat.dependency_id,
                )
                .join(models.Tag)
                .join(models.Topic)
                .where(models.Dependency.service_id == service1["service_id"])
            ).all()

            created_threats = {
                ThreatParamsToCheck(
                    tag_name=db_threat.tag_name,
                    target=db_threat.target,
                    version=db_threat.version,
                    title=db_threat.title,
                )
                for db_threat in db_threats
            }
            expected_threats = {
                ThreatParamsToCheck(**expected_threat_param, title=topic1.title)
                for expected_threat_param in expected_threat_params
            }
            assert created_threats == expected_threats

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
