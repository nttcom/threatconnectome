from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.main import app
from app.tests.medium.constants import (
    ATEAM1,
    ATEAM2,
    GROUP1,
    GROUP2,
    PTEAM1,
    PTEAM2,
    SAMPLE_SLACK_WEBHOOK_URL,
    TAG1,
    TAG2,
    TAG3,
    TOPIC1,
    TOPIC2,
    TOPIC3,
    TOPIC4,
    USER1,
    USER2,
    USER3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_ateam_invitation,
    accept_pteam_invitation,
    accept_watching_request,
    assert_200,
    create_ateam,
    create_pteam,
    create_tag,
    create_topic,
    create_topicstatus,
    create_user,
    create_watching_request,
    headers,
    invite_to_ateam,
    invite_to_pteam,
    schema_to_dict,
    upload_pteam_tags,
)

client = TestClient(app)


def test_get_ateams():
    create_user(USER1)
    create_user(USER2)

    data = assert_200(client.get("/ateams", headers=headers(USER1)))
    assert data == []

    ateam1 = create_ateam(USER1, ATEAM1)

    data = assert_200(client.get("/ateams", headers=headers(USER1)))  # by creator
    assert len(data) == 1
    assert UUID(data[0]["ateam_id"]) == ateam1.ateam_id
    assert data[0]["ateam_name"] == ATEAM1["ateam_name"]

    data = assert_200(client.get("/ateams", headers=headers(USER2)))  # by someone
    assert len(data) == 1
    assert UUID(data[0]["ateam_id"]) == ateam1.ateam_id
    assert data[0]["ateam_name"] == ATEAM1["ateam_name"]

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.get("/ateams"))  # no headers


def test_get_ateam():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1)))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert data["contact_info"] == ATEAM1["contact_info"]
    assert data["pteams"] == []

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}"))  # no headers


def test_get_ateam__by_member():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER2)))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert data["contact_info"] == ATEAM1["contact_info"]
    assert data["pteams"] == []


def test_get_ateam__by_not_member():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)

    with pytest.raises(HTTPError, match="403: Forbidden: Not an ateam member"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER2)))


def test_create_ateam():
    user1 = create_user(USER1)
    ateam1 = create_ateam(
        USER1, {**ATEAM1, "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL}}
    )

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1)))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert data["contact_info"] == ATEAM1["contact_info"]
    assert data["pteams"] == []
    assert data["alert_slack"]["enable"] == ateam1.alert_slack.enable
    assert (
        data["alert_slack"]["webhook_url"]
        == ateam1.alert_slack.webhook_url
        == SAMPLE_SLACK_WEBHOOK_URL
    )
    assert data["alert_mail"]["enable"] == ATEAM1["alert_mail"]["enable"]
    assert data["alert_mail"]["address"] == ATEAM1["alert_mail"]["address"]

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id
    assert data[0]["email"] == USER1["email"]
    assert len(data[0]["ateams"]) == 1
    assert UUID(data[0]["ateams"][0]["ateam_id"]) == ateam1.ateam_id
    assert data[0]["ateams"][0]["ateam_name"] == ATEAM1["ateam_name"]


def test_create_ateam__without_auth():
    create_user(USER1)

    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.post("/ateams", json=ATEAM1))  # no headers


def test_create_ateam__duplicate():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)
    ateam2 = create_ateam(USER1, ATEAM1)  # duplicate
    assert ateam1.ateam_id != ateam2.ateam_id
    del ateam1.ateam_id, ateam2.ateam_id
    assert ateam1 == ateam2


def test_update_ateam():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # update ateam_name, contact_info
    assert ATEAM1["ateam_name"] != ATEAM2["ateam_name"]
    data = assert_200(client.put(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1), json=ATEAM2))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM2["ateam_name"]
    assert data["contact_info"] == ATEAM2["contact_info"]
    assert data["pteams"] == []

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1)))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM2["ateam_name"]
    assert data["contact_info"] == ATEAM2["contact_info"]
    assert data["pteams"] == []


def test_update_validate_slack_webhook_url():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    json = {
        "alert_slack": {"enable": True, "webhook_url": "test"},
    }

    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid slack webhook url"):
        assert_200(client.put(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1), json=json))


def test_update_ateam__by_member():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)

    assert ATEAM1["ateam_name"] != ATEAM2["ateam_name"]

    # by member who does not have ADMIN
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.put(f"/ateams/{ateam1.ateam_id}", headers=headers(USER2), json=ATEAM2))

    # by member who has ADMIN
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER3, invitation.invitation_id)
    data = assert_200(client.put(f"/ateams/{ateam1.ateam_id}", headers=headers(USER3), json=ATEAM2))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM2["ateam_name"]
    assert data["alert_mail"]["enable"] == ATEAM2["alert_mail"]["enable"]
    assert data["alert_mail"]["address"] == ATEAM2["alert_mail"]["address"]


def test_update_ateam__by_not_member():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)

    assert ATEAM1["ateam_name"] != ATEAM2["ateam_name"]
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.put(f"/ateams/{ateam1.ateam_id}", headers=headers(USER2), json=ATEAM2))


def test_update_ateam_auth(testdb):
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)

    # initial
    row_master = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(user1.user_id),
        )
        .one()
    )
    assert row_master.authority == models.ATeamAuthIntFlag.ATEAM_MASTER

    # on invitation
    request_authes = list(map(models.ATeamAuthEnum, ["invite"]))
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=request_authes)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    row_user2 = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.ATeamAuthIntFlag.from_enums(request_authes)

    # update ateam auth
    request_authes = list(map(models.ATeamAuthEnum, ["admin"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_authes,
        }
    ]

    # without header
    with pytest.raises(HTTPError, match=r"401: Unauthorized"):
        assert_200(client.post(f"/ateams/{ateam1.ateam_id}/authority", json=request))

    # without admin
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER2), json=request
            )
        )

    # by master
    data = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user2.user_id)
    assert set(data[0]["authorities"]) == set(request_authes)
    row_user2 = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.ATeamAuthIntFlag.from_enums(request_authes)

    # by member having admin
    request_authes = list(map(models.ATeamAuthEnum, ["admin", "invite"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_authes,
        }
    ]
    data = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER2), json=request)
    )
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user2.user_id)
    assert set(data[0]["authorities"]) == set(request_authes)
    row_user2 = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.ATeamAuthIntFlag.from_enums(request_authes)

    # not a member
    request = [
        {
            "user_id": str(user3.user_id),
            "authorities": [],
        }
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Not an ateam member"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )


def test_update_ateam_auth__pseudo_uuid(testdb):
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # initial
    row_member = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_member:
        assert row_member.authority == models.ATeamAuthIntFlag.ATEAM_MEMBER  # pteam member
    row_others = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_others:
        assert row_member.authority == models.ATeamAuthIntFlag.FREE_TEMPLATE
    row_system = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(SYSTEM_UUID),
        )
        .one_or_none()
    )
    assert row_system is None

    # update
    request_auth = list(map(models.ATeamAuthEnum, ["invite"]))
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": request_auth},
        {"user_id": str(NOT_MEMBER_UUID), "authorities": request_auth},
    ]
    data = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )
    assert len(data) == 2
    assert {x["user_id"] for x in data} == set(map(str, {MEMBER_UUID, NOT_MEMBER_UUID}))
    assert set(data[0]["authorities"]) == set(data[1]["authorities"]) == set(request_auth)
    row_member = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one()
    )
    assert row_member.authority == models.ATeamAuthIntFlag.INVITE
    row_others = (
        testdb.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam1.ateam_id),
            models.ATeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one()
    )
    assert row_others.authority == models.ATeamAuthIntFlag.INVITE

    # give admin
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": [models.ATeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot give ADMIN to pseudo account"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )
    request = [
        {"user_id": str(NOT_MEMBER_UUID), "authorities": [models.ATeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot give ADMIN to pseudo account"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )

    # system account
    request = [
        {"user_id": str(SYSTEM_UUID), "authorities": [models.ATeamAuthEnum.ADMIN]},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid user id"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )


def test_update_ateam_auth__remove_admin__last():
    user1 = create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # remove last admin
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )


def test_update_ateam_auth__remove_admin__not_last():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    # invite another admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)

    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    # removing (no more last) admin
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )
    # removing last admin
    request = [
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER2), json=request
            )
        )


