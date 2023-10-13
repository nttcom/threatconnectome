from datetime import datetime, timedelta
from typing import List
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import models
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    GTEAM1,
    GTEAM2,
    PTEAM1,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
    USER3,
    ZONE1,
    ZONE2,
    ZONE3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_gteam_invitation,
    assert_200,
    assert_204,
    create_gteam,
    create_pteam,
    create_topic,
    create_user,
    create_zone,
    headers,
    invite_to_gteam,
)

client = TestClient(app)


def test_get_gteams():
    create_user(USER1)
    create_user(USER2)

    data = assert_200(client.get("/gteams", headers=headers(USER1)))
    assert data == []

    gteam1 = create_gteam(USER1, GTEAM1)

    data = assert_200(client.get("/gteams", headers=headers(USER1)))  # by creator
    assert len(data) == 1
    assert UUID(data[0]["gteam_id"]) == gteam1.gteam_id
    assert data[0]["gteam_name"] == GTEAM1["gteam_name"]

    data = assert_200(client.get("/gteams", headers=headers(USER2)))  # by someone
    assert len(data) == 1
    assert UUID(data[0]["gteam_id"]) == gteam1.gteam_id
    assert data[0]["gteam_name"] == GTEAM1["gteam_name"]

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.get("/gteams"))  # no headers


def test_get_gteam():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}", headers=headers(USER1)))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM1["gteam_name"]
    assert data["contact_info"] == GTEAM1["contact_info"]

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.get(f"/gteams/{gteam1.gteam_id}"))  # no headers


def test_get_gteam__by_member():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}", headers=headers(USER2)))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM1["gteam_name"]
    assert data["contact_info"] == GTEAM1["contact_info"]


def test_get_gteam__by_not_member():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)

    with pytest.raises(HTTPError, match="403: Forbidden: Not a gteam member"):
        assert_200(client.get(f"/gteams/{gteam1.gteam_id}", headers=headers(USER2)))


def test_create_gteam():
    user1 = create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}", headers=headers(USER1)))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM1["gteam_name"]
    assert data["contact_info"] == GTEAM1["contact_info"]

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id
    assert data[0]["email"] == USER1["email"]
    assert len(data[0]["gteams"]) == 1
    assert UUID(data[0]["gteams"][0]["gteam_id"]) == gteam1.gteam_id
    assert data[0]["gteams"][0]["gteam_name"] == GTEAM1["gteam_name"]


def test_create_gteam__without_auth():
    create_user(USER1)

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.post("/gteams", json=GTEAM1))  # no headers


def test_create_gteam__duplicate():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER1, GTEAM1)  # duplicate
    assert gteam1.gteam_id != gteam2.gteam_id
    del gteam1.gteam_id, gteam2.gteam_id
    assert gteam1 == gteam2


def test_update_gteam():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    # update gteam_name, contact_info
    assert GTEAM1["gteam_name"] != GTEAM2["gteam_name"]
    data = assert_200(client.put(f"/gteams/{gteam1.gteam_id}", headers=headers(USER1), json=GTEAM2))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM2["gteam_name"]
    assert data["contact_info"] == GTEAM2["contact_info"]

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}", headers=headers(USER1)))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM2["gteam_name"]
    assert data["contact_info"] == GTEAM2["contact_info"]


def test_update_gteam__by_member():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    gteam1 = create_gteam(USER1, GTEAM1)

    assert GTEAM1["gteam_name"] != GTEAM2["gteam_name"]

    # by member who does not have ADMIN
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.put(f"/gteams/{gteam1.gteam_id}", headers=headers(USER2), json=GTEAM2))

    # by member who has ADMIN
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER3, invitation.invitation_id)
    data = assert_200(client.put(f"/gteams/{gteam1.gteam_id}", headers=headers(USER3), json=GTEAM2))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM2["gteam_name"]


def test_update_gteam__by_not_member():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)

    assert GTEAM1["gteam_name"] != GTEAM2["gteam_name"]
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.put(f"/gteams/{gteam1.gteam_id}", headers=headers(USER2), json=GTEAM2))


