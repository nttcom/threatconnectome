from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    SERVICE1,
    SERVICE2,
    TAG1,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
    USER3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_actionlog,
    create_pteam,
    create_tag,
    create_topic_with_versioned_actions,
    create_user,
    get_service_by_service_name,
    get_tickets_related_to_topic_tag,
    headers,
    invite_to_pteam,
    upload_pteam_tags,
)

client = TestClient(app)


class TestActionLog:

    class Common:

        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            self.tag1 = create_tag(USER1, TAG1)
            self.topic1 = create_topic_with_versioned_actions(USER1, TOPIC1, [[TAG1]])
            self.action1 = self.topic1.actions[0]
            refs0 = {TAG1: [("Pipfile.lock", "1.0.0")]}
            upload_pteam_tags(USER1, self.pteam1.pteam_id, SERVICE1, refs0, True)
            self.service1 = get_service_by_service_name(USER1, self.pteam1.pteam_id, SERVICE1)
            self.ticket1 = get_tickets_related_to_topic_tag(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.topic1.topic_id,
                self.tag1.tag_id,
            )[0]

    class TestCreate(Common):

        def test_create_log(self):
            now = datetime.now()
            actionlog1 = create_actionlog(
                USER1,
                self.action1.action_id,
                self.topic1.topic_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                now,
            )

            assert actionlog1.logging_id != ZERO_FILLED_UUID
            assert actionlog1.action_id == self.action1.action_id
            assert actionlog1.topic_id == self.topic1.topic_id
            assert actionlog1.action == self.topic1.actions[0].action
            assert actionlog1.action_type == self.topic1.actions[0].action_type
            assert actionlog1.recommended == self.topic1.actions[0].recommended
            assert actionlog1.user_id == self.user1.user_id
            assert actionlog1.pteam_id == self.pteam1.pteam_id
            assert str(actionlog1.service_id) == self.service1["service_id"]
            assert str(actionlog1.ticket_id) == self.ticket1["ticket_id"]
            assert actionlog1.email == USER1["email"]
            assert actionlog1.executed_at == now
            assert actionlog1.created_at > now

        def test_create_log__with_wrong_action(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    uuid4(),  # wrong action_id
                    self.topic1.topic_id,
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_shoud_return_400_when_create_actionlog_with_wrong_topic(self):
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action1.action_id,
                    uuid4(),  # wrong topic_id
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
                    self.topic1.topic_id,
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
                    self.topic1.topic_id,
                    self.user1.user_id,
                    uuid4(),  # wrong pteam_id
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_create_log__with_called_by_not_pteam_member(self):
            create_user(USER2)
            with pytest.raises(HTTPError, match="403: Forbidden"):
                create_actionlog(
                    USER2,  # call by USER2
                    self.action1.action_id,
                    self.topic1.topic_id,
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_create_log_with_not_pteam_member_as_recipient(self):
            user2 = create_user(USER2)
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    self.action1.action_id,
                    self.topic1.topic_id,
                    user2.user_id,  # USER2
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

        def test_it_should_return_400_when_create_log_with_action_not_belong_specified_topic(self):
            topic2 = create_topic_with_versioned_actions(USER1, TOPIC2, [[TAG1]])
            action2 = topic2.actions[0]
            with pytest.raises(HTTPError, match="400: Bad Request"):
                create_actionlog(
                    USER1,
                    action2.action_id,  # action2
                    self.topic1.topic_id,
                    self.user1.user_id,
                    self.pteam1.pteam_id,
                    self.service1["service_id"],
                    self.ticket1["ticket_id"],
                    None,
                )

    class TestGet(Common):

        def test_get_logs(self):
            # create topic2 with 2 actions
            topic2 = create_topic_with_versioned_actions(USER1, TOPIC2, [[TAG1], [TAG1]])
            action2a = topic2.actions[0]
            action2b = topic2.actions[1]
            ticket2 = get_tickets_related_to_topic_tag(
                USER1,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.topic1.topic_id,
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

        def test_get_logs__members_only(self):
            actionlog1 = create_actionlog(
                USER1,
                self.action1.action_id,
                self.topic1.topic_id,
                self.user1.user_id,
                self.pteam1.pteam_id,
                self.service1["service_id"],
                self.ticket1["ticket_id"],
                None,
            )

            user2 = create_user(USER2)
            pteam2 = create_pteam(USER2, PTEAM2)
            refs0 = {TAG1: [("Pipfile.lock", "1.0.0")]}
            upload_pteam_tags(USER2, pteam2.pteam_id, SERVICE2, refs0, True)
            service2 = get_service_by_service_name(USER2, pteam2.pteam_id, SERVICE2)
            ticket2 = get_tickets_related_to_topic_tag(
                USER2,
                pteam2.pteam_id,
                service2["service_id"],
                self.topic1.topic_id,
                self.tag1.tag_id,
            )[0]
            actionlog2 = create_actionlog(
                USER2,
                self.action1.action_id,
                self.topic1.topic_id,
                user2.user_id,
                pteam2.pteam_id,
                service2["service_id"],
                ticket2["ticket_id"],
                None,
            )

            response = client.get("/actionlogs", headers=headers(USER1))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog1.logging_id)  # pteam1 only

            response = client.get("/actionlogs", headers=headers(USER2))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog2.logging_id)  # pteam2 only

            create_user(USER3)

            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0  # nothing for pteamless

            invitation = invite_to_pteam(USER1, self.pteam1.pteam_id)
            accept_pteam_invitation(USER3, invitation.invitation_id)

            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["logging_id"] == str(actionlog1.logging_id)  # pteam1 only

            invitation = invite_to_pteam(USER2, pteam2.pteam_id)
            accept_pteam_invitation(USER3, invitation.invitation_id)

            response = client.get("/actionlogs", headers=headers(USER3))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2  # both of pteam1 & pteam2
            assert data[0]["logging_id"] == str(actionlog2.logging_id)  # sorted by created_st
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