def test_update_ateam_auth__remove_admin__swap():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    # invite another admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)

    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    #  removing (no more last) admin
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )

    # swap admin
    request = [
        {"user_id": str(user1.user_id), "authorities": [models.ATeamAuthEnum.ADMIN]},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER2), json=request)
    )

    # comeback admin
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.ATeamAuthEnum.ADMIN]},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )

    # remove all admin at once
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request
            )
        )


@pytest.mark.skip(reason="Currently, not enough authes for test")  # TODO
def test_get_ateam_auth():
    pass


def test_ateam_auth_effects__individual():
    create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_ateam(USER2, ateam1.ateam_id)

    # give INVITE
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.ATeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_ateam(USER2, ateam1.ateam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_ateam_auth_effects__pseudo_member():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_ateam(USER2, ateam1.ateam_id)

    # give INVITE to MEMBER
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": [models.ATeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_ateam(USER2, ateam1.ateam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_ateam_auth_effects__pseudo_not_member():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_ateam(USER2, ateam1.ateam_id)

    # give INVITE to NOT_MEMBER
    request = [
        {"user_id": str(NOT_MEMBER_UUID), "authorities": [models.ATeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )

    # try again
    invitation = invite_to_ateam(USER2, ateam1.ateam_id)
    assert invitation.invitation_id != UUID(int=0)


def test_create_invitation():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": [models.ATeamAuthEnum.ADMIN, models.ATeamAuthEnum.INVITE],
    }
    data = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request)
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
        client.post(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request)
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
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    # without INVITE
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        invite_to_ateam(USER2, ateam1.ateam_id)

    # give INVITE only (no ADMIN)
    request = [
        {"user_id": str(user2.user_id), "authorities": [models.ATeamAuthEnum.INVITE]},
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )
    invitation = invite_to_ateam(USER2, ateam1.ateam_id)
    assert invitation.invitation_id != UUID(int=0)

    # invite with authorities
    with pytest.raises(HTTPError, match=r"400: Bad Request: ADMIN required to set authorities"):
        invite_to_ateam(USER2, ateam1.ateam_id, authes=[models.ATeamAuthEnum.INVITE])

    # give INVITE with ADMIN
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": [models.ATeamAuthEnum.INVITE, models.ATeamAuthEnum.ADMIN],
        },
    ]
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1), json=request)
    )
    invitation = invite_to_ateam(USER2, ateam1.ateam_id, authes=[models.ATeamAuthEnum.INVITE])
    assert invitation.invitation_id != UUID(int=0)


def test_create_invitation__wrong_params():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # wrong limit
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 0,
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Unwise limit_count"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request
            )
        )

    # past date
    request = {
        "expiration": str(datetime(2000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request)
    )
    # Note: past date is OK


def test_invited_ateam():
    user1 = create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)

    data = assert_200(
        client.get(f"/ateams/invitation/{invitation.invitation_id}", headers=headers(USER2))
    )
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert data["email"] == USER1["email"]
    assert UUID(data["user_id"]) == user1.user_id


def test_invited_ateam__wrong_invitation():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)
    invite_to_ateam(USER1, ateam1.ateam_id)

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/ateams/invitation/{ateam1.ateam_id}", headers=headers(USER1)))


def test_list_invitations():
    create_user(USER1)  # master
    create_user(USER2)  # member having INVITE
    create_user(USER3)  # not member, then member not having INVITE
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.INVITE])
    accept_ateam_invitation(USER2, invitation.invitation_id)
    # Note: above invitations are now exceeded limit_count.

    request = {
        "expiration": str(datetime.now() + timedelta(days=1)),
        "limit_count": 3,
        "authorities": [models.ATeamAuthEnum.ADMIN, models.ATeamAuthEnum.INVITE],
    }
    invitation1 = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request)
    )

    # get by master
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == UUID(invitation1["invitation_id"])
    assert UUID(data[0]["ateam_id"]) == ateam1.ateam_id
    assert datetime.fromisoformat(data[0]["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data[0]["limit_count"] == request["limit_count"]
    assert set(data[0]["authorities"]) == set(request["authorities"])
    assert data[0]["used_count"] == 0

    # get by member having INVITE
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER2)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == UUID(invitation1["invitation_id"])
    assert UUID(data[0]["ateam_id"]) == ateam1.ateam_id
    assert datetime.fromisoformat(data[0]["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data[0]["limit_count"] == request["limit_count"]
    assert set(data[0]["authorities"]) == set(request["authorities"])
    assert data[0]["used_count"] == 0

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER3)))

    # get by member not having INVITE
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)  # no additional auth
    accept_ateam_invitation(USER3, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER3)))


def test_delete_invitation():
    create_user(USER1)  # master
    create_user(USER2)  # member having INVITE
    create_user(USER3)  # not member, then member not having INVITE
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.INVITE])
    accept_ateam_invitation(USER2, invitation.invitation_id)

    target_id = invite_to_ateam(USER1, ateam1.ateam_id).invitation_id

    # delete by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/invitation/{target_id}", headers=headers(USER3)
            )
        )

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation/", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["invitation_id"]) == target_id

    # delete by member not having INVITE
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER3, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/invitation/{target_id}", headers=headers(USER3)
            )
        )

    # delete by member having INVITE
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/invitation/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/ateams/invitation/{target_id}", headers=headers(USER1)))

    # delete twice
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/invitation/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204  # not 404 for the case already expired


def test_invitation_limit(testdb):
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)

    # expired
    invitation1 = invite_to_ateam(USER1, ateam1.ateam_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 1
    row1 = (
        testdb.query(models.ATeamInvitation)
        .filter(
            models.ATeamInvitation.invitation_id == str(invitation1.invitation_id),
        )
        .one()
    )
    row1.expiration = datetime(2000, 1, 1, 0, 0, 0, 0)  # set past date
    testdb.add(row1)
    testdb.commit()
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1)))
    assert len(data) == 0  # expired
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        accept_ateam_invitation(USER2, invitation1.invitation_id)

    # used
    invitation2 = invite_to_ateam(USER1, ateam1.ateam_id)
    assert invitation2.limit_count == 1
    accept_ateam_invitation(USER2, invitation2.invitation_id)
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        accept_ateam_invitation(USER3, invitation1.invitation_id)