def test_update_gteam_auth(testdb):
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
    gteam1 = create_gteam(USER1, GTEAM1)

    # initial
    row_master = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(user1.user_id),
        )
        .one()
    )
    assert row_master.authority == models.GTeamAuthIntFlag.GTEAM_MASTER

    # on invitation
    request_authes = list(map(models.GTeamAuthEnum, ["invite"]))
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=request_authes)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    row_user2 = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.GTeamAuthIntFlag.from_enums(request_authes)

    # update gteam auth
    request_authes = list(map(models.GTeamAuthEnum, ["admin"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_authes,
        }
    ]

    # without header
    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.post(f"/gteams/{gteam1.gteam_id}/authority", json=request))

    # without admin
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER2), json=request
            )
        )

    # by master
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user2.user_id)
    assert set(data[0]["authorities"]) == set(request_authes)
    row_user2 = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.GTeamAuthIntFlag.from_enums(request_authes)

    # by member having admin
    request_authes = list(map(models.GTeamAuthEnum, ["admin", "invite"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_authes,
        }
    ]
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER2), json=request)
    )
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user2.user_id)
    assert set(data[0]["authorities"]) == set(request_authes)
    row_user2 = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.GTeamAuthIntFlag.from_enums(request_authes)

    # not a member
    request = [
        {
            "user_id": str(user3.user_id),
            "authorities": [],
        }
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Not a gteam member"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )


def test_update_gteam_auth__pseudo_uuid(testdb):
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    # initial
    row_member = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    if not models.GTeamAuthIntFlag.GTEAM_MEMBER:
        assert row_member is None
    else:
        assert row_member.authority == models.GTeamAuthIntFlag.GTEAM_MEMBER
    row_others = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    if not models.GTeamAuthIntFlag.FREE_TEMPLATE:
        assert row_others is None
    else:
        assert row_others.authority == models.GTeamAuthIntFlag.FREE_TEMPLATE
    row_system = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(SYSTEM_UUID),
        )
        .one_or_none()
    )
    assert row_system is None

    # update
    request_auth = list(map(models.GTeamAuthEnum, ["invite"]))
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": request_auth},
        {"user_id": str(NOT_MEMBER_UUID), "authorities": request_auth},
    ]
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )
    assert len(data) == 2
    assert {x["user_id"] for x in data} == set(map(str, {MEMBER_UUID, NOT_MEMBER_UUID}))
    assert set(data[0]["authorities"]) == set(data[1]["authorities"]) == set(request_auth)
    row_member = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one()
    )
    assert row_member.authority == models.GTeamAuthIntFlag.INVITE
    row_others = (
        testdb.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam1.gteam_id),
            models.GTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one()
    )
    assert row_others.authority == models.GTeamAuthIntFlag.INVITE

    # give admin
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": [models.GTeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot give ADMIN to pseudo account"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )
    request = [
        {"user_id": str(NOT_MEMBER_UUID), "authorities": [models.GTeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot give ADMIN to pseudo account"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )

    # system account
    request = [
        {"user_id": str(SYSTEM_UUID), "authorities": [models.GTeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid user id"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )


def test_update_gteam_auth__remove_admin():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)

    # remove last admin
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )

    # invite another admin
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER2, invitation.invitation_id)

    # try again: removing (no more last) admin
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )

    # removing new last admin
    request = [
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER2), json=request
            )
        )

    # swap admin
    request = [
        {"user_id": str(user1.user_id), "authorities": [models.GTeamAuthEnum.ADMIN]},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER2), json=request)
    )

    # comeback admin
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.GTeamAuthEnum.ADMIN]},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )

    # remove all admin at once
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request
            )
        )


@pytest.mark.skip(reason="Currently, not enough authes for test")  # TODO
def test_get_gteam_auth():
    pass


