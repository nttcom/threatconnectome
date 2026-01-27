import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models, persistence
from app.constants import (
    SYSTEM_EMAIL,
)
from app.eol_constants import EOL_WARNING_THRESHOLD_DAYS
from app.main import app
from app.notification.mail import (
    create_mail_alert_for_new_vuln,
)
from app.notification.slack import (
    create_slack_pteam_alert_blocks_for_new_vuln,
)
from app.routers.eols import _bg_check_eol_notification
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    SAMPLE_SLACK_WEBHOOK_URL,
    SERVICE1,
    USER1,
    VULN1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    create_vuln,
    headers,
    headers_with_api_key,
    set_ticket_status,
)

client = TestClient(app)


class TestAlert:
    class TestAlertByPutVuln:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)

            # Upload the SBOM file and create dependency information
            upload_file_name = "test_trivy_cyclonedx_axios.json"
            sbom_file = (
                Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
            )
            with open(sbom_file, "r") as sbom:
                sbom_json = sbom.read()
            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, SERVICE1, upload_file_name
            )

            # Get service ID, package version, and package ID from the database
            service_id = testdb.scalars(
                select(models.Service.service_id).where(
                    models.Service.pteam_id == str(self.pteam1.pteam_id),
                    models.Service.service_name == SERVICE1,
                )
            ).one()
            self.service1 = {
                "service_id": str(service_id),
                "service_name": SERVICE1,
            }

            # Get dependency information (PackageVersion) from the database
            package_version = testdb.scalars(select(models.PackageVersion)).one()
            self.package_version1 = package_version

        def test_it_should_alert_by_mail_when_put_matched_vuln(self, testdb, mocker):
            # Given
            address = "account0@example.com"
            webhook_url = SAMPLE_SLACK_WEBHOOK_URL + "0"
            pteam_request = {
                "alert_slack": {
                    "enable": False,
                    "webhook_url": webhook_url,
                },
                "alert_mail": {
                    "enable": True,
                    "address": address,
                },
            }
            client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=pteam_request
            )

            dependencies = persistence.get_dependencies_from_service_id_and_package_id(
                testdb, self.service1["service_id"], self.package_version1.package_id
            )
            if len(dependencies) == 0:
                raise Exception("Dependency not found")

            # When
            send_email = mocker.patch("app.notification.alert.send_email")
            vuln1 = create_vuln(USER1, VULN1)

            # Then
            send_email.assert_called_once()

            exp_subject, exp_body = create_mail_alert_for_new_vuln(
                vuln1.title,
                models.SSVCDeployerPriorityEnum.IMMEDIATE,
                PTEAM1["pteam_name"],
                self.pteam1.pteam_id,
                self.package_version1.package.name,
                self.package_version1.package.ecosystem,
                dependencies[0].package_manager,
                self.package_version1.package_id,
                self.service1["service_id"],
                [self.service1["service_name"]],
            )
            send_email.assert_called_with(address, SYSTEM_EMAIL, exp_subject, exp_body)

        def test_it_should_alert_by_slack_when_put_matched_vuln(self, mocker):
            # Given
            address = "account0@example.com"
            webhook_url = SAMPLE_SLACK_WEBHOOK_URL + "0"
            pteam_request = {
                "alert_slack": {
                    "enable": True,
                    "webhook_url": webhook_url,
                },
                "alert_mail": {
                    "enable": False,
                    "address": address,
                },
            }
            client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=pteam_request
            )

            # When
            send_slack = mocker.patch("app.notification.alert.send_slack")
            vuln1 = create_vuln(USER1, VULN1)

            # Then
            send_slack.assert_called_once()

            slack_message_blocks = create_slack_pteam_alert_blocks_for_new_vuln(
                self.pteam1.pteam_id,
                PTEAM1["pteam_name"],
                self.package_version1.package_id,
                self.package_version1.package.name,
                vuln1.vuln_id,
                vuln1.title,
                models.SSVCDeployerPriorityEnum.IMMEDIATE,
                self.service1["service_id"],
                [self.service1["service_name"]],
            )
            send_slack.assert_called_with(webhook_url, slack_message_blocks)

        def test_it_should_not_alert_by_mail_and_slack_when_alert_enable_is_false(self, mocker):
            # Given
            address = "account0@example.com"
            webhook_url = SAMPLE_SLACK_WEBHOOK_URL + "0"
            pteam_request = {
                "alert_slack": {
                    "enable": False,
                    "webhook_url": webhook_url,
                },
                "alert_mail": {
                    "enable": False,
                    "address": address,
                },
            }
            client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=pteam_request
            )

            # When
            send_slack = mocker.patch("app.notification.alert.send_slack")
            send_email = mocker.patch("app.notification.alert.send_email")
            create_vuln(USER1, VULN1)

            # Then
            send_slack.assert_not_called()
            send_email.assert_not_called()

    class TestAlertByPutService:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)

            # Upload the SBOM file and create dependency information
            upload_file_name = "test_trivy_cyclonedx_axios.json"
            sbom_file = (
                Path(__file__).resolve().parent.parent / "common" / "upload_test" / upload_file_name
            )
            with open(sbom_file, "r") as sbom:
                sbom_json = sbom.read()
            bg_create_tags_from_sbom_json(
                sbom_json, self.pteam1.pteam_id, SERVICE1, upload_file_name
            )

            # Get service ID, package version, and package ID from the database
            service_id = testdb.scalars(
                select(models.Service.service_id).where(
                    models.Service.pteam_id == str(self.pteam1.pteam_id),
                    models.Service.service_name == SERVICE1,
                )
            ).one()
            self.service1 = {
                "service_id": str(service_id),
                "service_name": SERVICE1,
            }

            # Get dependency information (PackageVersion) from the database
            package_version = testdb.scalars(select(models.PackageVersion)).one()
            self.package_version1 = package_version

            self.webhook_url = SAMPLE_SLACK_WEBHOOK_URL + "0"
            pteam_request = {
                "alert_slack": {
                    "enable": True,
                    "webhook_url": self.webhook_url,
                },
                "alert_mail": {
                    "enable": True,
                    "address": "account0@example.com",
                },
            }
            client.put(
                f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=pteam_request
            )

            request = {
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            }

            client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}",
                headers=headers(USER1),
                json=request,
            )

            self.vuln1 = create_vuln(USER1, VULN1)

        def test_it_should_alert_when_ssvc_exceeds_threshold(self, mocker):
            # Given
            request = {
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "service_safety_impact": models.SafetyImpactEnum.CATASTROPHIC.value,
            }

            # When
            send_slack = mocker.patch("app.notification.alert.send_slack")
            service_id = self.service1["service_id"]
            client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}",
                headers=headers(USER1),
                json=request,
            )

            # Then
            send_slack.assert_called_once()

            slack_message_blocks = create_slack_pteam_alert_blocks_for_new_vuln(
                self.pteam1.pteam_id,
                PTEAM1["pteam_name"],
                self.package_version1.package_id,
                self.package_version1.package.name,
                self.vuln1.vuln_id,
                self.vuln1.title,
                models.SSVCDeployerPriorityEnum.IMMEDIATE,
                self.service1["service_id"],
                [self.service1["service_name"]],
            )
            send_slack.assert_called_with(self.webhook_url, slack_message_blocks)

        def test_it_should_not_alert_when_ssvc_not_exceeds_threshold(self, mocker):
            # Given
            request = {
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            }

            # When
            send_slack = mocker.patch("app.notification.alert.send_slack")
            service_id = self.service1["service_id"]
            client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}",
                headers=headers(USER1),
                json=request,
            )

            # Then
            send_slack.assert_not_called()

        def test_it_should_not_alert_when_ticket_completed(self, testdb, mocker):
            # Given
            service_id = self.service1["service_id"]
            ticket_id = testdb.scalars(
                select(models.Ticket.ticket_id).where(
                    models.Service.pteam_id == str(self.pteam1.pteam_id),
                    models.Service.service_id == service_id,
                )
            ).first()

            put_ticket_request = {
                "ticket_status": {
                    "ticket_handling_status": "completed",
                }
            }
            set_ticket_status(
                USER1,
                self.pteam1.pteam_id,
                ticket_id,
                put_ticket_request,
            )
            request = {
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "service_safety_impact": models.SafetyImpactEnum.CATASTROPHIC.value,
            }

            # When
            send_slack = mocker.patch("app.notification.alert.send_slack")
            client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{service_id}",
                headers=headers(USER1),
                json=request,
            )

            # Then
            send_slack.assert_not_called()

    class TestAlertByPutEoLNotifications:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            create_user(USER1)
            pteam_test_data = copy.deepcopy(PTEAM1)
            pteam_test_data["alert_slack"]["webhook_url"] = SAMPLE_SLACK_WEBHOOK_URL + "0"
            pteam_test_data["alert_mail"]["enable"] = True
            pteam_test_data["alert_mail"]["address"] = "account0@example.com"
            self.pteam = create_pteam(USER1, pteam_test_data)

            # register ubuntu-20.04
            self.service_name1 = "test_service1"
            upload_file_name1 = "trivy-ubuntu2004.cdx.json"
            sbom_file1 = (
                Path(__file__).resolve().parent.parent
                / "common"
                / "upload_test"
                / upload_file_name1
            )
            with open(sbom_file1, "r") as sbom:
                sbom_json1 = sbom.read()

            bg_create_tags_from_sbom_json(
                sbom_json1, self.pteam.pteam_id, self.service_name1, upload_file_name1
            )

            # register axios 1.6.7
            service_name2 = "test_service2"
            upload_file_name2 = "test_trivy_cyclonedx_axios.json"
            sbom_file2 = (
                Path(__file__).resolve().parent.parent
                / "common"
                / "upload_test"
                / upload_file_name2
            )
            with open(sbom_file2, "r") as sbom:
                sbom_json2 = sbom.read()

            bg_create_tags_from_sbom_json(
                sbom_json2, self.pteam.pteam_id, service_name2, upload_file_name2
            )

        def test_it_should_alert_when_eol_from_within_six_months(self, testdb, mocker):
            # Given

            # Create EcosystemEoLDependency
            eol_product_id_1 = str(uuid4())
            eol_from_date1 = (
                datetime.now(timezone.utc) + timedelta(days=EOL_WARNING_THRESHOLD_DAYS)
            ).strftime("%Y-%m-%d")
            eol_product_1_request: dict[str, Any] = {
                "name": "product_1",
                "product_category": models.ProductCategoryEnum.RUNTIME,
                "description": "product 1 description",
                "is_ecosystem": True,
                "matching_name": "product_1",
                "eol_versions": [
                    {
                        "version": "20.04",
                        "release_date": "2021-01-01",
                        "eol_from": eol_from_date1,
                        "matching_version": "ubuntu-20.04",
                    }
                ],
            }

            client.put(
                f"/eols/{eol_product_id_1}",
                headers=headers_with_api_key(USER1),
                json=eol_product_1_request,
            )

            ecosystem_eol_dependency = testdb.scalars(
                select(models.EcosystemEoLDependency)
                .join(
                    models.EoLVersion,
                    models.EcosystemEoLDependency.eol_version_id
                    == models.EoLVersion.eol_version_id,
                )
                .join(
                    models.EoLProduct,
                    models.EoLProduct.eol_product_id == models.EoLVersion.eol_product_id,
                )
                .where(models.EoLProduct.eol_product_id == eol_product_id_1)
            ).one()

            ecosystem_eol_dependency.eol_notification_sent = False
            testdb.commit()

            # Create PackageEoLDependency
            eol_product_id_2 = str(uuid4())
            eol_from_date2 = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")
            eol_product_2_request: dict[str, Any] = {
                "name": "product_2",
                "product_category": models.ProductCategoryEnum.PACKAGE,
                "description": "product 2 description",
                "is_ecosystem": False,
                "matching_name": "axios",
                "eol_versions": [
                    {
                        "version": "1.6.7",
                        "release_date": "2019-01-01",
                        "eol_from": eol_from_date2,
                        "matching_version": "1.6.7",
                    }
                ],
            }

            client.put(
                f"/eols/{eol_product_id_2}",
                headers=headers_with_api_key(USER1),
                json=eol_product_2_request,
            )

            package_eol_dependency = testdb.scalars(
                select(models.PackageEoLDependency)
                .join(
                    models.EoLVersion,
                    models.PackageEoLDependency.eol_version_id == models.EoLVersion.eol_version_id,
                )
                .join(
                    models.EoLProduct,
                    models.EoLProduct.eol_product_id == models.EoLVersion.eol_product_id,
                )
                .where(models.EoLProduct.eol_product_id == eol_product_id_2)
            ).one()

            package_eol_dependency.eol_notification_sent = False
            testdb.commit()

            send_slack = mocker.patch("app.notification.alert.send_slack")
            send_mail = mocker.patch("app.notification.alert.send_email")

            # When
            _bg_check_eol_notification()

            # Then
            assert send_slack.call_count == 2
            assert send_mail.call_count == 2
            assert ecosystem_eol_dependency.eol_notification_sent is True
            assert package_eol_dependency.eol_notification_sent is True

        def test_it_should_not_alert_when_eol_notification_already_sent(self, testdb, mocker):
            # Given
            eol_product_id_1 = str(uuid4())
            eol_from_date1 = (
                datetime.now(timezone.utc) + timedelta(days=EOL_WARNING_THRESHOLD_DAYS)
            ).strftime("%Y-%m-%d")
            eol_product_1_request: dict[str, Any] = {
                "name": "product_1",
                "product_category": models.ProductCategoryEnum.RUNTIME,
                "description": "product 1 description",
                "is_ecosystem": True,
                "matching_name": "product_1",
                "eol_versions": [
                    {
                        "version": "20.04",
                        "release_date": "2021-01-01",
                        "eol_from": eol_from_date1,
                        "matching_version": "ubuntu-20.04",
                    }
                ],
            }

            client.put(
                f"/eols/{eol_product_id_1}",
                headers=headers_with_api_key(USER1),
                json=eol_product_1_request,
            )

            # TODO: Delete after implementing the notification feature for EOL data registration.
            ecosystem_eol_dependency = testdb.scalars(
                select(models.EcosystemEoLDependency)
                .join(
                    models.EoLVersion,
                    models.EcosystemEoLDependency.eol_version_id
                    == models.EoLVersion.eol_version_id,
                )
                .join(
                    models.EoLProduct,
                    models.EoLProduct.eol_product_id == models.EoLVersion.eol_product_id,
                )
                .where(models.EoLProduct.eol_product_id == eol_product_id_1)
            ).one()
            ecosystem_eol_dependency.eol_notification_sent = True
            testdb.commit()

            send_slack = mocker.patch("app.notification.alert.send_slack")
            send_mail = mocker.patch("app.notification.alert.send_email")

            # When
            _bg_check_eol_notification()

            # Then
            send_slack.assert_not_called()
            send_mail.assert_not_called()

        def test_it_should_not_alert_when_eol_from_more_than_six_months(self, testdb, mocker):
            # Given
            eol_product_id_1 = str(uuid4())
            EOL_NOT_WARNING_THRESHOLD_DAYS = 181
            eol_from_date1 = (
                datetime.now(timezone.utc) + timedelta(days=EOL_NOT_WARNING_THRESHOLD_DAYS)
            ).strftime("%Y-%m-%d")
            eol_product_1_request: dict[str, Any] = {
                "name": "product_1",
                "product_category": models.ProductCategoryEnum.RUNTIME,
                "description": "product 1 description",
                "is_ecosystem": True,
                "matching_name": "product_1",
                "eol_versions": [
                    {
                        "version": "20.04",
                        "release_date": "2021-01-01",
                        "eol_from": eol_from_date1,
                        "matching_version": "ubuntu-20.04",
                    }
                ],
            }

            client.put(
                f"/eols/{eol_product_id_1}",
                headers=headers_with_api_key(USER1),
                json=eol_product_1_request,
            )

            ecosystem_eol_dependency = testdb.scalars(
                select(models.EcosystemEoLDependency)
                .join(
                    models.EoLVersion,
                    models.EcosystemEoLDependency.eol_version_id
                    == models.EoLVersion.eol_version_id,
                )
                .join(
                    models.EoLProduct,
                    models.EoLProduct.eol_product_id == models.EoLVersion.eol_product_id,
                )
                .where(models.EoLProduct.eol_product_id == eol_product_id_1)
            ).one()

            ecosystem_eol_dependency.eol_notification_sent = False
            testdb.commit()

            send_slack = mocker.patch("app.notification.alert.send_slack")
            send_mail = mocker.patch("app.notification.alert.send_email")

            # When
            _bg_check_eol_notification()

            # Then
            send_slack.assert_not_called()
            send_mail.assert_not_called()

        def test_it_should_not_alert_when_alert_slack_and_alert_email_are_False(
            self, testdb, mocker
        ):
            # Given
            pteam_request = {
                "alert_slack": {
                    "enable": False,
                    "webhook_url": "",
                },
                "alert_mail": {
                    "enable": False,
                    "address": "",
                },
            }
            client.put(f"/pteams/{self.pteam.pteam_id}", headers=headers(USER1), json=pteam_request)

            # Create EcosystemEoLDependency
            eol_product_id_1 = str(uuid4())
            eol_from_date1 = (
                datetime.now(timezone.utc) + timedelta(days=EOL_WARNING_THRESHOLD_DAYS)
            ).strftime("%Y-%m-%d")
            eol_product_1_request: dict[str, Any] = {
                "name": "product_1",
                "product_category": models.ProductCategoryEnum.RUNTIME,
                "description": "product 1 description",
                "is_ecosystem": True,
                "matching_name": "product_1",
                "eol_versions": [
                    {
                        "version": "20.04",
                        "release_date": "2021-01-01",
                        "eol_from": eol_from_date1,
                        "matching_version": "ubuntu-20.04",
                    }
                ],
            }

            client.put(
                f"/eols/{eol_product_id_1}",
                headers=headers_with_api_key(USER1),
                json=eol_product_1_request,
            )

            ecosystem_eol_dependency = testdb.scalars(
                select(models.EcosystemEoLDependency)
                .join(
                    models.EoLVersion,
                    models.EcosystemEoLDependency.eol_version_id
                    == models.EoLVersion.eol_version_id,
                )
                .join(
                    models.EoLProduct,
                    models.EoLProduct.eol_product_id == models.EoLVersion.eol_product_id,
                )
                .where(models.EoLProduct.eol_product_id == eol_product_id_1)
            ).one()

            ecosystem_eol_dependency.eol_notification_sent = False
            testdb.commit()

            send_slack = mocker.patch("app.notification.alert.send_slack")
            send_mail = mocker.patch("app.notification.alert.send_email")

            # When
            _bg_check_eol_notification()

            # Then
            send_slack.assert_not_called()
            send_mail.assert_not_called()
            assert ecosystem_eol_dependency.eol_notification_sent is False
