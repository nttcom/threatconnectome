import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    get_service_by_service_name,
    get_tickets_related_to_topic_tag,
    headers,
    invite_to_pteam,
    set_ticket_status,
    upload_pteam_tags,
)

client = TestClient(app)


class TestDeleteUser:
    @pytest.fixture(scope="function")
    def user_setup(self, testdb: Session):
        user1 = create_user(USER1)
        user2 = create_user(USER2)

        pteam_data = PTEAM1
        pteam1 = create_pteam(USER1, pteam_data)

        invite = invite_to_pteam(USER1, pteam1.pteam_id)
        accept_pteam_invitation(USER2, invite.invitation_id)

        return {"user1": user1, "user2": user2, "pteam1": pteam1}

    def _get_user_deleted(self, user, testdb: Session):
        deleted_user = testdb.execute(
            select(models.Account).where(models.Account.user_id == str(user.user_id))
        ).scalar_one_or_none()

        action_logs = (
            testdb.execute(
                select(models.ActionLog).where(models.ActionLog.user_id == str(user.user_id))
            )
            .scalars()
            .all()
        )

        return deleted_user, action_logs

    def _get_pteam_not_deleted(self, pteam, testdb: Session):
        existing_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam.pteam_id))
        ).scalar_one_or_none()

        return existing_pteam

    def _get_pteam_deleted(self, pteam, testdb: Session):
        deleted_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam.pteam_id))
        ).scalar_one_or_none()

        return deleted_pteam

    def test_user_can_delete_themselves(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # Set user2 as admin (set it so that there is an admin other than user1)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": True},
        )

        # Check if the user can delete themselves.
        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

    def test_user_deletes_last_admin_and_pteam_is_deleted(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # set user2, who is not an admin(user1 is the last admin)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
        )

        # Check if the user can delete themselves.
        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # Confirm that the PTeam has been deleted.
        deleted_pteam = self._get_pteam_deleted(pteam1, testdb)
        assert deleted_pteam is None

    def test_delete_user_if_user_is_not_last_admin(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # Set user2 as admin (set it so that there is an admin other than user1)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": True},
        )

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # Confirm that the PTeam has not been deleted because it is not the last admin.
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None

    def test_delete_user_if_user_is_not_admin(self, user_setup, testdb: Session):
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # set user2, who is not an admin(user1 is the last admin)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": False},
        )

        delete_response = client.delete("/users/me", headers=headers(USER2))
        assert delete_response.status_code == 204

        # Confirmation after deleting user2, who is not an admin.
        deleted_user, action_logs = self._get_user_deleted(user2, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # Confirm that the PTeam has not been deleted because user2 is not an admin.
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None


class TestDeleteUserSideEffects:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # Setup user, pteam, service, and topic
        self.user1 = create_user(USER1)
        self.user2 = create_user(USER2)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        self.pteam2 = create_pteam(USER2, PTEAM2)
        self.tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")

        action1 = {
            "action": "test action1",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.tag1.tag_name],
                "vulnerable_versions": {self.tag1.tag_name: ["< 9999.99.99"]},
            },
        }

        self.topic1 = create_topic(
            USER1, {**TOPIC1, "tags": [self.tag1.tag_name], "actions": [action1]}
        )
        self.topic2 = create_topic(
            USER2, {**TOPIC2, "tags": [self.tag1.tag_name], "actions": [action1]}
        )

        refs0 = {self.tag1.tag_name: [("test target", "1.2.3"), ("noise target", "1.2.3")]}
        service_name1 = "test service1"
        service_name2 = "test service2"

        upload_pteam_tags(USER1, self.pteam1.pteam_id, service_name1, refs0)
        upload_pteam_tags(USER2, self.pteam2.pteam_id, service_name2, refs0)

        self.service1 = get_service_by_service_name(USER1, self.pteam1.pteam_id, service_name1)
        self.service2 = get_service_by_service_name(USER2, self.pteam2.pteam_id, service_name2)

        invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
        invitation2 = invite_to_pteam(USER2, self.pteam2.pteam_id)

        accept_pteam_invitation(USER2, invitation1.invitation_id)
        accept_pteam_invitation(USER1, invitation2.invitation_id)

        # Setup ticket status with actionlog
        tickets1 = get_tickets_related_to_topic_tag(
            USER1,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.topic1.topic_id,
            self.tag1.tag_id,
        )
        self.ticket1 = tickets1[0]

        tickets2 = get_tickets_related_to_topic_tag(
            USER2,
            self.pteam2.pteam_id,
            self.service2["service_id"],
            self.topic2.topic_id,
            self.tag1.tag_id,
        )
        self.ticket2 = tickets2[0]

        # Action logs for tickets
        log_request1 = {
            "action_id": str(self.topic1.actions[0].action_id),
            "topic_id": str(self.topic1.topic_id),
            "user_id": str(self.user1.user_id),
            "pteam_id": str(self.pteam1.pteam_id),
            "service_id": self.service1["service_id"],
            "ticket_id": self.ticket1["ticket_id"],
            "executed_at": None,
        }

        log_response1 = client.post("/actionlogs", headers=headers(USER1), json=log_request1)
        self.actionlog1 = log_response1.json()

        log_request2 = {
            "action_id": str(self.topic2.actions[0].action_id),
            "topic_id": str(self.topic2.topic_id),
            "user_id": str(self.user2.user_id),
            "pteam_id": str(self.pteam2.pteam_id),
            "service_id": self.service2["service_id"],
            "ticket_id": self.ticket2["ticket_id"],
            "executed_at": None,
        }

        log_response2 = client.post("/actionlogs", headers=headers(USER2), json=log_request2)
        self.actionlog2 = log_response2.json()

        # Set ticket status
        status_request1 = {
            "topic_status": models.TopicStatusType.completed.value,
            "assignees": [str(self.user1.user_id)],
            "logging_ids": [self.actionlog1["logging_id"]],
        }
        set_ticket_status(
            USER1,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.ticket1["ticket_id"],
            status_request1,
        )

        status_request2 = {
            "topic_status": models.TopicStatusType.completed.value,
            "assignees": [str(self.user2.user_id)],
            "logging_ids": [self.actionlog2["logging_id"]],
        }
        set_ticket_status(
            USER2,
            self.pteam2.pteam_id,
            self.service2["service_id"],
            self.ticket2["ticket_id"],
            status_request2,
        )

    @staticmethod
    def delete_user_me(user) -> None:
        response = client.delete("/users/me", headers=headers(user))
        if response.status_code != 204:
            raise HTTPError(response)

    @staticmethod
    def get_users_me(user) -> schemas.UserResponse:
        response = client.get("/users/me", headers=headers(user))
        if response.status_code != 200:
            raise HTTPError(response)
        return schemas.UserResponse(**response.json())

    @staticmethod
    def update_pteam_member(
        operate_user, user_id, pteam_id, is_admin: bool
    ) -> schemas.PTeamMemberResponse:
        request = {"is_admin": is_admin}
        response = client.put(
            f"/pteams/{pteam_id}/members/{user_id}", headers=headers(operate_user), json=request
        )
        if response.status_code != 200:
            raise HTTPError(response)
        return schemas.PTeamMemberResponse(**response.json())

    def test_cannot_get_user_after_deleted(self, testdb):
        self.delete_user_me(USER1)
        with pytest.raises(HTTPError, match="404: Not Found: No such user"):
            self.get_users_me(USER1)

    def test_user_id_of_deleted_users_actionlog_should_be_none(self, testdb):
        # Make user2 admin to prevent deletion of pteam1
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        # Check user_id of deleted user's actionlog
        db_actionlog = testdb.scalars(
            select(models.ActionLog).where(
                models.ActionLog.logging_id == str(self.actionlog1["logging_id"])
            )
        ).one()
        assert db_actionlog.user_id is None

    def test_user_id_of_not_deleted_users_actionlog_should_be_kept(self, testdb):
        self.delete_user_me(USER1)

        # Check user_id of non-deleted user's actionlog
        db_actionlog = testdb.scalars(
            select(models.ActionLog).where(
                models.ActionLog.logging_id == str(self.actionlog2["logging_id"])
            )
        ).one()
        assert db_actionlog.user_id == str(self.user2.user_id)

    def test_created_by_of_deleted_users_action_should_be_none(self, testdb):
        action1 = self.topic1.actions[0]
        # Make user2 admin to prevent deletion of pteam1
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        # Check created_by of deleted user's action
        db_action = testdb.scalars(
            select(models.TopicAction).where(models.TopicAction.action_id == str(action1.action_id))
        ).one()
        assert db_action.created_by is None

    def test_created_by_of_not_deleted_users_action_should_be_kept(self, testdb):
        action2 = self.topic2.actions[0]
        self.delete_user_me(USER1)

        # Check created_by of non-deleted user's action
        db_action = testdb.scalars(
            select(models.TopicAction).where(models.TopicAction.action_id == str(action2.action_id))
        ).one()
        assert db_action.created_by == str(self.user2.user_id)

    def test_created_by_of_deleted_users_topic_should_be_none(self, testdb):
        # Make user2 admin to prevent deletion of pteam1
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        # Check created_by of deleted user's topic
        db_topic = testdb.scalars(
            select(models.Topic).where(models.Topic.topic_id == str(self.topic1.topic_id))
        ).one()
        assert db_topic.created_by is None

    def test_created_by_of_not_deleted_users_topic_should_be_kept(self, testdb):
        self.delete_user_me(USER1)

        # Check created_by of non-deleted user's topic
        db_topic = testdb.scalars(
            select(models.Topic).where(models.Topic.topic_id == str(self.topic2.topic_id))
        ).one()
        assert db_topic.created_by == str(self.topic2.created_by)

    def test_pteam_invitations_from_deleted_users_should_be_none(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        db_invitation = testdb.scalars(
            select(models.PTeamInvitation).where(
                models.PTeamInvitation.user_id == str(self.user1.user_id)
            )
        ).one_or_none()
        assert db_invitation is None

    def test_pteam_invitations_from_not_deleted_users_should_be_kept(self, testdb):
        invite_to_pteam(USER2, self.pteam2.pteam_id)
        self.delete_user_me(USER1)

        db_invitation = testdb.scalars(
            select(models.PTeamInvitation).where(
                models.PTeamInvitation.user_id == str(self.user2.user_id)
            )
        ).one_or_none()
        assert db_invitation is not None

    def test_ticketstatus_of_deleted_users_should_be_none(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        # Check user_id of deleted user's ticketstatus
        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.user_id == str(self.user1.user_id),
            )
        ).one_or_none()
        assert db_ticketstatus is None

    def test_ticketstatus_of_not_deleted_users_should_be_none(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1)

        # Check user_id of deleted user's ticketstatus
        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.user_id == str(self.user2.user_id),
            )
        ).one_or_none()
        assert db_ticketstatus is not None

    @pytest.mark.skip(
        reason="process of excluding deleted users' user_id from TicketStatus "
        "assignees is not implemented."
    )
    def test_ticketstatus_assignees_should_not_include_deleted_user(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)

        status_request = {
            "topic_status": models.TopicStatusType.completed.value,
            "assignees": [str(self.user1.user_id)],
            "logging_ids": [self.actionlog1["logging_id"]],
        }
        set_ticket_status(
            USER2,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.ticket1["ticket_id"],
            status_request,
        )

        self.delete_user_me(USER1)

        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.ticket_id == self.ticket1["ticket_id"]
            )
        ).one()

        assert str(self.user1.user_id) not in db_ticketstatus.assignees

    def test_ticketstatus_assignees_should_include_not_deleted_user(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)

        status_request = {
            "topic_status": models.TopicStatusType.completed.value,
            "assignees": [str(self.user1.user_id)],
            "logging_ids": [self.actionlog1["logging_id"]],
        }
        set_ticket_status(
            USER2,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.ticket1["ticket_id"],
            status_request,
        )

        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.ticket_id == self.ticket1["ticket_id"]
            )
        ).one()

        assert str(self.user1.user_id) in db_ticketstatus.assignees

    def test_pteamaccountrole_should_be_deleted_when_user_is_deleted(self, testdb):
        self.delete_user_me(USER1)

        db_pteam_role = testdb.scalars(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.user_id == str(self.user1.user_id)
            )
        ).one_or_none()

        assert db_pteam_role is None

    def test_pteamaccountrole_should_not_be_deleted_when_user_is_not_deleted(self, testdb):
        self.delete_user_me(USER1)

        db_pteam_role = testdb.scalars(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.user_id == str(self.user2.user_id)
            )
        ).one_or_none()

        assert db_pteam_role is not None