def test_accept_invitation():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # create one-time invitation
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    data = assert_200(
        client.post(f"/ateams/{ateam1.ateam_id}/invitation", headers=headers(USER1), json=request)
    )
    invitation_id = data["invitation_id"]

    # accept by USER2
    request = {
        "invitation_id": str(invitation_id),
    }
    data = assert_200(client.post("/ateams/apply_invitation", headers=headers(USER2), json=request))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2
    assert {UUID(user["user_id"]) for user in data} == {user1.user_id, user2.user_id}

    # over use
    request = {
        "invitation_id": str(invitation_id),
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) invitation id"):
        assert_200(client.post("/ateams/apply_invitation", headers=headers(USER3), json=request))

    # accept twice
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    request = {
        "invitation_id": str(invitation.invitation_id),
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Already joined to the ateam"):
        assert_200(client.post("/ateams/apply_invitation", headers=headers(USER2), json=request))


def test_accept_invitation__individual_auth():
    create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    request_auth = [models.ATeamAuthEnum.INVITE]

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1)))
    auth_map = {x["user_id"]: x for x in data}
    assert auth_map.get(str(user2.user_id)) is None

    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=request_auth)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/authority", headers=headers(USER1)))
    auth_map = {x["user_id"]: x["authorities"] for x in data}
    auth_user2 = auth_map.get(str(user2.user_id))
    assert set(auth_user2) == set(request_auth)


def test_get_members():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id
    assert data[0]["email"] == USER1["email"]

    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    def _find_user(user_list: List[dict], user_id: UUID) -> dict:
        return [user for user in user_list if UUID(user["user_id"]) == user_id][0]

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2
    member1 = _find_user(data, user1.user_id)
    assert member1["email"] == USER1["email"]
    assert len(member1["ateams"]) == 1
    assert UUID(member1["ateams"][0]["ateam_id"]) == ateam1.ateam_id
    member2 = _find_user(data, user2.user_id)
    assert member2["email"] == USER2["email"]
    assert len(member2["ateams"]) == 1
    assert UUID(member2["ateams"][0]["ateam_id"]) == ateam1.ateam_id

    # get by member
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER2)))
    assert len(data) == 2
    member1 = _find_user(data, user1.user_id)
    assert member1["email"] == USER1["email"]
    assert len(member1["ateams"]) == 1
    assert UUID(member1["ateams"][0]["ateam_id"]) == ateam1.ateam_id
    member2 = _find_user(data, user2.user_id)
    assert member2["email"] == USER2["email"]
    assert len(member2["ateams"]) == 1
    assert UUID(member2["ateams"][0]["ateam_id"]) == ateam1.ateam_id

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER3)))


def test_delete_member__kickout():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)

    # invite admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout invited admin
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/members/{user2.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite not admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout invited member
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/members/{user2.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite admin again
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # kickout master by invited admin
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/members/{user1.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER2)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user2.user_id


def test_delete_member__leave():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)

    # invite admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # invited admin leaves
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/members/{user2.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # invite not admin
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 2

    # invited member leaves
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/members/{user2.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/members", headers=headers(USER1)))
    assert len(data) == 1
    assert UUID(data[0]["user_id"]) == user1.user_id

    # master (last admin) leaves
    with pytest.raises(HTTPError, match=r"400: Bad Request: Removing last ADMIN is not allowed"):
        response = client.delete(
            f"/ateams/{ateam1.ateam_id}/members/{user1.user_id}", headers=headers(USER1)
        )
        if response.status_code != 204:
            raise HTTPError(response)


def test_access_pteam():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2)))

    # by not linked ateam member
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2)))

    # by linked ateam member
    watching_request = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam1.pteam_id)
    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2)))
    assert len(data["ateams"]) == 1
    assert UUID(data["ateams"][0]["ateam_id"]) == ateam1.ateam_id
    assert data["ateams"][0]["ateam_name"] == ATEAM1["ateam_name"]
    assert data["pteam_name"] == PTEAM1["pteam_name"]

    # purge pteam
    client.delete(
        f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam1.pteam_id}", headers=headers(USER1)
    )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2)))


def test_get_watching_pteams():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)

    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER1))
    )
    assert len(data) == 0

    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)

    def _find_pteam(pteam_list: List[dict], pteam_id: UUID) -> dict:
        return [pteam for pteam in pteam_list if UUID(pteam["pteam_id"]) == pteam_id][0]

    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER1))
    )
    assert len(data) == 1
    pteam = _find_pteam(data, pteam1.pteam_id)
    assert pteam["pteam_name"] == PTEAM1["pteam_name"]

    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    # get by member
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER2))
    )
    assert len(data) == 1
    pteam = _find_pteam(data, pteam1.pteam_id)
    assert pteam["pteam_name"] == PTEAM1["pteam_name"]

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER3)))


def test_remove_watching_pteam():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)

    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    watching_request = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam1.pteam_id)

    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER1))
    )
    assert len(data) == 1

    # delete by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam1.pteam_id}",
                headers=headers(USER3),
            )
        )

    # delete by not ADMIN
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam1.pteam_id}",
                headers=headers(USER2),
            )
        )

    # delete by ADMIN
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam1.pteam_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER1))
    )
    assert len(data) == 0
    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER1)))
    assert len(data) == 0


def test_create_watching_requests():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1), json=request
        )
    )
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] == request["limit_count"]
    assert data["used_count"] == 0

    # with default params
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
    }
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1), json=request
        )
    )
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] is None
    assert data["used_count"] == 0


def test_create_watching_requests__without_authority():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    # without ADMIN
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        create_watching_request(USER2, ateam1.ateam_id)


def test_create_watching_request__wrong_params():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)

    # wrong limit
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 0,
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Unwise limit_count"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1), json=request
            )
        )

    # past date
    request = {
        "expiration": str(datetime(2000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }
    assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1), json=request
        )
    )
    # Note: past date is OK


def test_get_requested_ateam():
    user1 = create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    watching_request = create_watching_request(USER1, ateam1.ateam_id)

    data = assert_200(
        client.get(
            f"/ateams/watching_request/{watching_request.request_id}", headers=headers(USER2)
        )
    )
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert data["email"] == USER1["email"]
    assert UUID(data["user_id"]) == user1.user_id


def test_get_requested_ateam__wrong_request():
    create_user(USER1)
    ateam1 = create_ateam(USER1, ATEAM1)
    create_watching_request(USER1, ateam1.ateam_id)

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(
            client.get(f"/ateams/watching_request/{ateam1.ateam_id}", headers=headers(USER1))
        )


def test_list_watching_request():
    create_user(USER1)  # master
    create_user(USER2)  # not member, then member not having ADMIN
    ateam1 = create_ateam(USER1, ATEAM1)

    request = {
        "expiration": str(datetime.now() + timedelta(days=1)),
        "limit_count": 3,
    }
    watching_request1 = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1), json=request
        )
    )

    # get by master
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1))
    )
    assert len(data) == 1
    assert UUID(data[0]["request_id"]) == UUID(watching_request1["request_id"])
    assert UUID(data[0]["ateam_id"]) == ateam1.ateam_id
    assert datetime.fromisoformat(data[0]["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data[0]["limit_count"] == request["limit_count"]
    assert data[0]["used_count"] == 0

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.get(f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER2))
        )

    # get by member not having ADMIN
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)  # no additional auth
    accept_ateam_invitation(USER2, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.get(f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER2))
        )


