import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models, schemas
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    SERVICE1,
    SERVICE2,
    TAG1,
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

        def create_action(
            self, user: dict, vuln_id: str | UUID, action: dict
        ) -> schemas.ActionResponse:
            action_with_vuln = {**action, "vuln_id": str(vuln_id)}
            response = client.post(
                "/actions",
                headers=headers(user),
                json=action_with_vuln,
            )
            if response.status_code != 200:
                raise HTTPError(response)
            return schemas.ActionResponse(**response.json())

        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self, testdb):
            self.user1 = create_user(USER1)
            self.user2 = create_user(USER2)
            self.pteam1 = create_pteam(USER1, PTEAM1)

            # Upload the SBOM file and create dependency information
            upload_file_name = "test_trivy_cyclonedx_axios.json"
            sbom_file = Path(__file__).resolve().parent / "upload_test" / upload_file_name
            with open(sbom_file, "r") as sbom:
                sbom_json = json.load(sbom)
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
                "action_type": "elimination",
                "recommended": True,
            }
            self.action1 = self.create_action(USER1, self.vuln1.vuln_id, self.action_data)

            self.ticket1 = get_tickets_related_to_vuln_package(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.vuln1.vuln_id,
                self.package_version1.package_id,
            )[0]

    class TestCreate(Common):

        def test_create_log(self):
            now = datetime.now()
            actionlog1 = create_actionlog(
                USER1,
                self.action1.action_id,
                self.action_data["action"],
                self.action_data["action_type"],
                self.action_data["recommended"],
                self.vuln1.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                now,
            )

            assert actionlog1.logging_id != ZERO_FILLED_UUID
            assert actionlog1.action_id == self.action1.action_id
            assert str(actionlog1.vuln_id) == str(self.vuln1.vuln_id)
            assert actionlog1.action == self.action1.action
            assert actionlog1.action_type == self.action1.action_type
            assert actionlog1.recommended == self.action1.recommended
            assert actionlog1.user_id == self.user1.user_id
            assert actionlog1.pteam_id == self.pteam1.pteam_id
            assert str(actionlog1.service_id) == self.service1["service_id"]
            assert str(actionlog1.ticket_id) == self.ticket1["ticket_id"]
            assert actionlog1.email == USER1["email"]
            assert actionlog1.executed_at == now
            assert actionlog1.created_at > now

        def test_create_log_without_action_id(self):
            now = datetime.now()
            actionlog = create_actionlog(
                USER1,
                None,  # action_id = None
                self.action_data["action"],
                self.action_data["action_type"],
                self.action_data["recommended"],
                self.vuln1.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                now,
            )
            assert actionlog.logging_id != ZERO_FILLED_UUID
            assert actionlog.action_id is None
            assert actionlog.action == self.action1.action
            assert actionlog.action_type == self.action1.action_type
            assert actionlog.recommended == self.action1.recommended
            assert str(actionlog.vuln_id) == str(self.vuln1.vuln_id)
            assert actionlog.user_id == self.user1.user_id
            assert actionlog.pteam_id == self.pteam1.pteam_id
            assert str(actionlog.service_id) == self.service1["service_id"]
            assert str(actionlog.ticket_id) == self.ticket1["ticket_id"]
            assert actionlog.email == USER1["email"]
            assert actionlog.executed_at == now
            assert actionlog.created_at > now

        def test_create_log_with_wrong_action(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    uuid4(),  # wrong action_id
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
                    self.vuln1.vuln_id,
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_shoud_return_400_when_create_actionlog_with_wrong_vuln(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action1.action_id,
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
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
                    self.action1.action_id,
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
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
                    self.action1.action_id,
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
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
                    self.action1.action_id,
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
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
                    self.action1.action_id,
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
                    self.vuln1.vuln_id,
                    self.user2.user_id,  # USER2
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_when_create_log_with_action_not_belong_specified_vuln(self):
            vuln2 = create_vuln(USER1, VULN2)
            action_data = {
                "action": "Do something else",
                "action_type": "elimination",
                "recommended": True,
            }
            action2 = self.create_action(USER1, vuln2.vuln_id, action_data)
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    action2.action_id,  # action2
                    self.action_data["action"],
                    self.action_data["action_type"],
                    self.action_data["recommended"],
                    self.vuln1.vuln_id,
                    self.user1.user_id,
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
                "action_type": "elimination",
                "recommended": True,
            }
            action_data2 = {
                "action": "action2",
                "action_type": "elimination",
                "recommended": True,
            }
            action2a = self.create_action(USER1, vuln2.vuln_id, action_data1)
            action2b = self.create_action(USER1, vuln2.vuln_id, action_data2)
            ticket2 = get_tickets_related_to_vuln_package(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.vuln1.vuln_id,
                self.package_version1.package_id,
            )[0]
            now = datetime.now()
            yesterday = now - timedelta(days=1)

            actionlog1 = create_actionlog(
                USER1,
                action2a.action_id,
                action2a.action,
                action2a.action_type,
                action2a.recommended,
                vuln2.vuln_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                ticket2["ticket_id"],
                yesterday,
            )
            actionlog2 = create_actionlog(
                USER1,
                action2b.action_id,
                action2b.action,
                action2b.action_type,
                action2b.recommended,
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
            now = datetime.now()
            before = now - timedelta(days=1)

            actionlog1 = create_actionlog(
                USER1,
                self.action1.action_id,
                self.action1.action,
                self.action1.action_type,
                self.action1.recommended,
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
                sbom_json = json.load(sbom)
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
                self.action1.action_id,
                self.action1.action,
                self.action1.action_type,
                self.action1.recommended,
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

        def test_get_topic_logs(self):
            # create topic2 with 2 actions
            topic2 = create_topic_with_versioned_actions(USER1, TOPIC2, [[TAG1], [TAG1]])
            action2a = topic2.actions[0]
            action2b = topic2.actions[1]
            ticket2 = get_tickets_related_to_topic_tag(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                topic2.topic_id,
                self.tag1.tag_id,
            )[0]
            now = datetime.now()
            yesterday = now - timedelta(days=1)

            actionlog1 = create_actionlog(
                USER1,
                action2a.action_id,
                topic2.topic_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                ticket2["ticket_id"],
                yesterday,
            )
            actionlog2 = create_actionlog(
                USER1,
                action2b.action_id,
                topic2.topic_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                ticket2["ticket_id"],
                now,
            )

            response = client.get(f"/actionlogs/topics/{topic2.topic_id}", headers=headers(USER1))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by excuted_at
            assert data[0]["service_id"] == self.service1["service_id"]
            assert data[0]["ticket_id"] == ticket2["ticket_id"]
            assert data[1]["logging_id"] == str(actionlog1.logging_id)
            assert data[1]["service_id"] == self.service1["service_id"]
            assert data[1]["ticket_id"] == ticket2["ticket_id"]
