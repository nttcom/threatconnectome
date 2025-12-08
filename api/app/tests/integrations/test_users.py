import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    VULN1,
    VULN2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    create_vuln,
    get_service_by_service_name,
    get_tickets_related_to_vuln_package,
    headers,
    invite_to_pteam,
    judge_whether_firebase_or_supabase,
    set_ticket_status,
    upload_pteam_packages,
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

    def test_user_can_delete_themselves(self, user_setup, testdb: Session, mocker):
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
        module = judge_whether_firebase_or_supabase()
        delete_user = mocker.patch.object(
            module,
            "delete_user",
        )

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        delete_user.assert_called_once()

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

    def test_user_deletes_last_admin_and_pteam_is_deleted(
        self, user_setup, testdb: Session, mocker
    ):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # set user2, who is not an admin(user1 is the last admin)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
        )

        # Check if the user can delete themselves.
        module = judge_whether_firebase_or_supabase()
        delete_user = mocker.patch.object(
            module,
            "delete_user",
        )

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        delete_user.assert_called_once()

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # Confirm that the PTeam has been deleted.
        deleted_pteam = self._get_pteam_deleted(pteam1, testdb)
        assert deleted_pteam is None

    def test_delete_user_if_user_is_not_last_admin(self, user_setup, testdb: Session, mocker):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # Set user2 as admin (set it so that there is an admin other than user1)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": True},
        )

        module = judge_whether_firebase_or_supabase()
        delete_user = mocker.patch.object(
            module,
            "delete_user",
        )

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        delete_user.assert_called_once()

        # Confirmation after user deletion.
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # Confirm that the PTeam has not been deleted because it is not the last admin.
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None

    def test_delete_user_if_user_is_not_admin(self, user_setup, testdb: Session, mocker):
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # set user2, who is not an admin(user1 is the last admin)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": False},
        )

        module = judge_whether_firebase_or_supabase()
        delete_user = mocker.patch.object(
            module,
            "delete_user",
        )

        delete_response = client.delete("/users/me", headers=headers(USER2))
        assert delete_response.status_code == 204

        delete_user.assert_called_once()

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
    def common_setup(self, testdb):
        # Setup user, pteam, service, and vuln
        self.user1 = create_user(USER1)
        self.user2 = create_user(USER2)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        self.pteam2 = create_pteam(USER2, PTEAM2)

        self.vuln1 = create_vuln(USER1, VULN1)
        self.vuln2 = create_vuln(USER2, VULN2)

        refs1 = [
            {
                "package_name": "axios",
                "ecosystem": "npm",
                "package_manager": "npm",
                "references": [{"target": "target1", "version": "1.0"}],
            }
        ]

        refs2 = [
            {
                "package_name": "asynckit",
                "ecosystem": "npm",
                "package_manager": "npm",
                "references": [{"target": "target2", "version": "1.0"}],
            }
        ]

        service_name1 = "test service1"
        service_name2 = "test service2"

        upload_pteam_packages(USER1, self.pteam1.pteam_id, service_name1, refs1)
        upload_pteam_packages(USER2, self.pteam2.pteam_id, service_name2, refs2)

        self.service1 = get_service_by_service_name(USER1, self.pteam1.pteam_id, service_name1)
        self.service2 = get_service_by_service_name(USER2, self.pteam2.pteam_id, service_name2)

        invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
        invitation2 = invite_to_pteam(USER2, self.pteam2.pteam_id)

        accept_pteam_invitation(USER2, invitation1.invitation_id)
        accept_pteam_invitation(USER1, invitation2.invitation_id)

        package1 = persistence.get_package_by_name_and_ecosystem_and_source_name(
            testdb, refs1[0]["package_name"], refs1[0]["ecosystem"], None
        )

        # Setup ticket status with actionlog
        tickets1 = get_tickets_related_to_vuln_package(
            USER1,
            self.pteam1.pteam_id,
            self.service1["service_id"],
            self.vuln1.vuln_id,
            package1.package_id,
        )
        self.ticket1 = tickets1[0]

        package2 = persistence.get_package_by_name_and_ecosystem_and_source_name(
            testdb, refs2[0]["package_name"], refs2[0]["ecosystem"], None
        )

        tickets2 = get_tickets_related_to_vuln_package(
            USER2,
            self.pteam2.pteam_id,
            self.service2["service_id"],
            self.vuln2.vuln_id,
            package2.package_id,
        )
        self.ticket2 = tickets2[0]

        # Action logs for tickets
        log_request1 = {
            "vuln_id": str(self.vuln1.vuln_id),
            "user_id": str(self.user1.user_id),
            "pteam_id": str(self.pteam1.pteam_id),
            "service_id": self.service1["service_id"],
            "ticket_id": self.ticket1["ticket_id"],
            "action": "test_action1",
            "executed_at": None,
        }

        log_response1 = client.post("/actionlogs", headers=headers(USER1), json=log_request1)
        self.actionlog1 = log_response1.json()

        log_request2 = {
            "vuln_id": str(self.vuln1.vuln_id),
            "user_id": str(self.user2.user_id),
            "pteam_id": str(self.pteam2.pteam_id),
            "service_id": self.service2["service_id"],
            "ticket_id": self.ticket2["ticket_id"],
            "action": "test_action2",
            "executed_at": None,
        }

        log_response2 = client.post("/actionlogs", headers=headers(USER2), json=log_request2)
        self.actionlog2 = log_response2.json()

        # Set ticket status
        status_request1 = {
            "ticket_status": {
                "ticket_handling_status": models.TicketHandlingStatusType.completed.value,
                "assignees": [str(self.user1.user_id)],
                "logging_ids": [self.actionlog1["logging_id"]],
            }
        }
        set_ticket_status(
            USER1,
            self.pteam1.pteam_id,
            self.ticket1["ticket_id"],
            status_request1,
        )

        status_request2 = {
            "ticket_status": {
                "ticket_handling_status": models.TicketHandlingStatusType.completed.value,
                "assignees": [str(self.user2.user_id)],
                "logging_ids": [self.actionlog2["logging_id"]],
            }
        }
        set_ticket_status(
            USER2,
            self.pteam2.pteam_id,
            self.ticket2["ticket_id"],
            status_request2,
        )

    @staticmethod
    def delete_user_me(user, mocker) -> None:
        module = judge_whether_firebase_or_supabase()
        delete_user = mocker.patch.object(
            module,
            "delete_user",
        )
        response = client.delete("/users/me", headers=headers(user))
        delete_user.assert_called_once()
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
    ) -> schemas.PTeamMemberUpdateResponse:
        request = {"is_admin": is_admin}
        response = client.put(
            f"/pteams/{pteam_id}/members/{user_id}", headers=headers(operate_user), json=request
        )
        if response.status_code != 200:
            raise HTTPError(response)
        return schemas.PTeamMemberUpdateResponse(**response.json())

    def test_cannot_get_user_after_deleted(self, mocker):
        self.delete_user_me(USER1, mocker)
        with pytest.raises(HTTPError, match="404: Not Found: No such user"):
            self.get_users_me(USER1)

    def test_user_id_of_deleted_users_actionlog_should_be_none(self, testdb, mocker):
        # Make user2 admin to prevent deletion of pteam1
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1, mocker)

        # Check user_id of deleted user's actionlog
        db_actionlog = testdb.scalars(
            select(models.ActionLog).where(
                models.ActionLog.logging_id == str(self.actionlog1["logging_id"])
            )
        ).one()
        assert db_actionlog.user_id is None
        assert db_actionlog.email == ""

    def test_user_id_of_not_deleted_users_actionlog_should_be_kept(self, testdb, mocker):
        self.delete_user_me(USER1, mocker)

        # Check user_id of non-deleted user's actionlog
        db_actionlog = testdb.scalars(
            select(models.ActionLog).where(
                models.ActionLog.logging_id == str(self.actionlog2["logging_id"])
            )
        ).one()
        assert db_actionlog.user_id == str(self.user2.user_id)

    def test_created_by_of_deleted_users_vuln_should_be_none(self, testdb, mocker):
        # Make user2 admin to prevent deletion of pteam1
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1, mocker)

        # Check created_by of deleted user's vuln
        db_vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln1.vuln_id))
        ).one()
        assert db_vuln.created_by is None

    def test_created_by_of_not_deleted_users_vuln_should_be_kept(self, testdb, mocker):
        self.delete_user_me(USER1, mocker)

        # Check created_by of non-deleted user's vuln
        db_vuln = testdb.scalars(
            select(models.Vuln).where(models.Vuln.vuln_id == str(self.vuln2.vuln_id))
        ).one()
        assert db_vuln.created_by == str(self.vuln2.created_by)

    def test_pteam_invitations_from_deleted_users_should_be_none(self, testdb, mocker):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1, mocker)

        db_invitation = testdb.scalars(
            select(models.PTeamInvitation).where(
                models.PTeamInvitation.user_id == str(self.user1.user_id)
            )
        ).one_or_none()
        assert db_invitation is None

    def test_pteam_invitations_from_not_deleted_users_should_be_kept(self, testdb, mocker):
        invite_to_pteam(USER2, self.pteam2.pteam_id)
        self.delete_user_me(USER1, mocker)

        db_invitation = testdb.scalars(
            select(models.PTeamInvitation).where(
                models.PTeamInvitation.user_id == str(self.user2.user_id)
            )
        ).one_or_none()
        assert db_invitation is not None

    def test_ticketstatus_of_deleted_users_should_be_none(self, testdb, mocker):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1, mocker)

        # Check user_id of deleted user's ticketstatus
        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.user_id == str(self.user1.user_id),
            )
        ).one_or_none()
        assert db_ticketstatus is None

    def test_ticketstatus_of_not_deleted_users_should_be_none(self, testdb, mocker):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)
        self.delete_user_me(USER1, mocker)

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
    def test_ticketstatus_assignees_should_not_include_deleted_user(self, testdb, mocker):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)

        status_request = {
            "ticket_status": {
                "ticket_handling_status": models.TicketHandlingStatusType.completed.value,
                "assignees": [str(self.user1.user_id)],
                "logging_ids": [self.actionlog1["logging_id"]],
            }
        }
        set_ticket_status(
            USER2,
            self.pteam1.pteam_id,
            self.ticket1["ticket_id"],
            status_request,
        )

        self.delete_user_me(USER1, mocker)

        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.ticket_id == self.ticket1["ticket_id"]
            )
        ).one()

        assert str(self.user1.user_id) not in db_ticketstatus.assignees

    def test_ticketstatus_assignees_should_include_not_deleted_user(self, testdb):
        self.update_pteam_member(USER1, self.user2.user_id, self.pteam1.pteam_id, True)

        status_request = {
            "ticket_status": {
                "ticket_handling_status": models.TicketHandlingStatusType.completed.value,
                "assignees": [str(self.user1.user_id)],
                "logging_ids": [self.actionlog1["logging_id"]],
            }
        }
        set_ticket_status(
            USER2,
            self.pteam1.pteam_id,
            self.ticket1["ticket_id"],
            status_request,
        )

        db_ticketstatus = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.ticket_id == self.ticket1["ticket_id"]
            )
        ).one()

        assert str(self.user1.user_id) in db_ticketstatus.assignees

    def test_pteamaccountrole_should_be_deleted_when_user_is_deleted(self, testdb, mocker):
        self.delete_user_me(USER1, mocker)

        db_pteam_role = testdb.scalars(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.user_id == str(self.user1.user_id)
            )
        ).one_or_none()

        assert db_pteam_role is None

    def test_pteamaccountrole_should_not_be_deleted_when_user_is_not_deleted(self, testdb, mocker):
        self.delete_user_me(USER1, mocker)

        db_pteam_role = testdb.scalars(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.user_id == str(self.user2.user_id)
            )
        ).one_or_none()

        assert db_pteam_role is not None
