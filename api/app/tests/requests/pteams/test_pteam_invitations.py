from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import models, schemas
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    USER3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    headers,
    invite_to_pteam,
)

client = TestClient(app)


def test_admin_can_create_invitation():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)  # master have ADMIN

    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert datetime.fromisoformat(
        data["expiration"].replace("Z", "+00:00")
    ) == datetime.fromisoformat(request["expiration"]).replace(tzinfo=timezone.utc)
    assert data["limit_count"] == request["limit_count"]


def test_it_should_return_403_when_not_admin_create_invitation():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # no admin
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # try without admin
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_it_should_return_403_not_member_create_invitation():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_pteam(USER2, PTEAM2)

    # user2 is ADMIN of another pteam.
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_create_invitation__wrong_params():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # wrong limit
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 0,  # out of limit
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    # past date
    request = {
        "expiration": str(datetime(2000, 1, 1, 0, 0, 0, 0)),  # past date
        "limit_count": 1,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1), json=request
    )
    assert response.status_code == 200  # past date is OK


def test_invited_pteam():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)

    response = client.get(f"/pteams/invitation/{invitation.invitation_id}", headers=headers(USER2))
    assert response.status_code == 200
    data = response.json()
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert data["pteam_name"] == PTEAM1["pteam_name"]
    assert data["email"] == USER1["email"]
    assert UUID(data["user_id"]) == user1.user_id


def test_it_should_should_return_200_when_get_invitations_by_creator():
    create_user(USER1)  # master, have INVITE & ADMIN
    create_user(USER2)  # member, not have INVITE
    user3 = create_user(USER3)  # member, have INVITE
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
    )

    # create invitation
    invitation1 = invite_to_pteam(USER1, pteam1.pteam_id)

    # get by creator
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    assert len(response.json()) == 1  # invitation0 should be expired
    data = schemas.PTeamInvitationResponse(**response.json()[0])
    assert data.invitation_id == invitation1.invitation_id
    assert data.pteam_id == pteam1.pteam_id
    assert data.expiration == invitation1.expiration
    assert data.limit_count == invitation1.limit_count
    assert data.used_count == invitation1.used_count == 0


def test_it_should_should_return_200_when_get_invitations_by_admin():
    create_user(USER1)  # master, have INVITE & ADMIN
    create_user(USER2)  # member, not have INVITE
    user3 = create_user(USER3)  # member, have INVITE
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
    )

    # create invitation
    invitation1 = invite_to_pteam(USER1, pteam1.pteam_id)

    # get with admin
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER3))
    assert response.status_code == 200
    assert len(response.json()) == 1  # invitation0 should be expired
    data = schemas.PTeamInvitationResponse(**response.json()[0])
    assert data.invitation_id == invitation1.invitation_id
    assert data.pteam_id == pteam1.pteam_id
    assert data.expiration == invitation1.expiration
    assert data.limit_count == invitation1.limit_count
    assert data.used_count == invitation1.used_count == 0


def test_it_should_should_return_403_when_get_invitations_by_not_admin():
    create_user(USER1)  # master, have INVITE & ADMIN
    create_user(USER2)  # member, not have INVITE
    user3 = create_user(USER3)  # member, have INVITE
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
    )

    # create invitation
    invite_to_pteam(USER1, pteam1.pteam_id)

    # get without admin
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_delete_invitation():
    create_user(USER1)  # master, have INVITE
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation1 = invite_to_pteam(USER1, pteam1.pteam_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["invitation_id"] == str(invitation1.invitation_id)

    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/invitation/{invitation1.invitation_id}", headers=headers(USER1)
    )
    assert response.status_code == 204

    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_delete_invitation__by_another():
    create_user(USER1)
    create_user(USER2)
    user3 = create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)

    target_invitation = invite_to_pteam(USER1, pteam1.pteam_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["invitation_id"] == str(target_invitation.invitation_id)

    # delete by not pteam member
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/invitation/{target_invitation.invitation_id}",
        headers=headers(USER2),
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # delete by pteam member without admin
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/invitation/{target_invitation.invitation_id}",
        headers=headers(USER2),
    )
    assert response.status_code == 403

    # delete by pteam member with admin
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
    )
    assert response.status_code == 200
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/invitation/{target_invitation.invitation_id}",
        headers=headers(USER3),
    )
    assert response.status_code == 204

    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_invitation_limit(testdb):
    # access to testdb directly to control expiration.
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)

    # expired
    invitation1 = invite_to_pteam(USER1, pteam1.pteam_id)
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    assert len(response.json()) == 1
    row1 = (
        testdb.query(models.PTeamInvitation)
        .filter(models.PTeamInvitation.invitation_id == str(invitation1.invitation_id))
        .one()
    )
    row1.expiration = datetime(2000, 1, 1, 0, 0, 0, 0)  # past date
    testdb.add(row1)
    testdb.commit()
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    assert len(response.json()) == 0  # expired
    with pytest.raises(HTTPError, match="400: Bad Request"):
        accept_pteam_invitation(USER2, invitation1.invitation_id)

    # used
    invitation2 = invite_to_pteam(USER1, pteam1.pteam_id)
    assert invitation2.limit_count == 1  # limited once
    accept_pteam_invitation(USER2, invitation2.invitation_id)
    with pytest.raises(HTTPError, match="400: Bad Request"):
        accept_pteam_invitation(USER3, invitation2.invitation_id)  # cannot use twice


def test_apply_invitation():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 1
    assert set(x["user_id"] for x in members) == set(str(x.user_id) for x in [user1])
    response = client.get("/users/me", headers=headers(USER2))
    assert response.status_code == 200
    pteam_roles = response.json()["pteam_roles"]
    assert len(pteam_roles) == 0

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    assert set(x["user_id"] for x in members) == set(str(x.user_id) for x in [user1, user2])
    response = client.get("/users/me", headers=headers(USER2))
    assert response.status_code == 200
    pteam_roles = response.json()["pteam_roles"]
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in pteam_roles} == {
        x.pteam_id for x in [pteam1]
    }


def test_apply_invitation__individual_auth():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    members_map = {UUID(x["user_id"]): x for x in response.json()}
    assert members_map.get(user2.user_id).get("is_admin") is False