def test_gteam_auth_effects__individual():
    create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_gteam(USER2, gteam1.gteam_id)

    # give INVITE
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.GTeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_gteam(USER2, gteam1.gteam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_gteam_auth_effects__pseudo_member():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_gteam(USER2, gteam1.gteam_id)

    # give INVITE to MEMBER
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": [models.GTeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_gteam(USER2, gteam1.gteam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_gteam_auth_effects__pseudo_not_member():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_gteam(USER2, gteam1.gteam_id)

    # give INVITE to NOT_MEMBER
    request = [
        {"user_id": str(NOT_MEMBER_UUID), "authorities": [models.GTeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_gteam(USER2, gteam1.gteam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_create_invitation():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": [models.GTeamAuthEnum.ADMIN, models.GTeamAuthEnum.INVITE],
    }
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request)
    )
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert set(data["authorities"]) == set(request["authorities"])
    assert data["limit_count"] == request["limit_count"]
    assert data["used_count"] == 0

    # with default params
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
    }
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request)
    )
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] is None
    assert len(data["authorities"]) == 0
    assert data["used_count"] == 0


def test_create_invitation__without_authority():
    create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    # without INVITE
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_gteam(USER2, gteam1.gteam_id)

    # give INVITE only (no ADMIN)
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.GTeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )
    invitation = invite_to_gteam(USER2, gteam1.gteam_id)
    assert invitation.invitation_id != UUID(int=0)

    # invite with authorities
    with pytest.raises(HTTPError, match=r"400: Bad Request: ADMIN required to set authorities"):
        invite_to_gteam(USER2, gteam1.gteam_id, authes=[models.GTeamAuthEnum.INVITE])

    # give INVITE with ADMIN
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": [models.GTeamAuthEnum.INVITE, models.GTeamAuthEnum.ADMIN],
        },
    ]
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1), json=request)
    )
    invitation = invite_to_gteam(USER2, gteam1.gteam_id, authes=[models.GTeamAuthEnum.INVITE])
    assert invitation.invitation_id != UUID(int=0)


def test_create_invitation__wrong_params():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    # wrong limit
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 0,
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Unwise limit_count"):
        assert_200(
            client.post(
                f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request
            )
        )

    # past date
    request = {
        "expiration": str(datetime(2000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request)
    )
    # Note: past date is OK


def test_invited_gteam():
    user1 = create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)

    data = assert_200(
        client.get(f"/gteams/invitation/{invitation.invitation_id}", headers=headers(USER2))
    )
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["gteam_name"] == GTEAM1["gteam_name"]
    assert data["email"] == USER1["email"]
    assert UUID(data["user_id"]) == user1.user_id


def test_invited_gteam__wrong_invitation():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    invite_to_gteam(USER1, gteam1.gteam_id)

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/gteams/invitation/{gteam1.gteam_id}", headers=headers(USER1)))


def test_list_invitations():
    create_user(USER1)  # master
    create_user(USER2)  # member having INVITE
    create_user(USER3)  # not member, then member not having INVITE
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.INVITE])
    accept_gteam_invitation(USER2, invitation.invitation_id)
    # Note: above invitations are now exceeded limit_count.

    request = {
        "expiration": str(datetime.now() + timedelta(days=1)),
        "limit_count": 3,
        "authorities": [models.GTeamAuthEnum.ADMIN, models.GTeamAuthEnum.INVITE],
    }
    invitation1 = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request)
    )

    # get by master
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == UUID(invitation1["invitation_id"])
    assert UUID(data[0]["gteam_id"]) == gteam1.gteam_id
    assert datetime.fromisoformat(data[0]["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data[0]["limit_count"] == request["limit_count"]
    assert set(data[0]["authorities"]) == set(request["authorities"])
    assert data[0]["used_count"] == 0

    # get by member having INVITE
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER2)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == UUID(invitation1["invitation_id"])
    assert UUID(data[0]["gteam_id"]) == gteam1.gteam_id
    assert datetime.fromisoformat(data[0]["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data[0]["limit_count"] == request["limit_count"]
    assert set(data[0]["authorities"]) == set(request["authorities"])
    assert data[0]["used_count"] == 0

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER3)))

    # get by member not having INVITE
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)  # no additional auth
    accept_gteam_invitation(USER3, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER3)))