def test_delete_watching_request():
    create_user(USER1)  # master
    create_user(USER2)  # member having ADMIN
    create_user(USER3)  # not member, then member not having ADMIN
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id, authes=[models.ATeamAuthEnum.ADMIN])
    accept_ateam_invitation(USER2, invitation.invitation_id)

    target_id = create_watching_request(USER1, ateam1.ateam_id).request_id

    # delete by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/watching_request/{target_id}", headers=headers(USER3)
            )
        )

    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_request/", headers=headers(USER1))
    )
    assert len(data) == 1
    assert UUID(data[0]["request_id"]) == target_id

    # delete by member not having ADMIN
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER3, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/watching_request/{target_id}", headers=headers(USER3)
            )
        )

    # delete by member having ADMIN
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/watching_request/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204

    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/ateams/watching_request/{target_id}", headers=headers(USER1)))

    # delete twice
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/watching_request/{target_id}", headers=headers(USER2)
    )
    assert response.status_code == 204  # not 404 for the case already expired


def test_watching_request_limit(testdb: Session):
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER2, PTEAM1)

    # expired
    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1))
    )
    assert len(data) == 1
    row1 = (
        testdb.query(models.ATeamWatchingRequest)
        .filter(
            models.ATeamWatchingRequest.request_id == str(watching_request1.request_id),
        )
        .one()
    )
    row1.expiration = datetime(2000, 1, 1, 0, 0, 0, 0)  # set past date
    testdb.add(row1)
    testdb.commit()
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_request", headers=headers(USER1))
    )
    assert len(data) == 0  # expired
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) request id"):
        accept_watching_request(USER2, watching_request1.request_id, pteam1.pteam_id)


def test_accept_watching_request():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER2, PTEAM1)

    # create one-time watching_request
    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)

    # accept by USER2
    request = {"request_id": str(watching_request1.request_id), "pteam_id": str(pteam1.pteam_id)}
    data = assert_200(
        client.post("/ateams/apply_watching_request", headers=headers(USER2), json=request)
    )
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert UUID(data["ateams"][0]["ateam_id"]) == ateam1.ateam_id

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}", headers=headers(USER1)))
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert data["ateam_name"] == ATEAM1["ateam_name"]
    assert len(data["pteams"]) == 1
    assert UUID(data["pteams"][0]["pteam_id"]) == pteam1.pteam_id
    assert data["pteams"][0]["pteam_name"] == PTEAM1["pteam_name"]

    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2)))
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert len(data["ateams"]) == 1
    assert UUID(data["ateams"][0]["ateam_id"]) == ateam1.ateam_id
    assert data["ateams"][0]["ateam_name"] == ATEAM1["ateam_name"]

    # over use
    request = {"request_id": str(watching_request1.request_id), "pteam_id": str(pteam1.pteam_id)}
    with pytest.raises(HTTPError, match=r"400: Bad Request: Invalid \(or expired\) request id"):
        assert_200(
            client.post("/ateams/apply_watching_request", headers=headers(USER2), json=request)
        )

    # accept twice
    watching_request2 = create_watching_request(USER1, ateam1.ateam_id)
    request = {"request_id": str(watching_request2.request_id), "pteam_id": str(pteam1.pteam_id)}
    with pytest.raises(HTTPError, match=r"400: Bad Request: Already connect to the ateam"):
        assert_200(
            client.post("/ateams/apply_watching_request", headers=headers(USER2), json=request)
        )


def test_accept_watching_request__not_admin():
    create_user(USER1)
    create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    # USER2 is not ADMIN of pteam1
    request = {"request_id": str(watching_request1.request_id), "pteam_id": str(pteam1.pteam_id)}
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.post("/ateams/apply_watching_request", headers=headers(USER2), json=request)
        )


