import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
    USER2,
)
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    headers,
    invite_to_pteam,
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

        # user2をadminに設定(use1以外にadminがいる状態に設定)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": True},
        )

        # ユーザーが自分を削除できるかを確認
        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # ユーザー削除後の確認
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # チームは削除されていないことを確認
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None

    def test_user_deletes_last_admin_and_pteam_is_deleted(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # user1が最後のadminであることを確認(adminではないuser2を追加)
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
        )

        # user1が自分を削除
        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # ユーザー削除後の確認
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # PTeamは削除されていることを確認
        deleted_pteam = self._get_pteam_deleted(pteam1, testdb)
        assert deleted_pteam is None

    def test_delete_user_if_user_is_not_last_admin(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # user2をadmin=Trueとして追加
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": True},
        )

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        # ユーザー削除後の確認
        deleted_user, action_logs = self._get_user_deleted(user1, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # 最後のadminではないためPTeamは削除されていないことを確認
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None

    def test_delete_user_if_user_is_not_admin(self, user_setup, testdb: Session):
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        # user2をadminでない状態でPTeamに参加させる
        client.put(
            f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
            headers=headers(USER1),
            json={"is_admin": False},
        )

        delete_response = client.delete("/users/me", headers=headers(USER2))
        assert delete_response.status_code == 204

        # adminでないuser2を削除後の確認
        deleted_user, action_logs = self._get_user_deleted(user2, testdb)
        assert deleted_user is None
        for log in action_logs:
            assert log.user_id is None

        # adminではないため、PTeamは削除されていないことを確認
        existing_pteam = self._get_pteam_not_deleted(pteam1, testdb)
        assert existing_pteam is not None