def test_delete_invitation():
    create_user(USER1)  # master
    create_user(USER2)  # member having INVITE
    create_user(USER3)  # not member, then member not having INVITE
    gteam1 = create_gteam(USER1, GTEAM1)
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.INVITE])
    accept_gteam_invitation(USER2, invitation.invitation_id)

    target_id = invite_to_gteam(USER1, gteam1.gteam_id).invitation_id

    # delete by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/gteams/{gteam1.gteam_id}/invitation/{target_id}", headers=headers(USER3)
            )
        )

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation/", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == target_id

    # delete by member not having INVITE
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER3, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/gteams/{gteam1.gteam_id}/invitation/{target_id}", headers=headers(USER3)
            )
        )

    # delete by member having INVITE
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/invitation/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/gteams/invitation/{target_id}", headers=headers(USER1)))

    # delete twice
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/invitation/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204  # not 404 for the case already expired


def test_invitation_limit(testdb):
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    gteam1 = create_gteam(USER1, GTEAM1)

    # expired
    invitation1 = invite_to_gteam(USER1, gteam1.gteam_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 1
    row1 = (
        testdb.query(models.GTeamInvitation)
        .filter(
            models.GTeamInvitation.invitation_id == str(invitation1.invitation_id),
        )
        .one()
    )
    row1.expiration = datetime(2000, 1, 1, 0, 0, 0, 0)  # set past date
    testdb.add(row1)
    testdb.commit()
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 0  # expired
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        accept_gteam_invitation(USER2, invitation1.invitation_id)

    # used
    invitation2 = invite_to_gteam(USER1, gteam1.gteam_id)
    assert invitation2.limit_count == 1
    accept_gteam_invitation(USER2, invitation2.invitation_id)
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        accept_gteam_invitation(USER3, invitation1.invitation_id)


def test_accept_invitation():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    create_user(USER3)
    gteam1 = create_gteam(USER1, GTEAM1)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # create one-time invitation
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    data = assert_200(
        client.post(f"/gteams/{gteam1.gteam_id}/invitation", headers=headers(USER1), json=request)
    )
    invitation_id = data["invitation_id"]

    # accept by USER2
    request = {
        "invitation_id": str(invitation_id),
    }
    data = assert_200(client.post("/gteams/apply_invitation", headers=headers(USER2), json=request))
    assert UUID(data["gteam_id"]) == gteam1.gteam_id

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2
    assert {UUID(user["user_id"]) for user in data} == {user1.user_id, user2.user_id}

    # over use
    request = {
        "invitation_id": str(invitation_id),
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        assert_200(client.post("/gteams/apply_invitation", headers=headers(USER3), json=request))

    # accept twice
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    request = {
        "invitation_id": str(invitation.invitation_id),
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Already joined to the gteam"):
        assert_200(client.post("/gteams/apply_invitation", headers=headers(USER2), json=request))


def test_accept_invitation__individual_auth():
    create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    request_auth = [models.GTeamAuthEnum.INVITE]

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1)))
    auth_map = {x["user_id"]: x for x in data}
    assert auth_map.get(str(user2.user_id)) is None

    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=request_auth)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/authority", headers=headers(USER1)))
    auth_map = {x["user_id"]: x["authorities"] for x in data}
    auth_user2 = auth_map.get(str(user2.user_id))
    assert set(auth_user2) == set(request_auth)


def test_get_members():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    create_user(USER3)
    gteam1 = create_gteam(USER1, GTEAM1)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id
    assert data[0]["email"] == USER1["email"]

    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)

    def _find_user(user_list: List[dict], user_id: UUID) -> dict:
        return [user for user in user_list if UUID(user["user_id"]) == user_id][0]

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2
    member1 = _find_user(data, user1.user_id)
    assert member1["email"] == USER1["email"]
    assert len(member1["gteams"]) == 1
    assert UUID(member1["gteams"][0]["gteam_id"]) == gteam1.gteam_id
    member2 = _find_user(data, user2.user_id)
    assert member2["email"] == USER2["email"]
    assert len(member2["gteams"]) == 1
    assert UUID(member2["gteams"][0]["gteam_id"]) == gteam1.gteam_id

    # get by member
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER2)))
    assert len(data) == 2
    member1 = _find_user(data, user1.user_id)
    assert member1["email"] == USER1["email"]
    assert len(member1["gteams"]) == 1
    assert UUID(member1["gteams"][0]["gteam_id"]) == gteam1.gteam_id
    member2 = _find_user(data, user2.user_id)
    assert member2["email"] == USER2["email"]
    assert len(member2["gteams"]) == 1
    assert UUID(member2["gteams"][0]["gteam_id"]) == gteam1.gteam_id

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a gteam member"):
        assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER3)))