def test_get_topic_status():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)
    pteam1 = create_pteam(USER1, PTEAM1)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("Pipfile.lock", "1.0.0")]}, True)
    pteam2 = create_pteam(USER1, PTEAM2)
    upload_pteam_tags(
        USER1,
        pteam2.pteam_id,
        GROUP2,
        {
            TAG1: [("Pipfile.lock", "1.0.0")],
            TAG2: [("Pipfile.lock", "1.0.0")],
            TAG3: [("Pipfile.lock", "1.0.0")],
        },
        True,
    )
    ateam1 = create_ateam(USER1, ATEAM1)

    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)

    # wrong ateam_id
    with pytest.raises(HTTPError, match=r"404: Not Found"):
        assert_200(client.get(f"/ateams/{pteam1.pteam_id}/topicstatus", headers=headers(USER1)))

    # no pteams
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 0
    assert len(data["topic_statuses"]) == 0

    # PTEAM1 joins
    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)

    # no topics
    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 0
    assert len(data["topic_statuses"]) == 0

    # create topic1
    topic1 = create_topic(USER1, {**TOPIC1, "tags": [TAG1]})

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic1.topic_id
    assert topic_statuses[0]["title"] == TOPIC1["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC1["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic1.updated_at
    assert topic_statuses[0]["num_pteams"] == 1
    assert len(topic_statuses[0]["pteams"]) == 1
    pteam = topic_statuses[0]["pteams"][0]
    assert UUID(pteam["pteam_id"]) == pteam1.pteam_id
    assert pteam["pteam_name"] == PTEAM1["pteam_name"]
    pteam_statuses = pteam["statuses"]
    assert len(pteam_statuses) == 1
    assert UUID(pteam_statuses[0]["topic_id"]) == topic1.topic_id
    assert UUID(pteam_statuses[0]["pteam_id"]) == pteam1.pteam_id
    assert pteam_statuses[0]["tag"] == schema_to_dict(tag1)
    assert pteam_statuses[0]["topic_status"] == models.TopicStatusType.alerted
    assert pteam_statuses[0]["assignees"] == []
    assert pteam_statuses[0]["scheduled_at"] is None

    # ack
    request = {
        "topic_status": models.TopicStatusType.acknowledged,
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic1.topic_id
    assert topic_statuses[0]["title"] == TOPIC1["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC1["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic1.updated_at
    assert topic_statuses[0]["num_pteams"] == 1
    assert len(topic_statuses[0]["pteams"]) == 1
    pteam = topic_statuses[0]["pteams"][0]
    assert UUID(pteam["pteam_id"]) == pteam1.pteam_id
    assert pteam["pteam_name"] == PTEAM1["pteam_name"]
    pteam_statuses = pteam["statuses"]
    assert len(pteam_statuses) == 1
    assert UUID(pteam_statuses[0]["topic_id"]) == topic1.topic_id
    assert UUID(pteam_statuses[0]["pteam_id"]) == pteam1.pteam_id
    assert pteam_statuses[0]["tag"] == schema_to_dict(tag1)
    assert pteam_statuses[0]["topic_status"] == models.TopicStatusType.acknowledged
    assert set(map(UUID, pteam_statuses[0]["assignees"])) == set([user1.user_id])
    assert pteam_statuses[0]["scheduled_at"] is None

    # schedule
    request = {
        "topic_status": models.TopicStatusType.scheduled,
        "scheduled_at": str(datetime(3000, 1, 1)),
        "assignees": list(map(str, [user1.user_id, user2.user_id])),
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic1.topic_id
    assert topic_statuses[0]["title"] == TOPIC1["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC1["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic1.updated_at
    assert topic_statuses[0]["num_pteams"] == 1
    pteam = topic_statuses[0]["pteams"][0]
    assert UUID(pteam["pteam_id"]) == pteam1.pteam_id
    assert pteam["pteam_name"] == PTEAM1["pteam_name"]
    pteam_statuses = pteam["statuses"]
    assert len(pteam_statuses) == 1
    assert UUID(pteam_statuses[0]["topic_id"]) == topic1.topic_id
    assert UUID(pteam_statuses[0]["pteam_id"]) == pteam1.pteam_id
    assert pteam_statuses[0]["tag"] == schema_to_dict(tag1)
    assert pteam_statuses[0]["topic_status"] == models.TopicStatusType.scheduled
    assert set(map(UUID, pteam_statuses[0]["assignees"])) == set([user1.user_id, user2.user_id])
    assert datetime.fromisoformat(pteam_statuses[0]["scheduled_at"]) == datetime.fromisoformat(
        request["scheduled_at"]
    )

    # complete
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 0
    assert len(data["topic_statuses"]) == 0

    def _pick_pteam(pteams, pteam_id):
        return next(filter(lambda x: x["pteam_id"] == str(pteam_id), pteams), None)

    def _pick_tag(statuses, tag_id):
        return next(filter(lambda x: x["tag"]["tag_id"] == str(tag_id), statuses), None)

    # PTEAM2 joins
    watching_request2 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request2.request_id, pteam2.pteam_id)

    # create topic2 with 2 tags
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [TAG1, TAG2]})

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 2
    assert len(topic_statuses := data["topic_statuses"]) == 2
    assert topic2.updated_at > topic1.updated_at
    assert topic2.threat_impact > topic1.threat_impact
    # topic1
    assert UUID(topic_statuses[0]["topic_id"]) == topic1.topic_id
    assert topic_statuses[0]["title"] == TOPIC1["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC1["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic1.updated_at
    assert topic_statuses[0]["num_pteams"] == 1
    assert len(topic_statuses[0]["pteams"]) == 1
    assert UUID(topic_statuses[0]["pteams"][0]["pteam_id"]) == pteam2.pteam_id
    assert topic_statuses[0]["pteams"][0]["pteam_name"] == PTEAM2["pteam_name"]
    assert len(topic_statuses[0]["pteams"][0]["statuses"]) == 1
    assert UUID(topic_statuses[0]["pteams"][0]["statuses"][0]["topic_id"]) == topic1.topic_id
    assert UUID(topic_statuses[0]["pteams"][0]["statuses"][0]["pteam_id"]) == pteam2.pteam_id
    assert topic_statuses[0]["pteams"][0]["statuses"][0]["tag"] == schema_to_dict(tag1)
    assert (
        topic_statuses[0]["pteams"][0]["statuses"][0]["topic_status"]
        == models.TopicStatusType.alerted
    )
    assert topic_statuses[0]["pteams"][0]["statuses"][0]["assignees"] == []
    assert topic_statuses[0]["pteams"][0]["statuses"][0]["scheduled_at"] is None
    # topic2
    assert UUID(topic_statuses[1]["topic_id"]) == topic2.topic_id
    assert topic_statuses[1]["title"] == TOPIC2["title"]
    assert topic_statuses[1]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[1]["updated_at"]) == topic2.updated_at
    assert topic_statuses[1]["num_pteams"] == 2
    assert len(topic_statuses[1]["pteams"]) == 2
    tmp1 = _pick_pteam(topic_statuses[1]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    # stXYZ = topicX + pteamY + tagZ
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.alerted
    assert st211["assignees"] == []
    assert st211["scheduled_at"] is None
    tmp2 = _pick_pteam(topic_statuses[1]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 2
    tmp221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert tmp221
    assert tmp221["topic_status"] == models.TopicStatusType.alerted
    assert tmp221["assignees"] == []
    assert tmp221["scheduled_at"] is None
    tmp222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert tmp222
    assert tmp222["topic_status"] == models.TopicStatusType.alerted
    assert tmp222["assignees"] == []
    assert tmp222["scheduled_at"] is None

    # PTEAM2 complete TOPIC1 TAG1
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.alerted
    assert st211["assignees"] == []
    assert st211["scheduled_at"] is None
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 2
    st221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert st221["topic_status"] == models.TopicStatusType.alerted
    assert st221["assignees"] == []
    assert st221["scheduled_at"] is None
    st222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert st222["topic_status"] == models.TopicStatusType.alerted
    assert st222["assignees"] == []
    assert st222["scheduled_at"] is None

    # PTEAM2 ack TOPIC2 TAG1
    request = {
        "topic_status": models.TopicStatusType.acknowledged,
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.alerted
    assert st211["assignees"] == []
    assert st211["scheduled_at"] is None
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 2
    assert tmp2["statuses"][0]["topic_status"] == models.TopicStatusType.alerted  # worst first
    assert tmp2["statuses"][1]["topic_status"] == models.TopicStatusType.acknowledged
    st221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert st221["topic_status"] == models.TopicStatusType.acknowledged
    assert st221["assignees"] == list(map(str, [user1.user_id]))
    assert st221["scheduled_at"] is None
    st222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert st222["topic_status"] == models.TopicStatusType.alerted
    assert st222["assignees"] == []
    assert st222["scheduled_at"] is None

    # PTEAM2 schedule TOPIC2 TAG2
    request = {
        "topic_status": models.TopicStatusType.scheduled,
        "scheduled_at": str(datetime(3000, 1, 1)),
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic2.topic_id, tag2.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    assert UUID(topic_statuses[0]["pteams"][0]["pteam_id"]) == pteam1.pteam_id  # worst first
    assert UUID(topic_statuses[0]["pteams"][1]["pteam_id"]) == pteam2.pteam_id
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.alerted
    assert st211["assignees"] == []
    assert st211["scheduled_at"] is None
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 2
    assert tmp2["statuses"][0]["topic_status"] == models.TopicStatusType.acknowledged  # worst first
    assert tmp2["statuses"][1]["topic_status"] == models.TopicStatusType.scheduled
    st221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert st221["topic_status"] == models.TopicStatusType.acknowledged
    assert st221["assignees"] == list(map(str, [user1.user_id]))
    assert st221["scheduled_at"] is None
    st222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert st222["topic_status"] == models.TopicStatusType.scheduled
    assert st222["assignees"] == []
    assert datetime.fromisoformat(st222["scheduled_at"]) == datetime.fromisoformat(
        request["scheduled_at"]
    )

    # PTEAM1 schedule TOPIC2 TAG1
    request = {
        "topic_status": models.TopicStatusType.scheduled,
        "scheduled_at": str(datetime(3000, 12, 31)),
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    assert UUID(topic_statuses[0]["pteams"][0]["pteam_id"]) == pteam2.pteam_id  # worst first
    assert UUID(topic_statuses[0]["pteams"][1]["pteam_id"]) == pteam1.pteam_id
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.scheduled
    assert st211["assignees"] == []
    assert datetime.fromisoformat(st211["scheduled_at"]) == datetime.fromisoformat(
        request["scheduled_at"]
    )
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 2
    assert tmp2["statuses"][0]["topic_status"] == models.TopicStatusType.acknowledged  # worst first
    assert tmp2["statuses"][1]["topic_status"] == models.TopicStatusType.scheduled
    st221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert st221["topic_status"] == models.TopicStatusType.acknowledged
    assert st221["assignees"] == list(map(str, [user1.user_id]))
    assert st221["scheduled_at"] is None
    st222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert st222["topic_status"] == models.TopicStatusType.scheduled
    assert st222["assignees"] == []

    # PTEAM2 complete TOPIC2 TAG1
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    assert UUID(topic_statuses[0]["pteams"][0]["pteam_id"]) == pteam1.pteam_id  # later first(12/31)
    assert UUID(topic_statuses[0]["pteams"][1]["pteam_id"]) == pteam2.pteam_id  # (3000/1/1)
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211
    assert st211["topic_status"] == models.TopicStatusType.scheduled
    assert st211["assignees"] == []
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 1
    st222 = _pick_tag(tmp2["statuses"], tag2.tag_id)
    assert st222["topic_status"] == models.TopicStatusType.scheduled
    assert st222["assignees"] == []

    # PTEAM2 complete TOPIC2 TAG2
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic2.topic_id, tag2.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 1
    assert len(topic_statuses[0]["pteams"]) == 1
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211["topic_status"] == models.TopicStatusType.scheduled
    assert st211["assignees"] == []

    # PTEAM2 ack TOPIC2 TAG1 again
    request = {
        "topic_status": models.TopicStatusType.acknowledged,
    }
    create_topicstatus(USER1, pteam2.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(client.get(f"/ateams/{ateam1.ateam_id}/topicstatus", headers=headers(USER1)))
    assert data["num_topics"] == 1
    assert len(topic_statuses := data["topic_statuses"]) == 1
    assert UUID(topic_statuses[0]["topic_id"]) == topic2.topic_id
    assert topic_statuses[0]["title"] == TOPIC2["title"]
    assert topic_statuses[0]["threat_impact"] == TOPIC2["threat_impact"]
    assert datetime.fromisoformat(topic_statuses[0]["updated_at"]) == topic2.updated_at
    assert topic_statuses[0]["num_pteams"] == 2
    assert len(topic_statuses[0]["pteams"]) == 2
    assert UUID(topic_statuses[0]["pteams"][0]["pteam_id"]) == pteam2.pteam_id  # worst first
    assert UUID(topic_statuses[0]["pteams"][1]["pteam_id"]) == pteam1.pteam_id
    tmp1 = _pick_pteam(topic_statuses[0]["pteams"], pteam1.pteam_id)
    assert tmp1
    assert len(tmp1["statuses"]) == 1
    st211 = _pick_tag(tmp1["statuses"], tag1.tag_id)
    assert st211["topic_status"] == models.TopicStatusType.scheduled
    assert st211["assignees"] == []
    tmp2 = _pick_pteam(topic_statuses[0]["pteams"], pteam2.pteam_id)
    assert tmp2
    assert len(tmp2["statuses"]) == 1
    st221 = _pick_tag(tmp2["statuses"], tag1.tag_id)
    assert st221["topic_status"] == models.TopicStatusType.acknowledged
    assert st221["assignees"] == []


class TestGetTopicStatusWithQueryParams:
    # default params on API
    default_offset: int = 0
    default_limit: int = 10
    default_sort_key: schemas.TopicSortKey = schemas.TopicSortKey.THREAT_IMPACT
    default_search: Optional[str] = None
    # reusable resources
    pteam1: schemas.PTeamInfo
    ateam1: schemas.ATeamInfo

    # FIXME:
    #   cannot use class scope because DB is rollbacked with function scope in handle_testdb
    #   (modified DB with class scope is not rollbacked in handle_db and causes conflicts).
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        create_tag(USER1, TAG1)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        upload_pteam_tags(
            USER1, self.pteam1.pteam_id, GROUP1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True
        )
        self.ateam1 = create_ateam(USER1, ATEAM1)

    def _get_summary(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        sort_key: Optional[schemas.TopicSortKey] = None,
    ) -> dict:
        params: Dict[str, Union[str, int]] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if sort_key is not None:
            params["sort_key"] = sort_key.value
        return assert_200(
            client.get(
                f"/ateams/{self.ateam1.ateam_id}/topicstatus", headers=headers(USER1), params=params
            )
        )

    def _assert_nums(
        self,
        data_: dict,
        expected_num_topics: int,
        expected_offset: int,
        expected_limit: int,
        expected_len_statuses: int,
    ):
        assert data_["num_topics"] == expected_num_topics
        assert data_["offset"] == expected_offset
        assert data_["limit"] == expected_limit
        assert len(data_["topic_statuses"]) == expected_len_statuses

    def _assert_topic_is(self, topic_status_: dict, topic_: schemas.TopicCreateResponse):
        assert UUID(topic_status_["topic_id"]) == topic_.topic_id
        assert topic_status_["title"] == topic_.title
        assert topic_status_["threat_impact"] == topic_.threat_impact
        assert datetime.fromisoformat(topic_status_["updated_at"]) == topic_.updated_at

    def test_default_behavior_without_topics(self):
        data = self._get_summary()
        self._assert_nums(data, 0, self.default_offset, self.default_limit, 0)
        assert data["search"] == self.default_search
        assert data["sort_key"] == self.default_sort_key

    def test_returns_given_params(self):
        data = self._get_summary(offset=3)
        self._assert_nums(data, 0, 3, self.default_limit, 0)
        data = self._get_summary(limit=5)
        self._assert_nums(data, 0, self.default_offset, 5, 0)
        data = self._get_summary(offset=4, limit=6)
        self._assert_nums(data, 0, 4, 6, 0)
        data = self._get_summary(search="word1")
        assert data["search"] == "word1"
        data = self._get_summary(sort_key=schemas.TopicSortKey.UPDATED_AT_DESC)
        assert data["sort_key"] == schemas.TopicSortKey.UPDATED_AT_DESC

    def test_ignore_empty_search(self):
        data = self._get_summary(search="")
        assert data["search"] == self.default_search

    @pytest.fixture(scope="function", name="topics")
    def create_4topics(self):
        # PTEAM1 joins
        watching_request1 = create_watching_request(USER1, self.ateam1.ateam_id)
        accept_watching_request(USER1, watching_request1.request_id, self.pteam1.pteam_id)

        # create 4 topics on unsorted order
        topic2 = create_topic(USER1, {**TOPIC2, "threat_impact": 2, "tags": [TAG1]})
        topic4 = create_topic(USER1, {**TOPIC4, "threat_impact": 3, "tags": [TAG1]})
        topic1 = create_topic(USER1, {**TOPIC1, "threat_impact": 1, "tags": [TAG1]})
        topic3 = create_topic(USER1, {**TOPIC3, "threat_impact": 3, "tags": [TAG1]})

        return [topic1, topic2, topic3, topic4]

    def test_default_behavior(self, topics):
        data = self._get_summary()
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        # default sort_key is threat_impact + updated_at_desc
        assert data["sort_key"] == schemas.TopicSortKey.THREAT_IMPACT
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])  # created after topic4
        self._assert_topic_is(data["topic_statuses"][3], topics[3])

    def test_offset(self, topics):
        data = self._get_summary(offset=1)
        self._assert_nums(data, 4, 1, self.default_limit, 3)
        # topics[0] omitted by offset
        self._assert_topic_is(data["topic_statuses"][0], topics[1])
        self._assert_topic_is(data["topic_statuses"][1], topics[2])
        self._assert_topic_is(data["topic_statuses"][2], topics[3])

        data = self._get_summary(offset=3)
        self._assert_nums(data, 4, 3, self.default_limit, 1)
        # topics[0,1,2] omitted by offset
        self._assert_topic_is(data["topic_statuses"][0], topics[3])

        data = self._get_summary(offset=4)
        self._assert_nums(data, 4, 4, self.default_limit, 0)  # all topics omitted by offset

        data = self._get_summary(offset=5)
        self._assert_nums(data, 4, 5, self.default_limit, 0)  # all topics omitted by offset

    def test_limit(self, topics):
        data = self._get_summary(limit=1)
        self._assert_nums(data, 4, self.default_offset, 1, 1)
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        # topics[1,2,3] omitted by limit

        data = self._get_summary(limit=3)
        self._assert_nums(data, 4, self.default_offset, 3, 3)
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])
        # topics[3] omitted by limit

        data = self._get_summary(limit=4)
        self._assert_nums(data, 4, self.default_offset, 4, 4)
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])
        self._assert_topic_is(data["topic_statuses"][3], topics[3])

        # limit 5
        data = self._get_summary(limit=5)
        self._assert_nums(data, 4, self.default_offset, 5, 4)
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])
        self._assert_topic_is(data["topic_statuses"][3], topics[3])

    def test_offset_and_limit(self, topics):
        data = self._get_summary(offset=1, limit=1)
        self._assert_nums(data, 4, 1, 1, 1)
        # topics[0] omitted by offset
        self._assert_topic_is(data["topic_statuses"][0], topics[1])
        # topics[2,3] omitted by limit

        data = self._get_summary(offset=2, limit=2)
        self._assert_nums(data, 4, 2, 2, 2)
        # topics[0,1] omitted by offset
        self._assert_topic_is(data["topic_statuses"][0], topics[2])
        self._assert_topic_is(data["topic_statuses"][1], topics[3])

        data = self._get_summary(offset=3, limit=3)
        self._assert_nums(data, 4, 3, 3, 1)
        # topics[0,1,2] omitted by offset
        self._assert_topic_is(data["topic_statuses"][0], topics[3])

        data = self._get_summary(offset=4, limit=4)
        self._assert_nums(data, 4, 4, 4, 0)  # all topics omitted by offset

    def test_search(self, topics):
        data = self._get_summary(search="topic")
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["search"] == "topic"
        self._assert_topic_is(data["topic_statuses"][0], topics[0])  # "topic one"
        self._assert_topic_is(data["topic_statuses"][1], topics[1])  # "topic two"
        self._assert_topic_is(data["topic_statuses"][2], topics[2])  # "topic three"
        self._assert_topic_is(data["topic_statuses"][3], topics[3])  # "topic four"

        data = self._get_summary(search="one")
        self._assert_nums(data, 1, self.default_offset, self.default_limit, 1)
        assert data["search"] == "one"
        self._assert_topic_is(data["topic_statuses"][0], topics[0])  # "topic one"

        data = self._get_summary(search="topic t")
        self._assert_nums(data, 2, self.default_offset, self.default_limit, 2)
        assert data["search"] == "topic t"
        self._assert_topic_is(data["topic_statuses"][0], topics[1])  # "topic two"
        self._assert_topic_is(data["topic_statuses"][1], topics[2])  # "topic three"

        # case insensitive
        data = self._get_summary(search="TOPIC t")
        self._assert_nums(data, 2, self.default_offset, self.default_limit, 2)
        assert data["search"] == "TOPIC t"
        self._assert_topic_is(data["topic_statuses"][0], topics[1])  # "topic two"
        self._assert_topic_is(data["topic_statuses"][1], topics[2])  # "topic three"

        # wildcard does not work (auto escape enabled)
        data = self._get_summary(search="%")
        self._assert_nums(data, 0, self.default_offset, self.default_limit, 0)
        assert data["search"] == "%"

        data = self._get_summary(search="_")
        self._assert_nums(data, 0, self.default_offset, self.default_limit, 0)
        assert data["search"] == "_"

    def test_actually_ignored_empty_search(self, topics):
        data = self._get_summary(search="")
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["search"] == self.default_search
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])
        self._assert_topic_is(data["topic_statuses"][3], topics[3])

    def test_sort_key(self, topics):
        assert (
            topics[1].updated_at
            < topics[3].updated_at
            < topics[0].updated_at
            < topics[2].updated_at
        )

        data = self._get_summary(sort_key=schemas.TopicSortKey.THREAT_IMPACT)
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["sort_key"] == schemas.TopicSortKey.THREAT_IMPACT
        # secondary key is updated_at_desc
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[1])
        self._assert_topic_is(data["topic_statuses"][2], topics[2])
        self._assert_topic_is(data["topic_statuses"][3], topics[3])

        data = self._get_summary(sort_key=schemas.TopicSortKey.THREAT_IMPACT_DESC)
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["sort_key"] == schemas.TopicSortKey.THREAT_IMPACT_DESC
        # secondary key is updated_at_desc
        self._assert_topic_is(data["topic_statuses"][0], topics[2])
        self._assert_topic_is(data["topic_statuses"][1], topics[3])
        self._assert_topic_is(data["topic_statuses"][2], topics[1])
        self._assert_topic_is(data["topic_statuses"][3], topics[0])

        data = self._get_summary(sort_key=schemas.TopicSortKey.UPDATED_AT)
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["sort_key"] == schemas.TopicSortKey.UPDATED_AT
        # secondary key is threat_impact
        self._assert_topic_is(data["topic_statuses"][0], topics[1])
        self._assert_topic_is(data["topic_statuses"][1], topics[3])
        self._assert_topic_is(data["topic_statuses"][2], topics[0])
        self._assert_topic_is(data["topic_statuses"][3], topics[2])

        data = self._get_summary(sort_key=schemas.TopicSortKey.UPDATED_AT_DESC)
        self._assert_nums(data, 4, self.default_offset, self.default_limit, 4)
        assert data["sort_key"] == schemas.TopicSortKey.UPDATED_AT_DESC
        # secondary key is threat_impact
        self._assert_topic_is(data["topic_statuses"][0], topics[2])
        self._assert_topic_is(data["topic_statuses"][1], topics[0])
        self._assert_topic_is(data["topic_statuses"][2], topics[3])
        self._assert_topic_is(data["topic_statuses"][3], topics[1])

    def test_complex_cases(self, topics):
        data = self._get_summary(
            offset=1,
            limit=2,
            search="topic",
            sort_key=schemas.TopicSortKey.UPDATED_AT_DESC,
        )
        # topics[0,1,2,3] matches, sorted to [2,0,3,1], sliced to [0,3]
        self._assert_nums(data, 4, 1, 2, 2)
        assert data["search"] == "topic"
        assert data["sort_key"] == schemas.TopicSortKey.UPDATED_AT_DESC
        self._assert_topic_is(data["topic_statuses"][0], topics[0])
        self._assert_topic_is(data["topic_statuses"][1], topics[3])

        data = self._get_summary(
            offset=0,
            limit=3,
            search="e",
            sort_key=schemas.TopicSortKey.THREAT_IMPACT_DESC,
        )
        # topics[0,2] matches, sored to [2,0], sliced to [2,0]
        self._assert_nums(data, 2, self.default_offset, 3, 2)
        assert data["search"] == "e"
        assert data["sort_key"] == schemas.TopicSortKey.THREAT_IMPACT_DESC
        self._assert_topic_is(data["topic_statuses"][0], topics[2])
        self._assert_topic_is(data["topic_statuses"][1], topics[0])

        data = self._get_summary(offset=2, search="topic t")
        # topics[1,2] matches, sorted to [1,2], sliced to []
        self._assert_nums(data, 2, 2, self.default_limit, 0)
        assert data["search"] == "topic t"
        assert data["sort_key"] == schemas.TopicSortKey.THREAT_IMPACT


