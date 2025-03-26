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
    USER3,
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

    def test_delete_user_success(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        pteam1 = user_setup["pteam1"]

        delete_response = client.delete("/users/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        deleted_user = testdb.execute(
            select(models.Account).where(models.Account.user_id == str(user1.user_id))
        ).scalar_one_or_none()
        assert deleted_user is None

        action_logs = (
            testdb.execute(
                select(models.ActionLog).where(models.ActionLog.user_id == str(user1.user_id))
            )
            .scalars()
            .all()
        )
        for log in action_logs:
            assert log.user_id is None

        deleted_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam1.pteam_id))
        ).scalar_one_or_none()
        assert deleted_pteam is None

    def test_delete_user_if_not_last_admin(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        user2 = user_setup["user2"]
        pteam1 = user_setup["pteam1"]

        user3 = create_user(USER3)
        pteam_role = models.PTeamAccountRole(
            account_id=user3["user_id"], pteam_id=pteam1.pteam_id, is_admin=True
        )
        testdb.add(pteam_role)
        testdb.commit()

        delete_response = client.delete("/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        deleted_user = testdb.execute(
            select(models.Account).where(models.Account.user_id == str(user1.user_id))
        ).scalar_one_or_none()
        assert deleted_user is None

        deleted_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam1.pteam_id))
        ).scalar_one_or_none()
        assert deleted_pteam is not None

    def test_delete_user_if_not_admin(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        pteam1 = user_setup["pteam1"]

        pteam_role = models.PTeamAccountRole(
            account_id=user1.user_id,
            pteam_id=pteam1.pteam_id,
            is_admin=False,
        )
        testdb.add(pteam_role)
        testdb.commit()

        delete_response = client.delete("/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        deleted_user = testdb.execute(
            select(models.Account).where(models.Account.user_id == str(user1.user_id))
        ).scalar_one_or_none()
        assert deleted_user is None

        deleted_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam1.pteam_id))
        ).scalar_one_or_none()
        assert deleted_pteam is not None

    def test_delete_user_if_last_admin(self, user_setup, testdb: Session):
        user1 = user_setup["user1"]
        pteam1 = user_setup["pteam1"]

        delete_response = client.delete("/me", headers=headers(USER1))
        assert delete_response.status_code == 204

        deleted_pteam = testdb.execute(
            select(models.PTeam).where(models.PTeam.pteam_id == str(pteam1.pteam_id))
        ).scalar_one_or_none()
        assert deleted_pteam is None