def test_delete_member__kickout():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)

    # invite admin
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout invited admin
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user2.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite not admin
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout invited member
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user2.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite admin again
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout master by invited admin
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user1.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER2)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user2.user_id


def test_delete_member__leave():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)

    # invite admin
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # invited admin leaves
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user2.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite not admin
    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # invited member leaves
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user2.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # master (last admin) leaves
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        response = client.delete(
            f"/gteams/{gteam1.gteam_id}/members/{user1.user_id}", headers=headers(USER1)
        )
        if response.status_code != 204:
            raise HTTPError(response)

    # invite admin again
    invitation = invite_to_gteam(USER1, gteam1.gteam_id, authes=[models.GTeamAuthEnum.ADMIN])
    accept_gteam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # try again
    response = client.delete(
        f"/gteams/{gteam1.gteam_id}/members/{user1.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/members", headers=headers(USER2)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user2.user_id


def test_list_gteam_zones():
    def _pick_zone(zones_: List[dict], zone_name_: str) -> dict:
        return next(filter(lambda x: x["zone_name"] == zone_name_, zones_), {})

    user1 = create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)

    create_user(USER2)
    gteam2 = create_gteam(USER2, GTEAM2)
    create_zone(USER2, gteam2.gteam_id, ZONE3)

    data = assert_200(client.get(f"/gteams/{gteam1.gteam_id}/zones", headers=headers(USER1)))
    assert len(data) == 2
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == ZONE1["zone_info"]
    assert UUID(zone1["created_by"]) == user1.user_id
    assert (zone2 := _pick_zone(data, ZONE2["zone_name"]))
    assert zone2["zone_info"] == ZONE2["zone_info"]


def test_get_gteam_zones_summary():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER1, gteam1.gteam_id, ZONE2)
    zone3 = create_zone(USER1, gteam1.gteam_id, ZONE3)

    # archive zone3
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{zone3.zone_name}/archived",
            headers=headers(USER1),
            json={"archived": True},
        )
    )
    assert data["archived"] is True

    # create pteam1 with zone1
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})

    # topic1, topic2 with zone1
    topic1 = create_topic(
        USER1,
        TOPIC1,
        zone_names=[zone1.zone_name],
        actions=[{**ACTION1, "zone_names": [zone1.zone_name]}],
    )
    topic2 = create_topic(USER1, TOPIC2, zone_names=[zone1.zone_name])
    assert topic1.updated_at < topic2.updated_at

    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/summary", headers=headers(USER1))
    )
    assert len(data["unarchived_zones"]) == 2
    assert {x["zone_name"] for x in data["unarchived_zones"]} == {zone1.zone_name, zone2.zone_name}
    assert len(data["unarchived_zones"][0]["topics"]) == 2
    assert UUID(data["unarchived_zones"][0]["topics"][0]["topic_id"]) == topic2.topic_id
    assert len(data["unarchived_zones"][0]["pteams"]) == 1
    assert len(data["unarchived_zones"][0]["actions"]) == 1
    assert UUID(data["unarchived_zones"][0]["pteams"][0]["pteam_id"]) == pteam1.pteam_id
    assert len(data["archived_zones"]) == 1
    assert data["archived_zones"][0]["zone_name"] == zone3.zone_name


def test_remove_zone_from_pteam():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})
    assert len(pteam1.zones) == 1
    assert pteam1.zones[0].zone_name == zone1.zone_name
    assert_204(
        client.delete(
            f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}/pteams/{pteam1.pteam_id}",
            headers=headers(USER1),
        )
    )
    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1)))
    assert len(data["zones"]) == 0