def test_topic_comment():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    ateam1 = create_ateam(USER1, ATEAM1)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER2, invitation.invitation_id)
    pteam1 = create_pteam(USER1, PTEAM1)  # TAG1
    topic1 = create_topic(USER1, TOPIC1)  # TAG1
    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)

    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 0

    # first comment by user1
    text1 = "test comment 1"
    request = {
        "comment": text1,
    }
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
            headers=headers(USER1),
            json=request,
        )
    )
    assert data["comment"] == text1
    assert UUID(data["comment_id"]) != UUID(int=0)
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert UUID(data["user_id"]) == user1.user_id
    assert data["email"] == USER1["email"]
    assert datetime.now() - datetime.fromisoformat(data["created_at"]) < timedelta(seconds=10)
    assert data["updated_at"] is None
    comment1 = {**data}

    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 1
    assert data[0] == comment1

    # second comment by user2
    text2 = "test comment 2"
    request = {
        "comment": text2,
    }
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
            headers=headers(USER2),
            json=request,
        )
    )
    assert data["comment"] == text2
    assert UUID(data["comment_id"]) != UUID(int=0)
    assert UUID(data["ateam_id"]) == ateam1.ateam_id
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert UUID(data["user_id"]) == user2.user_id
    assert data["email"] == USER2["email"]
    assert datetime.now() - datetime.fromisoformat(data["created_at"]) < timedelta(seconds=10)
    assert data["updated_at"] is None
    comment2 = {**data}

    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 2
    assert data[0] == comment2
    assert data[1] == comment1

    # edit comment1
    new_text1 = "test update comment 1"
    request = {
        "comment": new_text1,
    }
    data = assert_200(
        client.put(
            f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
            headers=headers(USER1),
            json=request,
        )
    )
    assert data["comment"] == new_text1
    assert datetime.now() - datetime.fromisoformat(data["updated_at"]) < timedelta(seconds=10)
    assert {**data, "comment": text1, "updated_at": None} == comment1
    new_comment1 = {**data}

    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 2
    assert data[0] == comment2  # sorted by created_at, not updated_at
    assert data[1] == new_comment1

    # delete comment2
    response = client.delete(
        f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment2["comment_id"]}',
        headers=headers(USER2),
    )
    assert response.status_code == 204

    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 1
    assert data[0] == new_comment1

    # purge pteam1
    response = client.delete(
        f"/ateams/{ateam1.ateam_id}/watching_pteams/{pteam1.pteam_id}", headers=headers(USER1)
    )
    assert response.status_code == 204

    # now ateam1 watches no pteam. however, getting (not bound topic's) comment is allowed.
    data = assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
        )
    )
    assert len(data) == 1
    assert data[0] == new_comment1


