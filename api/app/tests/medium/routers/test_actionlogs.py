from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    SERVICE1,
    SERVICE2,
    USER1,
    USER2,
    USER3,
    VULN1,
    VULN2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_actionlog,
    create_pteam,
    create_user,
    create_vuln,
    get_tickets_related_to_vuln_package,
    headers,
    invite_to_pteam,
)

client = TestClient(app)


class TestActionLog:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            self.user1 = create_user(USER1)
            self.user2 = create_user(USER2)
            self.pteam1 = create_pteam(USER1, PTEAM1)

            # Upload the SBOM file and create dependency information
            upload_file_name = "test_trivy_cyclonedx_axios.json"
            sbom_file = (
                Path(__file__).resolve().parent.parent.parent
                / "common"
                / "upload_test"
                / upload_file_name
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
                "pteam_id": self.pteam1.pteam_id,
            }

            # Get dependency information (PackageVersion) from the database
            package_version = testdb.scalars(select(models.PackageVersion)).one()
            self.package_version1 = package_version

            # Create vulnerability and action
            self.vuln1 = create_vuln(USER1, VULN1)
            self.action_data = {
                "action": "Do something",
            }

            self.ticket1 = get_tickets_related_to_vuln_package(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.vuln1.vuln_id,
                self.package_version1.package_id,
            )[0]

    class TestCreate(Common):
        def test_create_log(self):
            now = datetime.now(timezone.utc)
            actionlog1 = create_actionlog(
                USER1,
                self.action_data["action"],
                self.vuln1.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                now,
            )

            assert actionlog1.logging_id != ZERO_FILLED_UUID
            assert str(actionlog1.vuln_id) == str(self.vuln1.vuln_id)
            assert actionlog1.action == self.action_data["action"]
            assert actionlog1.user_id == self.user1.user_id
            assert actionlog1.pteam_id == self.pteam1.pteam_id
            assert str(actionlog1.service_id) == self.service1["service_id"]
            assert str(actionlog1.ticket_id) == self.ticket1["ticket_id"]
            assert actionlog1.email == USER1["email"]
            assert actionlog1.executed_at == now
            assert actionlog1.created_at > now

        def test_it_shoud_return_400_when_create_actionlog_with_wrong_vuln(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action_data["action"],
                    uuid4(),  # wrong vuln_id
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_when_create_log_with_wrong_user(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action_data["action"],
                    self.vuln1.vuln_id,
                    uuid4(),  # wrong user_id
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_when_create_log_with_wrong_pteam(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action_data["action"],
                    self.vuln1.vuln_id,
                    self.user1.user_id,
                    uuid4(),  # wrong pteam_id
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_create_log_with_called_by_not_pteam_member(self):
            with pytest.raises(HTTPError, match="403: Forbidden"):
                create_actionlog(
                    USER2,  # call by USER2
                    self.action_data["action"],
                    self.vuln1.vuln_id,
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_create_log_with_not_pteam_member_as_recipient(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action_data["action"],
                    self.vuln1.vuln_id,
                    self.user2.user_id,  # USER2
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

    class TestGet(Common):
        def test_get_logs(self):
            # create topic2 with 2 actions
            vuln2 = create_vuln(USER1, VULN2)
            action_data1 = {
                "action": "action1",
            }
            action_data2 = {
                "action": "action2",
            }
            ticket2 = get_tickets_related_to_vuln_package(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.vuln1.vuln_id,
                self.package_version1.package_id,
            )[0]
            now = datetime.now(timezone.utc)
            yesterday = now - timedelta(days=1)

            actionlog1 = create_actionlog(
                USER1,
                action_data1["action"],
                vuln2.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                ticket2["ticket_id"],
                yesterday,
            )
            actionlog2 = create_actionlog(
                USER1,
                action_data2["action"],
                vuln2.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                ticket2["ticket_id"],
                now,
            )

            response = client.get("/actionlogs", headers=headers(USER1))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
            assert data[0]["service_id"] == self.service1["service_id"]
            assert data[0]["ticket_id"] == ticket2["ticket_id"]
            assert data[1]["logging_id"] == str(actionlog1.logging_id)
            assert data[1]["service_id"] == self.service1["service_id"]
            assert data[1]["ticket_id"] == ticket2["ticket_id"]

        def test_get_logs_members_only(self, testdb):
            now = datetime.now(timezone.utc)
            before = now - timedelta(days=1)

            actionlog1 = create_actionlog(
                USER1,
                self.action_data["action"],
                self.vuln1.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                before,  # executed_at
            )

            pteam2 = create_pteam(USER2, PTEAM2)
            upload_file_name = "test_syft_cyclonedx.json"
            sbom_file = Path(__file__).resolve().parent / "upload_test" / upload_file_name
            with open(sbom_file, "r") as sbom:
                sbom_json = sbom.read()
            bg_create_tags_from_sbom_json(sbom_json, pteam2.pteam_id, SERVICE2, upload_file_name)

            service_id2 = testdb.scalars(
                select(models.Service.service_id).where(
                    models.Service.pteam_id == str(pteam2.pteam_id),
                    models.Service.service_name == SERVICE2,
                )
            ).one()

            service2 = {
                "service_id": str(service_id2),
                "service_name": SERVICE2,
                "pteam_id": pteam2.pteam_id,
            }

            ticket2 = get_tickets_related_to_vuln_package(
                USER2,
                pteam2.pteam_id,
                service2["service_id"],
                self.vuln1.vuln_id,
                self.package_version1.package_id,
            )[0]

            actionlog2 = create_actionlog(
                USER2,
                self.action_data["action"],
                self.vuln1.vuln_id,
                self.user2.user_id,
                pteam2.pteam_id,
                service2["service_id"],
                ticket2["ticket_id"],
                now,
            )

            response = client.get("/actionlogs", headers=headers(USER1))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog1.logging_id)

            response = client.get("/actionlogs", headers=headers(USER2))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog2.logging_id)

            create_user(USER3)
            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

            invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
            accept_pteam_invitation(USER3, invitation1.invitation_id)

            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog1.logging_id)

            invitation2 = invite_to_pteam(USER2, pteam2.pteam_id)
            accept_pteam_invitation(USER3, invitation2.invitation_id)

            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["logging_id"] == str(actionlog2.logging_id)
            assert data[1]["logging_id"] == str(actionlog1.logging_id)


class TestGetVulnLogs:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self, testdb):
        self.user1 = create_user(USER1)
        self.user2 = create_user(USER2)
        self.pteam1 = create_pteam(USER1, PTEAM1)

        # Upload the SBOM file and create dependency information
        upload_file_name = "test_trivy_cyclonedx_axios.json"
        sbom_file = (
            Path(__file__).resolve().parent.parent.parent
            / "common"
            / "upload_test"
            / upload_file_name
        )
        with open(sbom_file, "r") as sbom:
            sbom_json = sbom.read()
        bg_create_tags_from_sbom_json(sbom_json, self.pteam1.pteam_id, SERVICE1, upload_file_name)

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
            "pteam_id": self.pteam1.pteam_id,
        }

        # Get dependency information (PackageVersion) from the database
        package_version = testdb.scalars(select(models.PackageVersion)).one()
        self.package_version1 = package_version

        # Create vulnerability and action
        self.vuln1 = create_vuln(USER1, VULN1)
        self.action_data = {
            "action": "Do something",
        }

        self.ticket1 = get_tickets_related_to_vuln_package(
            USER1,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.vuln1.vuln_id,
            self.package_version1.package_id,
        )[0]

    def test_get_vuln_logs(self):
        action_data1 = {
            "action": "action1",
        }
        action_data2 = {
            "action": "action2",
        }

        ticket = self.ticket1

        # create two action logs
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        actionlog1 = create_actionlog(
            USER1,
            action_data1["action"],
            self.vuln1.vuln_id,
            self.user1.user_id,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            ticket["ticket_id"],
            yesterday,
        )
        actionlog2 = create_actionlog(
            USER1,
            action_data2["action"],
            self.vuln1.vuln_id,
            self.user1.user_id,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            ticket["ticket_id"],
            now,
        )

        response = client.get(f"/actionlogs/vulns/{self.vuln1.vuln_id}", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["logging_id"] == str(actionlog2.logging_id)
        assert data[0]["service_id"] == self.service1["service_id"]
        assert data[0]["ticket_id"] == ticket["ticket_id"]
        assert data[1]["logging_id"] == str(actionlog1.logging_id)
        assert data[1]["service_id"] == self.service1["service_id"]
        assert data[1]["ticket_id"] == ticket["ticket_id"]

    def test_get_vuln_logs_excludes_other_vuln(self):
        vuln2 = create_vuln(USER1, VULN2)

        action_data1 = {
            "action": "action1",
        }

        create_actionlog(
            USER1,
            action_data1["action"],
            self.vuln1.vuln_id,
            self.user1.user_id,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.ticket1["ticket_id"],
            datetime.now(timezone.utc),
        )

        other_action_data = {
            "action": "unrelated_action",
        }

        other_actionlog = create_actionlog(
            USER1,
            other_action_data["action"],
            vuln2.vuln_id,
            self.user1.user_id,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.ticket1["ticket_id"],
            datetime.now(timezone.utc),
        )

        response = client.get(f"/actionlogs/vulns/{self.vuln1.vuln_id}", headers=headers(USER1))
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["vuln_id"] == str(self.vuln1.vuln_id)
        assert data[0]["logging_id"] != str(other_actionlog.logging_id)