def test_topic_comment__errors():
    user1 = create_user(USER1)
    create_user(USER2)
    user3 = create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)  # TAG1
    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/",
            headers=headers(USER1),
            json={"comment": "test comment 1"},
        )
    )
    assert UUID(data["user_id"]) == user1.user_id
    assert data["email"] == USER1["email"]
    comment1 = {**data}

    # wrong ateam
    with pytest.raises(HTTPError, match=r"404: Not Found: No such ateam"):
        assert_200(
            client.get(
                f"/ateams/{user1.user_id}/topiccomment/{topic1.topic_id}", headers=headers(USER1)
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such ateam"):
        assert_200(
            client.post(
                f"/ateams/{user1.user_id}/topiccomment/{topic1.topic_id}",
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such ateam"):
        assert_200(
            client.put(
                f'/ateams/{user1.user_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such ateam"):
        assert_200(
            client.delete(
                f'/ateams/{user1.user_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER1),
            )
        )

    # wrong topic
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.get(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{user1.user_id}", headers=headers(USER1)
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{user1.user_id}",
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.put(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{user1.user_id}/{comment1["comment_id"]}',
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
        assert_200(
            client.delete(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{user1.user_id}/{comment1["comment_id"]}',
                headers=headers(USER1),
            )
        )

    # wrong comment
    with pytest.raises(HTTPError, match=r"404: Not Found: No such comment"):
        assert_200(
            client.put(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{user1.user_id}",
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such comment"):
        assert_200(
            client.delete(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{user1.user_id}",
                headers=headers(USER1),
            )
        )

    # not ateam member nor pteam member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(
            client.get(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER2)
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
                headers=headers(USER2),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not your comment"):
        assert_200(
            client.put(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER2),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER2),
            )
        )

    # not ateam member but pteam member
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(
            client.get(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER2)
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not an ateam member"):
        assert_200(
            client.post(
                f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
                headers=headers(USER2),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not your comment"):
        assert_200(
            client.put(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER2),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER2),
            )
        )

    # ateam member (not ADMIN)
    invitation = invite_to_ateam(USER1, ateam1.ateam_id)
    accept_ateam_invitation(USER3, invitation.invitation_id)
    assert_200(
        client.get(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}", headers=headers(USER3)
        )
    )
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
            headers=headers(USER3),
            json={"comment": "test comment 2"},
        )
    )
    assert UUID(data["user_id"]) == user3.user_id
    assert data["email"] == USER3["email"]
    comment2 = {**data}
    # another member's comment
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not your comment"):
        assert_200(
            client.put(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER3),
                json={"comment": "xxx"},
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment1["comment_id"]}',
                headers=headers(USER3),
            )
        )
    # own comment
    text2 = "test comment 2 updated"
    data = assert_200(
        client.put(
            f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment2["comment_id"]}',
            headers=headers(USER3),
            json={"comment": text2},
        )
    )
    assert data["comment_id"] == comment2["comment_id"]
    assert data["comment"] == text2
    response = client.delete(
        f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment2["comment_id"]}',
        headers=headers(USER3),
    )
    assert response.status_code == 204

    # ADMIN
    data = assert_200(
        client.post(
            f"/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}",
            headers=headers(USER3),
            json={"comment": "test comment 3"},
        )
    )
    assert UUID(data["user_id"]) == user3.user_id
    assert data["email"] == USER3["email"]
    comment3 = {**data}
    # only the comment writer can update it
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not your comment"):
        assert_200(
            client.put(
                f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment3["comment_id"]}',
                headers=headers(USER1),
                json={"comment": "xxx"},
            )
        )
    # ADMIN can delete other's comments
    response = client.delete(
        f'/ateams/{ateam1.ateam_id}/topiccomment/{topic1.topic_id}/{comment3["comment_id"]}',
        headers=headers(USER1),
    )
    assert response.status_code == 204
