import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import (
    DEFAULT_ALERT_THREAT_IMPACT,
    MEMBER_UUID,
    NOT_MEMBER_UUID,
    SYSTEM_EMAIL,
    SYSTEM_UUID,
    ZERO_FILLED_UUID,
)
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ATEAM1,
    EXT_TAG1,
    EXT_TAG2,
    EXT_TAG3,
    PTEAM1,
    PTEAM2,
    PTEAM3,
    PTEAM4,
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
    accept_pteam_invitation,
    accept_watching_request,
    assert_200,
    assert_204,
    compare_references,
    compare_tags,
    create_action,
    create_actionlog,
    create_ateam,
    create_pteam,
    create_tag,
    create_topic,
    create_topicstatus,
    create_user,
    create_watching_request,
    file_upload_headers,
    get_pteam_groups,
    get_pteam_tags,
    headers,
    invite_to_pteam,
    schema_to_dict,
    to_datetime,
    upload_pteam_tags,
)

client = TestClient(app)


def test_get_pteams():
    create_user(USER1)

    response = client.get("/pteams", headers=headers(USER1))
    assert response.status_code == 200
    assert response.json() == []

    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/pteams", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pteam_id"] == str(pteam1.pteam_id)
    assert data[0]["pteam_name"] == PTEAM1["pteam_name"]
    assert data[0]["contact_info"] == PTEAM1["contact_info"]


def test_get_pteams__without_auth():
    response = client.get("/pteams")  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_get_pteams__by_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get("/pteams", headers=headers(USER2))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pteam_id"] == str(pteam1.pteam_id)
    assert data[0]["pteam_name"] == PTEAM1["pteam_name"]
    assert data[0]["contact_info"] == PTEAM1["contact_info"]


def test_get_pteams__by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/pteams", headers=headers(USER2))  # not a member
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pteam_id"] == str(pteam1.pteam_id)
    assert data[0]["pteam_name"] == PTEAM1["pteam_name"]
    assert data[0]["contact_info"] == PTEAM1["contact_info"]
    assert "tag_name" not in data[0].keys()


def test_get_pteam():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["contact_info"] == PTEAM1["contact_info"]
    assert data["pteam_name"] == PTEAM1["pteam_name"]
    assert data["alert_slack"]["enable"] == PTEAM1["alert_slack"]["enable"]
    assert data["alert_slack"]["webhook_url"] == PTEAM1["alert_slack"]["webhook_url"]
    assert data["alert_mail"]["enable"] == PTEAM1["alert_mail"]["enable"]
    assert data["alert_mail"]["address"] == PTEAM1["alert_mail"]["address"]


def test_get_pteam__without_auth():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}")  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_get_pteam__by_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2))
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["contact_info"] == PTEAM1["contact_info"]
    assert data["pteam_name"] == PTEAM1["pteam_name"]
    assert data["alert_slack"]["enable"] == PTEAM1["alert_slack"]["enable"]
    assert data["alert_slack"]["webhook_url"] == PTEAM1["alert_slack"]["webhook_url"]


def test_get_pteam__by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2))  # not a member
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_create_pteam():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    assert pteam1.pteam_name == PTEAM1["pteam_name"]
    assert pteam1.contact_info == PTEAM1["contact_info"]
    assert pteam1.alert_slack.webhook_url == PTEAM1["alert_slack"]["webhook_url"]
    assert pteam1.alert_threat_impact == PTEAM1["alert_threat_impact"]
    assert pteam1.pteam_id != ZERO_FILLED_UUID

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    user_me = response.json()
    assert {UUID(pteam["pteam_id"]) for pteam in user_me["pteams"]} == {pteam1.pteam_id}

    pteam2 = create_pteam(USER1, PTEAM2)
    assert pteam2.pteam_name == PTEAM2["pteam_name"]
    assert pteam2.contact_info == PTEAM2["contact_info"]
    assert pteam2.alert_slack.webhook_url == PTEAM2["alert_slack"]["webhook_url"]
    assert pteam2.alert_threat_impact == PTEAM2["alert_threat_impact"]
    assert pteam2.pteam_id != ZERO_FILLED_UUID

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    user_me = response.json()
    assert {UUID(pteam["pteam_id"]) for pteam in user_me["pteams"]} == {
        pteam1.pteam_id,
        pteam2.pteam_id,
    }


def test_create_pteam__by_default():
    create_user(USER1)
    _pteam = PTEAM1.copy()
    del _pteam["contact_info"]
    del _pteam["alert_slack"]
    del _pteam["alert_threat_impact"]
    del _pteam["alert_mail"]
    pteam1 = create_pteam(USER1, _pteam)
    assert pteam1.contact_info == ""
    assert pteam1.alert_slack.enable is True
    assert pteam1.alert_slack.webhook_url == ""
    assert pteam1.alert_threat_impact == DEFAULT_ALERT_THREAT_IMPACT
    assert pteam1.alert_mail.enable is True
    assert pteam1.alert_mail.address == ""


def test_create_pteam__without_auth():
    create_user(USER1)
    request = {**PTEAM1}
    response = client.post("/pteams", json=request)  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_create_pteam__duplicate():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER1, PTEAM1)
    assert pteam1.pteam_id != pteam2.pteam_id
    del pteam1.pteam_id, pteam2.pteam_id
    assert pteam1 == pteam2


def test_update_pteam():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = schemas.PTeamUpdateRequest(**PTEAM2).model_dump()
    response = client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_name"] == PTEAM2["pteam_name"]
    assert data["contact_info"] == PTEAM2["contact_info"]
    assert data["alert_slack"]["enable"] == PTEAM2["alert_slack"]["enable"]
    assert data["alert_slack"]["webhook_url"] == PTEAM2["alert_slack"]["webhook_url"]
    assert data["alert_threat_impact"] == PTEAM2["alert_threat_impact"]
    assert data["alert_mail"]["enable"] == PTEAM2["alert_mail"]["enable"]
    assert data["alert_mail"]["address"] == PTEAM2["alert_mail"]["address"]


def test_update_pteam__by_admin():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["admin"])
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = schemas.PTeamUpdateRequest(**PTEAM2).model_dump()
    data = assert_200(
        client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2), json=request)
    )
    assert data["pteam_name"] == PTEAM2["pteam_name"]
    assert data["contact_info"] == PTEAM2["contact_info"]
    assert data["alert_slack"]["enable"] == PTEAM2["alert_slack"]["enable"]
    assert data["alert_slack"]["webhook_url"] == PTEAM2["alert_slack"]["webhook_url"]
    assert data["alert_threat_impact"] == PTEAM2["alert_threat_impact"]
    assert data["alert_mail"]["enable"] == PTEAM2["alert_mail"]["enable"]
    assert data["alert_mail"]["address"] == PTEAM2["alert_mail"]["address"]


def test_update_pteam__by_not_admin():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = schemas.PTeamUpdateRequest(**PTEAM2).model_dump()
    response = client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER2), json=request)
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_update_pteam_empty_data():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    empty_data = {
        "pteam_name": "",
        "contact_info": "",
        "alert_slack": {"enable": False, "webhook_url": ""},
    }

    request = schemas.PTeamUpdateRequest(**{**empty_data}).model_dump()
    response = client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_name"] == ""
    assert data["contact_info"] == ""
    assert data["alert_slack"]["webhook_url"] == ""
    assert data["alert_threat_impact"] == 3


def test_get_pteam_groups():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER1, PTEAM2)
    create_tag(USER1, TAG1)

    # no groups at created pteam
    groups1 = get_pteam_groups(USER1, pteam1.pteam_id)
    groups2 = get_pteam_groups(USER1, pteam2.pteam_id)
    assert groups1.groups == groups2.groups == []

    refs0 = {TAG1: [("fake target", "fake version")]}

    # add group x to pteam1
    group_x = "group_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    groups1a = get_pteam_groups(USER1, pteam1.pteam_id)
    groups2a = get_pteam_groups(USER1, pteam2.pteam_id)
    assert groups1a.groups == [group_x]
    assert groups2a.groups == []

    # add group y to pteam2
    group_y = "group_y"
    upload_pteam_tags(USER1, pteam2.pteam_id, group_y, refs0)

    groups1b = get_pteam_groups(USER1, pteam1.pteam_id)
    groups2b = get_pteam_groups(USER1, pteam2.pteam_id)
    assert groups1b.groups == [group_x]
    assert groups2b.groups == [group_y]

    # add group y to pteam1
    upload_pteam_tags(USER1, pteam1.pteam_id, group_y, refs0)

    groups1c = get_pteam_groups(USER1, pteam1.pteam_id)
    groups2c = get_pteam_groups(USER1, pteam2.pteam_id)
    assert set(groups1c.groups) == {group_x, group_y}
    assert groups2c.groups == [group_y]

    # only members get groups
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        get_pteam_groups(USER2, pteam1.pteam_id)


def test_get_pteam_tags():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)

    # no tags at created pteam
    etags0 = get_pteam_tags(USER1, pteam1.pteam_id)
    assert etags0 == []

    # add tag1 to pteam1
    group_x = "group_x"
    refs1 = {tag1.tag_name: [("fake target", "fake version")]}
    expected_ref1 = [
        {"group": group_x, "target": "fake target", "version": "fake version"},
    ]
    etags1a = upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs1)

    assert len(etags1a) == 1
    assert compare_tags(etags1a, [tag1])
    assert compare_references(etags1a[0].references, expected_ref1)

    etags1b = get_pteam_tags(USER1, pteam1.pteam_id)
    assert len(etags1b) == 1
    assert compare_tags(etags1b, [tag1])
    assert compare_references(etags1b[0].references, expected_ref1)

    # add tag2 to pteam1
    group_y = "group_y"
    refs2 = {tag2.tag_name: [("fake target 2", "fake version 2")]}
    expected_ref2 = [
        {"group": group_y, "target": "fake target 2", "version": "fake version 2"},
    ]
    etags2a = upload_pteam_tags(USER1, pteam1.pteam_id, group_y, refs2)

    assert len(etags2a) == 2
    assert compare_tags(etags2a, sorted([tag1, tag2], key=lambda x: x.tag_name))
    if compare_tags([etags2a[0]], [tag1]):
        assert compare_references(etags2a[0].references, expected_ref1)
        assert compare_references(etags2a[1].references, expected_ref2)
    else:
        assert compare_references(etags2a[1].references, expected_ref1)
        assert compare_references(etags2a[0].references, expected_ref2)

    # only members get tags
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        get_pteam_tags(USER2, pteam1.pteam_id)


def test_get_pteam_tags__by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/tags", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_update_pteam_auth(testdb):
    # access to testdb directly to check auth modified by side effects.

    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    # initial values
    row_user1 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user1.user_id),
        )
        .one()
    )
    assert row_user1.authority == models.PTeamAuthIntFlag.PTEAM_MASTER  # pteam master
    row_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_member:
        assert row_member.authority == models.PTeamAuthIntFlag.PTEAM_MEMBER  # pteam member
    row_not_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_not_member:
        assert row_not_member.authority == models.PTeamAuthIntFlag.FREE_TEMPLATE  # not member

    # on invitation
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status", "invite"]))
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, request_auth)  # invite with auth
    accept_pteam_invitation(USER2, invitation.invitation_id)
    row_user2 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.PTeamAuthIntFlag.from_enums(request_auth)

    # update auth
    request_auth = list(map(models.PTeamAuthEnum, ["invite", "admin"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_auth,
        }
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user2.user_id)
    assert set(data[0]["authorities"]) == set(request_auth)
    row_user2 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.PTeamAuthIntFlag.from_enums(request_auth)


def test_update_pteam_auth__without_auth(testdb):
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    row_user1 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user1.user_id),
        )
        .one()
    )
    assert row_user1.authority & models.PTeamAuthIntFlag.ADMIN

    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": None,
        }
    ]
    response = client.post(f"/pteams/{pteam1.pteam_id}/authority", json=request)  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_update_pteam_auth__without_authority():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    # invite another as ADMIN (removing last ADMIN is not allowed)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["admin"])
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # remove ADMIN from user1
    request_auth = list(map(models.PTeamAuthEnum, ["invite"]))
    request = [
        {
            "user_id": str(user1.user_id),
            "authorities": request_auth,
        }
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(request)
    assert data[0]["user_id"] == str(user1.user_id)
    assert set(data[0]["authorities"]) == set(request_auth)

    # update without authority
    request_auth = list(map(models.PTeamAuthEnum, ["admin"]))
    request = [
        {
            "user_id": str(user1.user_id),
            "authorities": request_auth,
        }
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_update_pteam_auth__pseudo_uuid(testdb):
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # initial values
    row_user1 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user1.user_id),
        )
        .one()
    )
    assert row_user1.authority == models.PTeamAuthIntFlag.PTEAM_MASTER  # pteam master
    row_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_member:
        assert row_member.authority == models.PTeamAuthIntFlag.PTEAM_MEMBER  # pteam member
    row_not_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_not_member:
        assert row_not_member.authority == models.PTeamAuthIntFlag.FREE_TEMPLATE  # not member

    # update MEMBER & NOT_MEMBER
    member_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    not_member_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": member_auth},
        {"user_id": str(NOT_MEMBER_UUID), "authorities": not_member_auth},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    resp_map = {x["user_id"]: x for x in response.json()}
    resp_member = resp_map[str(MEMBER_UUID)]
    assert set(resp_member["authorities"]) == set(member_auth)
    resp_not_member = resp_map[str(NOT_MEMBER_UUID)]
    assert set(resp_not_member["authorities"]) == set(not_member_auth)
    row_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one()
    )
    assert row_member.authority == models.PTeamAuthIntFlag.from_enums(member_auth)
    row_not_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one()
    )
    assert row_not_member.authority == models.PTeamAuthIntFlag.from_enums(not_member_auth)


def test_update_pteam_auth__not_member(testdb):
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    # before joining
    row_user2 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user2.user_id),
        )
        .one_or_none()
    )
    assert row_user2 is None

    # give auth to not member
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = [
        {
            "user_id": str(user2.user_id),
            "authorities": request_auth,
        }
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    # invite to pteam
    request_auth2 = list(map(models.PTeamAuthEnum, ["topic_status", "invite"]))
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, request_auth2)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    row_user2 = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(user2.user_id),
        )
        .one()
    )
    assert row_user2.authority == models.PTeamAuthIntFlag.from_enums(request_auth2)


def test_update_pteam_auth__pseudo(testdb):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    row_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_member:
        assert row_member.authority == models.PTeamAuthIntFlag.PTEAM_MEMBER
    row_not_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    if row_not_member:
        assert row_not_member.authority == models.PTeamAuthIntFlag.FREE_TEMPLATE

    member_auth = list(map(models.PTeamAuthEnum, ["invite", "topic_status"]))
    not_member_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": member_auth},
        {"user_id": str(NOT_MEMBER_UUID), "authorities": not_member_auth},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    auth_map = {x["user_id"]: x["authorities"] for x in response.json()}
    assert set(auth_map[str(MEMBER_UUID)]) == set(member_auth)
    assert set(auth_map[str(NOT_MEMBER_UUID)]) == set(not_member_auth)

    row_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(MEMBER_UUID),
        )
        .one_or_none()
    )
    assert row_member.authority == models.PTeamAuthIntFlag.from_enums(member_auth)
    row_not_member = (
        testdb.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam1.pteam_id),
            models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID),
        )
        .one_or_none()
    )
    assert row_not_member.authority == models.PTeamAuthIntFlag.from_enums(not_member_auth)


def test_update_pteam_auth__pseudo_admin():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(MEMBER_UUID), "authorities": ["admin"]}],
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(NOT_MEMBER_UUID), "authorities": ["admin"]}],
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"


def test_update_pteam_auth__remove_admin__last():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # remove last admin
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


def test_update_pteam_auth__remove_admin__another():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    # invite another admin
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["admin"])
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # try removing (no more last) admin
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["authorities"] == []

    # come back admin
    request = [
        {"user_id": str(user1.user_id), "authorities": ["admin"]},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER2), json=request
    )
    assert response.status_code == 200

    # remove all admins
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


def test_update_pteam_auth__swap_admin():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = [
        {"user_id": str(user1.user_id), "authorities": []},  # retire ADMIN
        {"user_id": str(user2.user_id), "authorities": ["admin"]},  # be ADMIN
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(request)
    auth_map = {x["user_id"]: x for x in data}
    old_admin = auth_map.get(str(user1.user_id))
    assert old_admin["authorities"] == []
    new_admin = auth_map.get(str(user2.user_id))
    assert new_admin["authorities"] == ["admin"]


def test_get_pteam_auth():
    user1 = create_user(USER1)  # master
    user2 = create_user(USER2)  # member
    create_user(USER3)  # not member
    pteam1 = create_pteam(USER1, PTEAM1)
    invite_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, invite_auth)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # set pteam auth
    member_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    not_member_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = [
        {"user_id": str(MEMBER_UUID), "authorities": member_auth},
        {"user_id": str(NOT_MEMBER_UUID), "authorities": not_member_auth},
    ]
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1), json=request
    )
    assert response.status_code == 200

    # get by master -> all member's auth & members auth
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1))
    assert response.status_code == 200
    auth_map = {x["user_id"]: x["authorities"] for x in response.json()}
    assert set(auth_map.keys()) == set(
        map(str, [user1.user_id, user2.user_id, MEMBER_UUID, NOT_MEMBER_UUID])
    )
    assert set(auth_map[str(user1.user_id)]) == set(
        models.PTeamAuthIntFlag(models.PTeamAuthIntFlag.PTEAM_MASTER).to_enums()
    )
    assert set(auth_map.get(str(user2.user_id))) == set(invite_auth)
    assert set(auth_map.get(str(MEMBER_UUID))) == set(member_auth)
    assert set(auth_map.get(str(NOT_MEMBER_UUID))) == set(not_member_auth)

    # get by member -> all member's auth & members auth
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER2))
    assert response.status_code == 200
    auth_map = {x["user_id"]: x["authorities"] for x in response.json()}
    assert set(auth_map.keys()) == set(
        map(str, [user1.user_id, user2.user_id, MEMBER_UUID, NOT_MEMBER_UUID])
    )
    assert set(auth_map[str(user1.user_id)]) == set(
        models.PTeamAuthIntFlag(models.PTeamAuthIntFlag.PTEAM_MASTER).to_enums()
    )
    assert set(auth_map.get(str(user2.user_id))) == set(invite_auth)
    assert set(auth_map.get(str(MEMBER_UUID))) == set(member_auth)
    assert set(auth_map.get(str(NOT_MEMBER_UUID))) == set(not_member_auth)

    # get by not member -> not-member auth only
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER3))
    assert response.status_code == 200
    auth_map = {x["user_id"]: x["authorities"] for x in response.json()}
    assert set(auth_map.keys()) == set(map(str, [NOT_MEMBER_UUID]))
    assert set(auth_map.get(str(NOT_MEMBER_UUID))) == set(not_member_auth)


def test_get_pteam_auth__without_auth():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/authority")  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_pteam_auth_effects__indivudual():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # no INVITE
    accept_pteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match="403: Forbidden"):
        invite_to_pteam(USER2, pteam1.pteam_id)

    # give INVITE
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(user2.user_id), "authorities": ["invite"]}],
    )
    assert response.status_code == 200

    # try again
    invitation = invite_to_pteam(USER2, pteam1.pteam_id)
    assert invitation.invitation_id != ZERO_FILLED_UUID


def test_pteam_auth_effects__pseudo_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # no INVITE
    accept_pteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match="403: Forbidden"):
        invite_to_pteam(USER2, pteam1.pteam_id)

    # give INVITE to MEMBER
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(MEMBER_UUID), "authorities": ["invite"]}],
    )
    assert response.status_code == 200

    # try again
    invitation = invite_to_pteam(USER2, pteam1.pteam_id)
    assert invitation.invitation_id != ZERO_FILLED_UUID


def test_pteam_auth_effects__pseudo_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # no INVITE
    accept_pteam_invitation(USER2, invitation.invitation_id)

    with pytest.raises(HTTPError, match="403: Forbidden"):
        invite_to_pteam(USER2, pteam1.pteam_id)

    # give INVITE to NOT_MEMBER. it is also applied to members.
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(NOT_MEMBER_UUID), "authorities": ["invite"]}],
    )
    assert response.status_code == 200

    # try again
    invitation = invite_to_pteam(USER2, pteam1.pteam_id)
    assert invitation.invitation_id != ZERO_FILLED_UUID


def test_create_invitation():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)  # master have INVITE & ADMIN

    request_auth = list(map(models.PTeamAuthEnum, ["invite"]))
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": request_auth,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] == request["limit_count"]
    assert set(data["authorities"]) == set(request["authorities"])


def test_create_invitation__without_authorities():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["topic_status"])  # no INVITE
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # try without INVITE
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": None,  # no authorities
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # give INVITE
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(user2.user_id), "authorities": ["invite"]}],
    )
    assert response.status_code == 200

    # try again with INVITE
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] == request["limit_count"]
    assert data["authorities"] == []

    # try giving authorities only with INVITE (no ADMIN)
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": request_auth,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    # give INVITE & ADMIN
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(user2.user_id), "authorities": ["invite", "admin"]}],
    )
    assert response.status_code == 200

    # try again with INVITE & ADMIN
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2), json=request
    )
    assert response.status_code == 200
    data = response.json()
    assert datetime.fromisoformat(data["expiration"]) == datetime.fromisoformat(
        request["expiration"]
    )
    assert data["limit_count"] == request["limit_count"]
    assert set(data["authorities"]) == set(request["authorities"])


def test_create_invitation__by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_pteam(USER2, PTEAM2)

    # user2 is ADMIN of another pteam.
    request_auth = list(map(models.PTeamAuthEnum, ["invite"]))
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": request_auth,
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
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 0,  # out of limit
        "authorities": request_auth,
    }
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    # past date
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    request = {
        "expiration": str(datetime(2000, 1, 1, 0, 0, 0, 0)),  # past date
        "limit_count": 1,
        "authorities": request_auth,
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


def test_list_invitations():
    create_user(USER1)  # master, have INVITE & ADMIN
    create_user(USER2)  # member, not have INVITE
    create_user(USER3)  # member, have INVITE
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["invite"])
    accept_pteam_invitation(USER3, invitation.invitation_id)

    # create invitation
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status"]))
    invitation1 = invite_to_pteam(USER1, pteam1.pteam_id, request_auth)

    # get by master
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER1))
    assert response.status_code == 200
    assert len(response.json()) == 1  # invitation0 should be expired
    data = schemas.PTeamInvitationResponse(**response.json()[0])
    assert data.invitation_id == invitation1.invitation_id
    assert data.pteam_id == pteam1.pteam_id
    assert data.expiration == invitation1.expiration
    assert data.limit_count == invitation1.limit_count
    assert data.used_count == invitation1.used_count == 0
    assert set(data.authorities) == set(request_auth)

    # get without INVITE
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # get with INVITE, without ADMIN
    response = client.get(f"/pteams/{pteam1.pteam_id}/invitation", headers=headers(USER3))
    assert response.status_code == 200
    assert len(response.json()) == 1  # invitation0 should be expired
    data = schemas.PTeamInvitationResponse(**response.json()[0])
    assert data.invitation_id == invitation1.invitation_id
    assert data.pteam_id == pteam1.pteam_id
    assert data.expiration == invitation1.expiration
    assert data.limit_count == invitation1.limit_count
    assert data.used_count == invitation1.used_count == 0
    assert set(data.authorities) == set(request_auth)


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

    # delete by pteam member without INVITE
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # no INVITE
    accept_pteam_invitation(USER3, invitation.invitation_id)
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/invitation/{target_invitation.invitation_id}",
        headers=headers(USER2),
    )
    assert response.status_code == 403

    # delete by pteam member with INVITE
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(user3.user_id), "authorities": ["invite"]}],
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
    pteams = response.json()["pteams"]
    assert len(pteams) == 0
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1))
    auth_map = {x["user_id"]: x for x in response.json()}
    assert auth_map.get(str(user2.user_id)) is None

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    assert set(x["user_id"] for x in members) == set(str(x.user_id) for x in [user1, user2])
    response = client.get("/users/me", headers=headers(USER2))
    assert response.status_code == 200
    pteams = response.json()["pteams"]
    assert {UUID(pteam["pteam_id"]) for pteam in pteams} == {x.pteam_id for x in [pteam1]}
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1))
    auth_map = {x["user_id"]: x for x in response.json()}
    assert auth_map.get(str(user2.user_id)) is None  # no individual auth


def test_apply_invitation__individual_auth():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    request_auth = list(map(models.PTeamAuthEnum, ["topic_status", "invite"]))

    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1))
    auth_map = {x["user_id"]: x for x in response.json()}
    assert auth_map.get(str(user2.user_id)) is None

    invitation = invite_to_pteam(USER1, pteam1.pteam_id, request_auth)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER1))
    auth_map = {x["user_id"]: x for x in response.json()}
    assert set(auth_map.get(str(user2.user_id), {}).get("authorities", [])) == set(request_auth)


def test_delete_member__last_admin():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user1.user_id)
    assert {UUID(pteam["pteam_id"]) for pteam in data["pteams"]} == {pteam1.pteam_id}

    # try leaving the pteam
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


def test_delete_member__last_admin_another():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user1.user_id)
    assert {UUID(pteam["pteam_id"]) for pteam in data["pteams"]} == {pteam1.pteam_id}

    # invite another member (not ADMIN)
    create_user(USER2)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # try leaving the pteam
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


def test_delete_member__not_last_admin():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user1.user_id)
    assert {UUID(pteam["pteam_id"]) for pteam in data["pteams"]} == {pteam1.pteam_id}

    # invite another member (not ADMIN)
    user2 = create_user(USER2)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # make the other member ADMIN
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(user2.user_id), "authorities": ["admin"]}],
    )
    assert response.status_code == 200

    # try leaving pteam
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER1)
    )
    assert response.status_code == 204

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user1.user_id)
    assert data["pteams"] == []

    # lost extra authorities on leaving.
    response = client.get(f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER2))
    assert response.status_code == 200
    auth_map = {x["user_id"]: x for x in response.json()}
    assert auth_map.get(str(user1.user_id)) is None


def test_delete_member__by_admin():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["admin", "invite"])
    accept_pteam_invitation(USER3, invitation.invitation_id)

    # kickout the other ADMIN
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 204

    # kickout member
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 204

    # kickout myself
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


def test_delete_member__by_admin_myself():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    # invite another ADMIN
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["admin"])
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # kickout myself
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER2)
    )
    assert response.status_code == 204


def test_delete_member__by_not_admin():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)

    # kickout ADMIN
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # kickout another member
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"

    # kickout myself
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}", headers=headers(USER3)
    )
    assert response.status_code == 204


def test_get_pteam_members():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 1
    keys = ["user_id", "uid", "email", "disabled", "years"]
    for key in keys:
        assert str(members[0].get(key)) == str(getattr(user1, key))
    assert {UUID(pteam["pteam_id"]) for pteam in members[0]["pteams"]} == {pteam1.pteam_id}

    user2 = create_user(USER2)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER1))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    members_map = {UUID(x["user_id"]): x for x in members}
    keys = ["user_id", "uid", "email", "disabled", "years"]
    for key in keys:
        assert str(members_map.get(user1.user_id).get(key)) == str(getattr(user1, key))
        assert str(members_map.get(user2.user_id).get(key)) == str(getattr(user2, key))
    assert (
        {UUID(p["pteam_id"]) for p in members_map.get(user1.user_id).get("pteams", [])}
        == {UUID(p["pteam_id"]) for p in members_map.get(user2.user_id).get("pteams", [])}
        == {pteam1.pteam_id}
    )


def test_get_pteam_members__by_member():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER2))
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    members_map = {UUID(x["user_id"]): x for x in members}
    keys = ["user_id", "uid", "email", "disabled", "years"]
    for key in keys:
        assert str(members_map.get(user1.user_id).get(key)) == str(getattr(user1, key))
        assert str(members_map.get(user2.user_id).get(key)) == str(getattr(user2, key))
    assert (
        {UUID(p["pteam_id"]) for p in members_map.get(user1.user_id).get("pteams", [])}
        == {UUID(p["pteam_id"]) for p in members_map.get(user2.user_id).get("pteams", [])}
        == {pteam1.pteam_id}
    )


def test_get_pteam_members__by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_set_pteam_topic_status():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)
    tag3 = create_tag(USER1, TAG3)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)  # assignees should be members
    accept_pteam_invitation(USER2, invitation.invitation_id)
    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name, tag3.parent_name]})

    # add tag1 + tag2 to pteam1
    group_x = "group_x"
    refs0 = {
        TAG1: [("fake target 1", "fake version 1")],
        TAG2: [("fake target 2", "fake version 2")],
    }
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    # set topicstatus
    json_data = {
        "topic_status": "acknowledged",
        "note": "acknowledged",
        "assignees": [str(x.user_id) for x in [user1, user2]],
        "scheduled_at": str(datetime(2023, 6, 1)),
    }
    responsed_topicstatus = create_topicstatus(
        USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data
    )
    assert responsed_topicstatus.topic_id == topic1.topic_id
    assert responsed_topicstatus.tag_id == tag1.tag_id
    assert responsed_topicstatus.topic_status == json_data["topic_status"]
    assert responsed_topicstatus.note == json_data["note"]
    assert responsed_topicstatus.user_id == user1.user_id
    assert set(map(str, responsed_topicstatus.assignees)) == set(json_data["assignees"])
    assert str(responsed_topicstatus.scheduled_at) == json_data["scheduled_at"]

    # set with mismatched tag
    with pytest.raises(HTTPError, match=r"400: Bad Request: Tag mismatch"):
        create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag2.tag_id, json_data)

    # set with not pteam tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag3.tag_id, json_data)


def test_set_pteam_topic_status__not_specify_assignee():
    user1 = create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    # set topicstatus
    json_data = {"topic_status": "acknowledged", "note": "acknowledged", "assignees": []}
    responsed_topicstatus = create_topicstatus(
        USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data
    )
    assert responsed_topicstatus.topic_id == topic1.topic_id
    assert responsed_topicstatus.tag_id == tag1.tag_id
    assert responsed_topicstatus.topic_status == json_data["topic_status"]
    assert responsed_topicstatus.note == json_data["note"]
    assert responsed_topicstatus.user_id == user1.user_id
    assert set(map(str, responsed_topicstatus.assignees)) == set(map(str, [user1.user_id]))


def test_set_pteam_topic_status__to_complete():
    user1 = create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION1])  # TAG1
    action1 = topic1.actions[0]

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    # create actionlogs
    actionlog1 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
    )
    actionlog2 = create_actionlog(
        USER1, action1.action_id, topic1.topic_id, user1.user_id, pteam1.pteam_id, None
    )

    # set topicstatus
    json_data = {
        "topic_status": "completed",
        "note": "",
        "logging_ids": [str(actionlog1.logging_id), str(actionlog2.logging_id)],
    }
    responsed_topicstatus = create_topicstatus(
        USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data
    )
    assert responsed_topicstatus.topic_id == topic1.topic_id
    assert responsed_topicstatus.tag_id == tag1.tag_id
    assert responsed_topicstatus.topic_status == json_data["topic_status"]
    assert responsed_topicstatus.note == json_data["note"]
    assert set(x.logging_id for x in responsed_topicstatus.action_logs) == set(
        map(UUID, json_data["logging_ids"])
    )
    assert responsed_topicstatus.user_id == user1.user_id


def test_set_pteam_topic_status__invalid_actionlog():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    # set topicstatus
    json_data = {
        "topic_status": "completed",
        "note": "completed",
        "logging_ids": [str(UUID(int=5))],
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request"):
        create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data)


def test_set_pteam_topic_status__with_unselectable_status():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    json_data = {"topic_status": "alerted", "note": "alerted"}
    with pytest.raises(HTTPError, match=r"400: Bad Request: Wrong topic status"):
        create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, json_data)


def test_set_pteam_topic_status__parent():
    create_user(USER1)
    tag_aaa = create_tag(USER1, "alpha1:alpha2:alpha3")
    tag_bbb = create_tag(USER1, "bravo1:bravo2:bravo3")
    tag_ccc = create_tag(USER1, "charlie1:charlie2:charlie3")
    tag_ddd = create_tag(USER1, "delta1:delta2:delta3")
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tags to pteam1
    group_x = "group_x"
    refs0 = {
        tag_aaa.tag_name: [("", "")],
        tag_bbb.tag_name: [("", "")],
        tag_ccc.parent_name: [("", "")],
        tag_ddd.parent_name: [("", "")],
    }
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    def _tags_summary() -> dict:
        return assert_200(
            client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
        )

    summary = _tags_summary()  # brief check summary
    assert summary["threat_impact_count"] == {"1": 0, "2": 0, "3": 0, "4": 4}

    topic1 = create_topic(USER1, {**TOPIC1, "topic_id": uuid4(), "tags": [tag_aaa.tag_name]})
    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 1, "2": 0, "3": 0, "4": 3}

    topic2 = create_topic(USER1, {**TOPIC1, "topic_id": uuid4(), "tags": [tag_bbb.parent_name]})
    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 2, "2": 0, "3": 0, "4": 2}

    # Note: topic3 does not match with pteam1
    topic3 = create_topic(USER1, {**TOPIC1, "topic_id": uuid4(), "tags": [tag_ccc.tag_name]})
    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 2, "2": 0, "3": 0, "4": 2}

    topic4 = create_topic(USER1, {**TOPIC1, "topic_id": uuid4(), "tags": [tag_ddd.parent_name]})
    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 3, "2": 0, "3": 0, "4": 1}

    def _status(topic_id, tag_id) -> dict:
        return assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/topicstatus/{topic_id}/{tag_id}", headers=headers(USER1)
            )
        )

    def _set_status(topic_id, tag_id, topic_status) -> dict:
        request = {
            "topic_status": topic_status,
            **({"scheduled_at": datetime.now()} if topic_status == "scheduled" else {}),
        }
        return assert_200(
            client.post(
                f"/pteams/{pteam1.pteam_id}/topicstatus/{topic_id}/{tag_id}",
                headers=headers(USER1),
                json=request,
            )
        )

    # watching child & child tagged topic
    st1 = _status(topic1.topic_id, tag_aaa.tag_id)
    assert st1["topic_id"] == str(topic1.topic_id)
    assert st1["pteam_id"] == str(pteam1.pteam_id)
    assert st1["tag_id"] == str(tag_aaa.tag_id)
    assert st1["topic_status"] is None
    # not watching parent
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _status(topic1.topic_id, tag_aaa.parent_id)
    # update status
    st1_1 = _set_status(topic1.topic_id, tag_aaa.tag_id, "completed")
    assert st1_1["topic_id"] == str(topic1.topic_id)
    assert st1_1["pteam_id"] == str(pteam1.pteam_id)
    assert st1_1["tag_id"] == str(tag_aaa.tag_id)
    assert st1_1["topic_status"] == "completed"
    # cannot update with not watching tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _set_status(topic1.topic_id, tag_aaa.parent_id, "completed")

    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 2, "2": 0, "3": 0, "4": 2}

    # watching child & parent tagged topic
    st2 = _status(topic2.topic_id, tag_bbb.tag_id)
    assert st2["topic_id"] == str(topic2.topic_id)
    assert st2["pteam_id"] == str(pteam1.pteam_id)
    assert st2["tag_id"] == str(tag_bbb.tag_id)
    assert st2["topic_status"] is None
    # not match parent
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _status(topic2.topic_id, tag_bbb.parent_id)
    # update with child tag on parent tagged topic
    st2_1 = _set_status(topic2.topic_id, tag_bbb.tag_id, "completed")
    assert st2_1["topic_id"] == str(topic2.topic_id)
    assert st2_1["pteam_id"] == str(pteam1.pteam_id)
    assert st2_1["tag_id"] == str(tag_bbb.tag_id)
    assert st2_1["topic_status"] == "completed"
    # cannot update with not watching tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _set_status(topic2.topic_id, tag_bbb.parent_id, "completed")

    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 1, "2": 0, "3": 0, "4": 3}

    # watching parent & child tagged topic
    # not watching child
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _status(topic3.topic_id, tag_ccc.tag_id)
    st3 = _status(topic3.topic_id, tag_ccc.parent_id)
    assert st3["topic_id"] == str(topic3.topic_id)
    assert st3["pteam_id"] == str(pteam1.pteam_id)
    assert st3["tag_id"] == str(tag_ccc.parent_id)
    assert st3["topic_status"] is None
    # update status
    # cannot update with not watching tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _set_status(topic2.topic_id, tag_ccc.tag_id, "completed")
    # cannot update with mismatched tag:  when topic.tag is c:c:c, pteam should have one of two,
    # c:c:c or the tag which parent is c:c:c (the latter is not happen).
    with pytest.raises(HTTPError, match=r"400: Bad Request: Tag mismatch"):
        _set_status(topic3.topic_id, tag_ccc.parent_id, "completed")

    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 1, "2": 0, "3": 0, "4": 3}

    # watching parent & parent tagged topic
    # not watching child
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _status(topic3.topic_id, tag_ddd.tag_id)
    st4 = _status(topic4.topic_id, tag_ddd.parent_id)
    assert st4["topic_id"] == str(topic4.topic_id)
    assert st4["pteam_id"] == str(pteam1.pteam_id)
    assert st4["tag_id"] == str(tag_ddd.parent_id)
    assert st4["topic_status"] is None
    # update status
    # cannot update with not watching tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _set_status(topic4.topic_id, tag_ddd.tag_id, "completed")
    st4_2 = _set_status(topic4.topic_id, tag_ddd.parent_id, "completed")
    assert st4_2["topic_id"] == str(topic4.topic_id)
    assert st4_2["pteam_id"] == str(pteam1.pteam_id)
    assert st4_2["tag_id"] == str(tag_ddd.parent_id)
    assert st4_2["topic_status"] == "completed"

    summary = _tags_summary()
    assert summary["threat_impact_count"] == {"1": 0, "2": 0, "3": 0, "4": 4}


def test_get_pteam_topics():
    user1 = create_user(USER1)
    create_user(USER2)
    create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER2))
    assert response.status_code == 200
    assert response.json() == []

    now = datetime.now()
    create_topic(USER1, TOPIC1, actions=[ACTION2, ACTION1])  # TAG1

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER2))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["topic_id"] == str(TOPIC1["topic_id"])
    assert data[0]["title"] == TOPIC1["title"]
    assert data[0]["abstract"] == TOPIC1["abstract"]
    assert data[0]["threat_impact"] == TOPIC1["threat_impact"]
    assert data[0]["created_by"] == str(user1.user_id)
    data0_created_at = datetime.fromisoformat(data[0]["created_at"])
    assert data0_created_at > now
    assert data0_created_at < now + timedelta(seconds=30)
    assert data[0]["created_at"] == data[0]["updated_at"]
    assert {x["tag_name"] for x in data[0]["tags"]} == set(TOPIC1["tags"])
    assert {x["tag_name"] for x in data[0]["misp_tags"]} == set(TOPIC1["misp_tags"])


def test_get_pteam_topics_with_topic_disabled():
    create_user(USER1)
    create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER1))
    assert response.status_code == 200
    assert response.json() == []

    create_topic(USER1, TOPIC1, actions=[ACTION2, ACTION1])  # TAG1
    create_topic(USER1, TOPIC2, actions=[ACTION2, ACTION1])  # TAG1

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["topic_id"] == str(TOPIC1["topic_id"])
    assert data[1]["topic_id"] == str(TOPIC2["topic_id"])

    request = {"disabled": True}
    response = client.put(f"/topics/{TOPIC1['topic_id']}", headers=headers(USER1), json=request)

    assert response.status_code == 200
    responsed_topic = schemas.TopicResponse(**response.json())
    assert responsed_topic.disabled is True

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["topic_id"] == str(TOPIC2["topic_id"])


def test_get_pteam_topics__by_not_member():
    create_user(USER1)
    create_user(USER2)
    create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_get_pteam_topic_status():
    user1 = create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    set_request = {
        "topic_status": models.TopicStatusType.acknowledged,
        "logging_ids": [],
        "assignees": [],
        "note": f"acknowledged by {USER1['email']}",
        "scheduled_at": None,
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, set_request)

    # get topicstatuses
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    responsed_topicstatuses = response.json()
    assert responsed_topicstatuses["pteam_id"] == str(pteam1.pteam_id)
    assert responsed_topicstatuses["topic_id"] == str(topic1.topic_id)
    assert responsed_topicstatuses["tag_id"] == str(tag1.tag_id)
    assert responsed_topicstatuses["user_id"] == str(user1.user_id)
    assert responsed_topicstatuses["topic_status"] == set_request["topic_status"]
    assert responsed_topicstatuses["note"] == set_request["note"]


def test_get_pteam_topic_status__by_not_member():
    create_user(USER1)
    create_user(USER2)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER2),
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_get_pteam_topic_statuses_summary():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tag1 to pteam1
    group_x = "group_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    # no topics
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tag_id"] == str(tag1.tag_id)
    assert data.get("topics") == []

    # a topic posted without no topic status
    topic2 = create_topic(USER1, TOPIC2)  # TAG1

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "alerted"
    assert data["topics"][0]["executed_at"] is None

    # add a unsolved status
    request = {
        "topic_status": models.TopicStatusType.acknowledged,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10

    # complete the topic
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "completed"
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10

    # add another topic
    topic1 = create_topic(USER1, TOPIC1)  # TAG1

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["topics"]) == 2
    assert topic1.threat_impact < topic2.threat_impact
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "alerted"
    assert data["topics"][0]["executed_at"] is None
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == "completed"

    # add a unsolved status
    request = {
        "topic_status": models.TopicStatusType.scheduled,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["topics"]) == 2
    assert topic1.threat_impact < topic2.threat_impact
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == "completed"

    # complete the topic
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tag_id"] == str(tag1.tag_id)
    assert topic1.threat_impact < topic2.threat_impact
    assert len(data["topics"]) == 2
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "completed"
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][1]["executed_at"]).timestamp() - now < 10


def test_get_pteam_topic_statuses_summary__parent():
    create_user(USER1)
    tag1 = create_tag(USER1, "alpha:alpha2:alpha3")
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tags to pteam1
    group_tc = "Threatconnectome"
    group_fs = "Flashsense"
    refs0 = {tag1.tag_name: [("api/Pipfile.lock", "1.3")]}
    refs1 = {tag1.tag_name: [("api2/Pipfile.lock", "1.4")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_tc, refs0)
    upload_pteam_tags(USER1, pteam1.pteam_id, group_fs, refs1)

    # no topics
    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert data["tag_id"] == str(tag1.tag_id)
    assert data.get("topics") == []

    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        data = assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.parent_id}",
                headers=headers(USER1),
            )
        )

    # a topic posted without no topic status
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [tag1.parent_name]})  # no action

    # topic2(parent tagged topic) listed on child tag, not on parent tag
    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "alerted"
    assert data["topics"][0]["executed_at"] is None

    # add a unsolved status
    request = {
        "topic_status": models.TopicStatusType.acknowledged,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10

    # complete the topic
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert data["tag_id"] == str(tag1.tag_id)
    assert len(data["topics"]) == 1
    assert data["topics"][0]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][0]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "completed"
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10

    # add another topic with child tag
    topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name]})  # different tag from topic2

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert len(data["topics"]) == 2
    assert topic1.threat_impact < topic2.threat_impact
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "alerted"
    assert data["topics"][0]["executed_at"] is None
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == "completed"

    # add a unsolved status
    request = {
        "topic_status": models.TopicStatusType.scheduled,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert len(data["topics"]) == 2
    assert topic1.threat_impact < topic2.threat_impact
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][0]["executed_at"]).timestamp() - now < 10
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == "completed"

    # complete the topic
    request = {
        "topic_status": models.TopicStatusType.completed,
    }
    now = datetime.now().timestamp()
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatusessummary/{tag1.tag_id}", headers=headers(USER1)
        )
    )
    assert data["tag_id"] == str(tag1.tag_id)
    assert topic1.threat_impact < topic2.threat_impact
    assert len(data["topics"]) == 2
    assert data["topics"][0]["topic_id"] == str(topic1.topic_id)
    assert data["topics"][0]["threat_impact"] == topic1.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][0]["updated_at"]).timestamp()
        == topic1.updated_at.timestamp()
    )
    assert data["topics"][0]["topic_status"] == "completed"
    assert data["topics"][1]["topic_id"] == str(topic2.topic_id)
    assert data["topics"][1]["threat_impact"] == topic2.threat_impact
    assert (
        datetime.fromisoformat(data["topics"][1]["updated_at"]).timestamp()
        == topic2.updated_at.timestamp()
    )
    assert data["topics"][1]["topic_status"] == request["topic_status"]
    assert datetime.fromisoformat(data["topics"][1]["executed_at"]).timestamp() - now < 10


def test_upload_pteam_tags_file():
    create_user(USER1)
    tag1 = create_tag(USER1, "alpha:alpha2:alpha3")
    pteam1 = create_pteam(USER1, PTEAM1)
    # To test multiple rows error, pteam2 is created for test
    create_pteam(USER1, PTEAM2)

    def _eval_upload_tags_file(blines_, params_) -> dict:
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
            for bline in blines_:
                tfile.writelines(bline + "\n")
            tfile.flush()
            tfile.seek(0)
            with open(tfile.name, "rb") as bfile:
                return assert_200(
                    client.post(
                        f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                        headers=file_upload_headers(USER1),
                        files={"file": bfile},
                        params=params_,
                    )
                )

    def _compare_ext_tags(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"tag_name", "tag_id", "parent_name", "parent_id"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return compare_references(_tag1["references"], _tag1["references"])

    def _compare_responsed_tags(_tags1: List[dict], _tags2: List[dict]) -> bool:
        if not isinstance(_tags1, list) or not isinstance(_tags2, list):
            return False
        if len(_tags1) != len(_tags2):
            return False
        return all(_compare_ext_tags(_tags1[_idx], _tags2[_idx]) for _idx in range(len(_tags1)))

    params = {"group": "threatconnectome", "force_mode": True}

    # upload a line
    lines = [
        (
            '{"tag_name":"teststring",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"}]}'
        )
    ]
    data = _eval_upload_tags_file(lines, params)
    tags = {tag["tag_name"]: tag for tag in data}
    assert len(tags) == 1
    assert "teststring" in tags
    assert compare_references(
        tags["teststring"]["references"],
        [{"group": params["group"], "target": "api/Pipfile.lock", "version": "1.0"}],
    )

    # upload 2 lines
    lines += [
        (
            '{"tag_name":"test1",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"},'
            '{"target":"api3/Pipfile.lock","version":"0.1"}]}'
        )
    ]
    data = _eval_upload_tags_file(lines, params)
    tags = {tag["tag_name"]: tag for tag in data}
    assert len(tags) == 2
    assert "teststring" in tags
    assert "test1" in tags
    assert compare_references(
        tags["teststring"]["references"],
        [{"group": params["group"], "target": "api/Pipfile.lock", "version": "1.0"}],
    )
    assert compare_references(
        tags["test1"]["references"],
        [
            {"group": params["group"], "target": "api/Pipfile.lock", "version": "1.0"},
            {"group": params["group"], "target": "api3/Pipfile.lock", "version": "0.1"},
        ],
    )

    # upload another lines
    lines = ['{"tag_name":"alpha:alpha2:alpha3", "references": [{"target": "", "version": ""}]}']
    data = _eval_upload_tags_file(lines, params)
    tags = {tag["tag_name"]: tag for tag in data}
    assert len(tags) == 1
    assert "alpha:alpha2:alpha3" in tags
    assert compare_references(
        tags["alpha:alpha2:alpha3"]["references"],
        [{"group": params["group"], "target": "", "version": ""}],
    )
    assert tags["alpha:alpha2:alpha3"]["tag_id"] == str(tag1.tag_id)  # already existed tag


def test_upload_pteam_tags_file__complex():
    create_user(USER1)
    tag_aaa = create_tag(USER1, "a:a:a")
    tag_bbb = create_tag(USER1, "b:b:b")
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})

    group_a = {"group": "group-a", "force_mode": True}
    group_b = {"group": "group-b", "force_mode": True}

    def _eval_upload_tags_file(lines_, params_) -> dict:
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
            for line in lines_:
                tfile.writelines(json.dumps(line) + "\n")
            tfile.flush()
            tfile.seek(0)
            with open(tfile.name, "rb") as bfile:
                return assert_200(
                    client.post(
                        f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                        headers=file_upload_headers(USER1),
                        files={"file": bfile},
                        params=params_,
                    )
                )

    def _tags_summary() -> dict:
        return assert_200(
            client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
        )

    def _compare_ext_tags(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"tag_name", "tag_id", "parent_name", "parent_id"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return compare_references(_tag1["references"], _tag1["references"])

    def _compare_responsed_tags(_tags1: List[dict], _tags2: List[dict]) -> bool:
        if not isinstance(_tags1, list) or not isinstance(_tags2, list):
            return False
        if len(_tags1) != len(_tags2):
            return False
        return all(_compare_ext_tags(_tags1[_idx], _tags2[_idx]) for _idx in range(len(_tags1)))

    def _compare_tag_summaries(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"threat_impact", "updated_at", "status_count"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return _compare_ext_tags(_tag1, _tag2)

    def _compare_summaries(_sum1: dict, _sum2: dict) -> bool:
        if not isinstance(_sum1, dict) or not isinstance(_sum2, dict):
            return False
        if _sum1.get("threat_impact_count") != _sum2.get("threat_impact_count"):
            return False
        if len(_sum1["tags"]) != len(_sum2["tags"]):
            return False
        return all(
            _compare_tag_summaries(_sum1["tags"][_idx], _sum2["tags"][_idx])
            for _idx in range(len(_sum1["tags"]))
        )

    # no tags
    summary = _tags_summary()
    summary_exp0 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 0},
        "tags": [],
    }
    assert _compare_summaries(summary, summary_exp0)

    # add a:a:a as group-a
    lines = [
        {
            "tag_name": tag_aaa.tag_name,
            "references": [{"target": "target1", "version": "1.0"}],
        },
    ]
    data = _eval_upload_tags_file(lines, group_a)
    exp1 = {
        **schema_to_dict(tag_aaa),
        "references": [
            {"target": "target1", "version": "1.0", "group": "group-a"},
        ],
    }
    assert _compare_responsed_tags(data, [exp1])
    summary = _tags_summary()
    summary_exp1 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 1},
        "tags": [
            {
                **exp1,
                "threat_impact": None,
                "updated_at": None,
                "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
            }
        ],
    }
    assert _compare_summaries(summary, summary_exp1)

    # add b:b:b as group-b
    lines = [
        {
            "tag_name": tag_bbb.tag_name,
            "references": [
                {"target": "target2", "version": "1.0"},
                {"target": "target2", "version": "1.1"},  # multiple version in one target
            ],
        }
    ]
    data = _eval_upload_tags_file(lines, group_b)
    exp2 = {
        **schema_to_dict(tag_bbb),
        "references": [
            {"target": "target2", "version": "1.0", "group": "group-b"},
            {"target": "target2", "version": "1.1", "group": "group-b"},
        ],
    }
    assert _compare_responsed_tags(data, [exp1, exp2])
    summary = _tags_summary()
    summary_exp2 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 2},
        "tags": [
            {
                **exp1,
                "threat_impact": None,
                "updated_at": None,
                "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
            },
            {
                **exp2,
                "threat_impact": None,
                "updated_at": None,
                "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
            },
        ],
    }
    assert _compare_summaries(summary, summary_exp2)

    # update group-a with b:b:b, without a:a:a
    lines = [
        {
            "tag_name": tag_bbb.tag_name,
            "references": [
                {"target": "target1", "version": "1.2"},
            ],
        }
    ]
    data = _eval_upload_tags_file(lines, group_a)
    exp3 = {
        **schema_to_dict(tag_bbb),
        "references": [
            *exp2["references"],
            {"target": "target1", "version": "1.2", "group": "group-a"},
        ],
    }
    assert _compare_responsed_tags(data, [exp3])
    summary = _tags_summary()
    summary_exp3 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 1},
        "tags": [
            {
                **exp3,
                "threat_impact": None,
                "updated_at": None,
                "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
            }
        ],
    }
    assert _compare_summaries(summary, summary_exp3)


def test_upload_pteam_tags_file_with_empty_file():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent.parent / "upload_test" / "empty.jsonl"
    with open(tag_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_tags_file",
            headers=file_upload_headers(USER1),
            files={"file": tags},
            params=params,
        )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Upload file is empty"


def test_upload_pteam_tags_file_with_wrong_filename():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent.parent / "upload_test" / "tag.txt"
    with open(tag_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_tags_file",
            headers=file_upload_headers(USER1),
            files={"file": tags},
            params=params,
        )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Please upload a file with .jsonl as extension"


def test_upload_pteam_tags_file_without_tag_name():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent.parent / "upload_test" / "no_tag_key.jsonl"
    with open(tag_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_tags_file",
            headers=file_upload_headers(USER1),
            files={"file": tags},
            params=params,
        )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Missing tag_name"


def test_upload_pteam_tags_file_with_wrong_content_format():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    tag_file = (
        Path(__file__).resolve().parent.parent / "upload_test" / "tag_with_wrong_format.jsonl"
    )
    with open(tag_file, "rb") as tags:
        with pytest.raises(HTTPError, match=r"400: Bad Request: Wrong file content"):
            assert_200(
                client.post(
                    f"/pteams/{pteam.pteam_id}/upload_tags_file",
                    headers=file_upload_headers(USER1),
                    files={"file": tags},
                    params=params,
                )
            )


def test_upload_pteam_tags_file_with_unexist_tagnames():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    not_exist_tag_names = ["teststring", "test1", "test2", "test3"]
    refs = {tag_name: [("fake target", "fake version")] for tag_name in not_exist_tag_names}

    with pytest.raises(
        HTTPError,
        match=rf"400: Bad Request: No such tags: {', '.join(sorted(not_exist_tag_names))}",
    ):
        upload_pteam_tags(USER1, pteam1.pteam_id, "threatconnectome", refs, force_mode=False)


def test_get_pteam_tags_summary():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)
    tag3 = create_tag(USER1, TAG3)
    pteam1 = create_pteam(USER1, PTEAM1)

    # set tag1,2,3 to pteam1
    refs0 = {
        tag1.tag_name: [("fake target 1", "fake version 1")],
        tag2.tag_name: [("fake target 2", "fake version 2")],
        tag3.tag_name: [("fake target 3", "fake version 3")],
    }
    group_x = "group_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs0)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    for impact in [1, 2, 3]:
        assert summary["threat_impact_count"][str(impact)] == 0
    assert summary["threat_impact_count"]["4"] == len(refs0)
    assert len(summary["tags"]) == len(refs0)
    sorted_etags = sorted(
        [
            {
                "tag_name": key,
                "references": [{"group": group_x, "target": v[0], "version": v[1]} for v in value],
            }
            for key, value in refs0.items()
        ],
        key=lambda x: x["tag_name"],
    )
    for idx in range(len(refs0)):
        assert summary["tags"][idx]["tag_name"] == sorted_etags[idx]["tag_name"]
        assert summary["tags"][idx]["references"] == sorted_etags[idx]["references"]
        assert summary["tags"][idx]["threat_impact"] is None
        assert summary["tags"][idx]["updated_at"] is None
        assert summary["tags"][idx]["status_count"]["alerted"] == 0
        assert summary["tags"][idx]["status_count"]["acknowledged"] == 0
        assert summary["tags"][idx]["status_count"]["scheduled"] == 0
        assert summary["tags"][idx]["status_count"]["completed"] == 0

    # by not a member
    create_user(USER2)
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER2)))

    # by a member
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    summary2 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER2))
    )
    assert summary2 == summary


def test_update_pteam_tags_summary__update_topic_status():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)
    tag3 = create_tag(USER1, TAG3)
    test_topic_1 = {**TOPIC1, "topic_id": uuid4(), "tags": [TAG1], "threat_impact": 1}
    test_topic_2 = {**TOPIC1, "topic_id": uuid4(), "tags": [TAG1, TAG2], "threat_impact": 3}
    test_topic_3 = {**TOPIC1, "topic_id": uuid4(), "tags": [TAG2, TAG3], "threat_impact": 2}
    topic1 = create_topic(USER1, test_topic_1)
    topic2 = create_topic(USER1, test_topic_2)
    topic3 = create_topic(USER1, test_topic_3)
    pteam1 = create_pteam(USER1, PTEAM1)

    def _extract_ext_tags(
        _ext_tags: List[dict],
    ) -> Tuple[
        Dict[str, dict[str, List[Tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        Dict[str, List[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
        _tag_to_refs_list: Dict[str, List[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    def _sorted_tags(_tags: List[dict]) -> List[dict]:
        return sorted(
            _tags,
            key=lambda x: (
                x.get("threat_impact") or 4,
                -(_dt.timestamp() if (_dt := to_datetime(x.get("updated_at"))) else 0),
                x.get("tag_name", ""),
            ),
        )

    def _compare_ext_tags(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"tag_name", "tag_id", "parent_name", "parent_id"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return compare_references(_tag1["references"], _tag1["references"])

    def _compare_tag_summaries(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"threat_impact", "status_count"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        _keys = {"updated_at"}
        if any(to_datetime(_tag1.get(_key)) != to_datetime(_tag2.get(_key)) for _key in _keys):
            return False
        return _compare_ext_tags(_tag1, _tag2)

    def _compare_summaries(_sum1: dict, _sum2: dict) -> bool:
        if not isinstance(_sum1, dict) or not isinstance(_sum2, dict):
            return False
        if _sum1.get("threat_impact_count") != _sum2.get("threat_impact_count"):
            return False
        if len(_sum1["tags"]) != len(_sum2["tags"]):
            return False
        return all(
            _compare_tag_summaries(_sum1["tags"][_idx], _sum2["tags"][_idx])
            for _idx in range(len(_sum1["tags"]))
        )

    req_tags, resp_tags = _extract_ext_tags([EXT_TAG1, EXT_TAG2, EXT_TAG3])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    tag1_exp0 = {
        **schema_to_dict(tag1),
        "references": resp_tags[tag1.tag_name],
        "threat_impact": 1,
        "updated_at": topic2.updated_at,
        "status_count": {"alerted": 2, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    tag2_exp0 = {
        **schema_to_dict(tag2),
        "references": resp_tags[tag2.tag_name],
        "threat_impact": 2,
        "updated_at": topic3.updated_at,
        "status_count": {"alerted": 2, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    tag3_exp0 = {
        **schema_to_dict(tag3),
        "references": resp_tags[tag3.tag_name],
        "threat_impact": 2,
        "updated_at": topic3.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary_exp0 = {
        "threat_impact_count": {"1": 1, "2": 2, "3": 0, "4": 0},
        "tags": _sorted_tags([tag1_exp0, tag2_exp0, tag3_exp0]),
    }
    assert _compare_summaries(summary, summary_exp0)

    # topic2: set acknoledged
    request = {
        "topic_status": "acknowledged",
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    tag1_exp1 = {
        **schema_to_dict(tag1),
        "references": resp_tags[tag1.tag_name],
        "threat_impact": 1,
        "updated_at": topic2.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 1, "scheduled": 0, "completed": 0},
    }
    summary_exp1 = {
        "threat_impact_count": {"1": 1, "2": 2, "3": 0, "4": 0},
        "tags": _sorted_tags([tag1_exp1, tag2_exp0, tag3_exp0]),
    }
    assert _compare_summaries(summary, summary_exp1)

    # topic2: set completed to tag2
    request = {
        "topic_status": "completed",
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag2.tag_id, request)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    tag2_exp2 = {
        **schema_to_dict(tag2),
        "references": resp_tags[tag2.tag_name],
        "threat_impact": 2,
        "updated_at": topic3.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 1},
    }
    summary_exp2 = {
        "threat_impact_count": {"1": 1, "2": 2, "3": 0, "4": 0},
        "tags": _sorted_tags([tag1_exp1, tag2_exp2, tag3_exp0]),
    }
    assert _compare_summaries(summary, summary_exp2)

    # topic2: set completed to tag1
    request = {
        "topic_status": "completed",
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic2.topic_id, tag1.tag_id, request)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    tag1_exp3 = {
        **schema_to_dict(tag1),
        "references": resp_tags[tag1.tag_name],
        "threat_impact": 1,
        "updated_at": topic1.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 1},
    }
    summary_exp3 = {
        "threat_impact_count": {"1": 1, "2": 2, "3": 0, "4": 0},
        "tags": _sorted_tags([tag1_exp3, tag2_exp2, tag3_exp0]),
    }
    assert _compare_summaries(summary, summary_exp3)

    # topic1: set completed to tag1
    request = {
        "topic_status": "completed",
    }
    create_topicstatus(USER1, pteam1.pteam_id, topic1.topic_id, tag1.tag_id, request)

    summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    tag1_exp4 = {
        **schema_to_dict(tag1),
        "references": resp_tags[tag1.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 2},
    }
    summary_exp4 = {
        "threat_impact_count": {"1": 0, "2": 2, "3": 0, "4": 1},
        "tags": _sorted_tags([tag1_exp4, tag2_exp2, tag3_exp0]),
    }
    assert _compare_summaries(summary, summary_exp4)


def test_update_pteam_tags_summary__update_topic():
    create_user(USER1)
    tag1 = create_tag(USER1, TAG1)
    tag2 = create_tag(USER1, TAG2)
    tag3 = create_tag(USER1, TAG3)
    test_topic_1 = {**TOPIC1, "topic_id": uuid4(), "tags": [TAG1], "threat_impact": 1}
    test_topic_2 = {**TOPIC1, "topic_id": uuid4(), "tags": [TAG1, TAG2], "threat_impact": 3}
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER1, PTEAM2)
    pteam3 = create_pteam(USER1, PTEAM3)

    def _extract_ext_tags(
        _ext_tags: List[dict],
    ) -> Tuple[
        Dict[str, dict[str, List[Tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        Dict[str, List[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
        _tag_to_refs_list: Dict[str, List[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    def _sorted_tags(_tags: List[dict]) -> List[dict]:
        return sorted(
            _tags,
            key=lambda x: (
                x.get("threat_impact") or 4,
                -(_dt.timestamp() if (_dt := to_datetime(x.get("updated_at"))) else 0),
                x.get("tag_name", ""),
            ),
        )

    def _compare_ext_tags(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"tag_name", "tag_id", "parent_name", "parent_id"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return compare_references(_tag1["references"], _tag1["references"])

    def _compare_tag_summaries(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"threat_impact", "status_count"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        _keys = {"updated_at"}
        if any(to_datetime(_tag1.get(_key)) != to_datetime(_tag2.get(_key)) for _key in _keys):
            return False
        return _compare_ext_tags(_tag1, _tag2)

    def _compare_summaries(_sum1: dict, _sum2: dict) -> bool:
        if not isinstance(_sum1, dict) or not isinstance(_sum2, dict):
            return False
        if _sum1.get("threat_impact_count") != _sum2.get("threat_impact_count"):
            return False
        if len(_sum1["tags"]) != len(_sum2["tags"]):
            return False
        return all(
            _compare_tag_summaries(_sum1["tags"][_idx], _sum2["tags"][_idx])
            for _idx in range(len(_sum1["tags"]))
        )

    # set pteam tags
    req_tags1, resp_tags1 = _extract_ext_tags([EXT_TAG1, EXT_TAG2, EXT_TAG3])
    req_tags2, resp_tags2 = _extract_ext_tags([EXT_TAG2])
    req_tags3, resp_tags3 = _extract_ext_tags([EXT_TAG3])

    for group, refs in req_tags1.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)
    for group, refs in req_tags2.items():
        upload_pteam_tags(USER1, pteam2.pteam_id, group, refs)
    for group, refs in req_tags3.items():
        upload_pteam_tags(USER1, pteam3.pteam_id, group, refs)

    # no topics

    # pteam1
    summary1 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt1_tag1_exp0 = {
        **schema_to_dict(tag1),
        "references": resp_tags1[tag1.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    pt1_tag2_exp0 = {
        **schema_to_dict(tag2),
        "references": resp_tags1[tag2.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    pt1_tag3_exp0 = {
        **schema_to_dict(tag3),
        "references": resp_tags1[tag3.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary1_exp0 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 3},
        "tags": _sorted_tags([pt1_tag1_exp0, pt1_tag2_exp0, pt1_tag3_exp0]),
    }
    assert _compare_summaries(summary1, summary1_exp0)

    # pteam2
    summary2 = assert_200(
        client.get(f"/pteams/{pteam2.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt2_tag2_exp0 = {
        **schema_to_dict(tag2),
        "references": resp_tags2[tag2.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary2_exp0 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 1},
        "tags": _sorted_tags([pt2_tag2_exp0]),
    }
    assert _compare_summaries(summary2, summary2_exp0)

    # pteam3
    summary3 = assert_200(
        client.get(f"/pteams/{pteam3.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt3_tag3_exp0 = {
        **schema_to_dict(tag3),
        "references": resp_tags3[tag3.tag_name],
        "threat_impact": None,
        "updated_at": None,
        "status_count": {"alerted": 0, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary3_exp0 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 0, "4": 1},
        "tags": _sorted_tags([pt3_tag3_exp0]),
    }
    assert _compare_summaries(summary3, summary3_exp0)

    # create topic2 (having [TAG1, TAG2])
    topic2 = create_topic(USER1, test_topic_2)

    # pteam1
    summary1 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt1_tag1_exp1 = {
        **schema_to_dict(tag1),
        "references": resp_tags1[tag1.tag_name],
        "threat_impact": 3,
        "updated_at": topic2.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    pt1_tag2_exp1 = {
        **schema_to_dict(tag2),
        "references": resp_tags1[tag2.tag_name],
        "threat_impact": 3,
        "updated_at": topic2.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary1_exp1 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 2, "4": 1},
        "tags": _sorted_tags([pt1_tag1_exp1, pt1_tag2_exp1, pt1_tag3_exp0]),
    }
    assert _compare_summaries(summary1, summary1_exp1)

    # pteam2
    summary2 = assert_200(
        client.get(f"/pteams/{pteam2.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt2_tag2_exp1 = {
        **schema_to_dict(tag2),
        "references": resp_tags2[tag2.tag_name],
        "threat_impact": 3,
        "updated_at": topic2.updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary2_exp1 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 1, "4": 0},
        "tags": _sorted_tags([pt2_tag2_exp1]),
    }
    assert _compare_summaries(summary2, summary2_exp1)

    # pteam3 does not match topic2
    summary3 = assert_200(
        client.get(f"/pteams/{pteam3.pteam_id}/tags/summary", headers=headers(USER1))
    )
    assert _compare_summaries(summary3, summary3_exp0)

    # create topic1 (having [TAG1])
    topic1 = create_topic(USER1, test_topic_1)

    # pteam1
    summary1 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt1_tag1_exp2 = {
        **schema_to_dict(tag1),
        "references": resp_tags1[tag1.tag_name],
        "threat_impact": 1,
        "updated_at": topic1.updated_at,
        "status_count": {"alerted": 2, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary1_exp2 = {
        "threat_impact_count": {"1": 1, "2": 0, "3": 1, "4": 1},
        "tags": _sorted_tags([pt1_tag1_exp2, pt1_tag2_exp1, pt1_tag3_exp0]),
    }
    assert _compare_summaries(summary1, summary1_exp2)

    # pteam2 does not match topic1
    summary2 = assert_200(
        client.get(f"/pteams/{pteam2.pteam_id}/tags/summary", headers=headers(USER1))
    )
    assert _compare_summaries(summary2, summary2_exp1)

    # pteam3 does not match topic1
    summary3 = assert_200(
        client.get(f"/pteams/{pteam3.pteam_id}/tags/summary", headers=headers(USER1))
    )
    assert _compare_summaries(summary3, summary3_exp0)

    # modify topic1
    request = {
        "threat_impact": 4,
    }
    data = assert_200(
        client.put(f"/topics/{topic1.topic_id}", headers=headers(USER1), json=request)
    )
    topic1_updated_at = data["updated_at"]

    # pteam1
    summary1 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt1_tag1_exp3 = {
        **schema_to_dict(tag1),
        "references": resp_tags1[tag1.tag_name],
        "threat_impact": 3,
        "updated_at": topic1_updated_at,  # modified topic1 is latest
        "status_count": {"alerted": 2, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary1_exp3 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 2, "4": 1},
        "tags": _sorted_tags([pt1_tag1_exp3, pt1_tag2_exp1, pt1_tag3_exp0]),
    }
    assert _compare_summaries(summary1, summary1_exp3)

    # pteam2 does not match topic1
    summary2 = assert_200(
        client.get(f"/pteams/{pteam2.pteam_id}/tags/summary", headers=headers(USER1))
    )
    assert _compare_summaries(summary2, summary2_exp1)

    # pteam3 does not match topic1
    summary3 = assert_200(
        client.get(f"/pteams/{pteam3.pteam_id}/tags/summary", headers=headers(USER1))
    )
    assert _compare_summaries(summary3, summary3_exp0)

    # modify topic2 (append TAG3)
    request = {
        "tags": [tag2.tag_name, tag3.tag_name],
    }
    data = assert_200(
        client.put(f"/topics/{topic2.topic_id}", headers=headers(USER1), json=request)
    )
    topic2_updated_at = data["updated_at"]

    # pteam1
    summary1 = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt1_tag1_exp4 = {
        **schema_to_dict(tag1),
        "references": resp_tags1[tag1.tag_name],
        "threat_impact": 4,
        "updated_at": topic1_updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    pt1_tag2_exp4 = {
        **schema_to_dict(tag2),
        "references": resp_tags1[tag2.tag_name],
        "threat_impact": 3,
        "updated_at": topic2_updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    pt1_tag3_exp4 = {
        **schema_to_dict(tag3),
        "references": resp_tags1[tag3.tag_name],
        "threat_impact": 3,
        "updated_at": topic2_updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary1_exp4 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 2, "4": 1},
        "tags": _sorted_tags([pt1_tag1_exp4, pt1_tag2_exp4, pt1_tag3_exp4]),
    }
    assert _compare_summaries(summary1, summary1_exp4)

    # pteam2
    summary2 = assert_200(
        client.get(f"/pteams/{pteam2.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt2_tag2_exp4 = {
        **schema_to_dict(tag2),
        "references": resp_tags2[tag2.tag_name],
        "threat_impact": 3,
        "updated_at": topic2_updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary2_exp4 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 1, "4": 0},
        "tags": _sorted_tags([pt2_tag2_exp4]),
    }
    assert _compare_summaries(summary2, summary2_exp4)

    # pteam3
    summary3 = assert_200(
        client.get(f"/pteams/{pteam3.pteam_id}/tags/summary", headers=headers(USER1))
    )
    pt3_tag3_exp4 = {
        **schema_to_dict(tag3),
        "references": resp_tags3[tag3.tag_name],
        "threat_impact": 3,
        "updated_at": topic2_updated_at,
        "status_count": {"alerted": 1, "acknowledged": 0, "scheduled": 0, "completed": 0},
    }
    summary3_exp4 = {
        "threat_impact_count": {"1": 0, "2": 0, "3": 1, "4": 0},
        "tags": _sorted_tags([pt3_tag3_exp4]),
    }
    assert _compare_summaries(summary3, summary3_exp4)


def test_get_pteam_tagged_topic_ids():
    create_user(USER1)
    create_user(USER2)
    tag1 = create_tag(USER1, "test:tag:alpha")
    tag2 = create_tag(USER1, "test:tag:bravo")
    pteam1 = create_pteam(USER1, PTEAM1)

    # with wrong pteam_id
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam"):
        assert_200(
            client.get(
                f"/pteams/{tag1.tag_id}/tags/{tag1.tag_id}/solved_topic_ids",
                headers=headers(USER1),
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam"):
        assert_200(
            client.get(
                f"/pteams/{tag1.tag_id}/tags/{tag1.tag_id}/unsolved_topic_ids",
                headers=headers(USER1),
            )
        )

    # with wrong tag_id
    with pytest.raises(HTTPError, match=r"404: Not Found: No such tag"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{pteam1.pteam_id}/solved_topic_ids",
                headers=headers(USER1),
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such tag"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{pteam1.pteam_id}/unsolved_topic_ids",
                headers=headers(USER1),
            )
        )

    # with valid but not a pteam tag
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{tag1.tag_id}/solved_topic_ids",
                headers=headers(USER1),
            )
        )
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{tag1.tag_id}/unsolved_topic_ids",
                headers=headers(USER1),
            )
        )

    # by not a member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{tag1.tag_id}/solved_topic_ids",
                headers=headers(USER2),
            )
        )
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(
            client.get(
                f"/pteams/{pteam1.pteam_id}/tags/{tag1.tag_id}/unsolved_topic_ids",
                headers=headers(USER2),
            )
        )

    def _get_topics(user, pteam, tag, tgt_solved) -> schemas.PTeamTaggedTopics:
        _leaf = "solved_topic_ids" if tgt_solved else "unsolved_topic_ids"
        _data = assert_200(
            client.get(f"/pteams/{pteam.pteam_id}/tags/{tag.tag_id}/{_leaf}", headers=headers(user))
        )
        _ret = schemas.PTeamTaggedTopics(**_data)
        assert _ret.pteam_id == pteam.pteam_id
        assert _ret.tag_id == tag.tag_id
        return _ret

    # add tag1 to pteam1
    refs0 = {tag1.tag_name: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, "fake group", refs0)

    # user2 become a member
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, p_invitation.invitation_id)

    # get by member
    solved = _get_topics(USER2, pteam1, tag1, True)
    assert solved.topic_ids == []
    assert solved.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved = _get_topics(USER2, pteam1, tag1, False)
    assert unsolved.topic_ids == []
    assert unsolved.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}

    # create topic1 with tag1
    topic1 = create_topic(USER1, {**TOPIC1, "threat_impact": 1, "tags": [tag1.tag_name]})
    solved = _get_topics(USER2, pteam1, tag1, True)
    assert solved.topic_ids == []
    assert solved.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved = _get_topics(USER2, pteam1, tag1, False)
    assert unsolved.topic_ids == [topic1.topic_id]
    assert unsolved.threat_impact_count == {"1": 1, "2": 0, "3": 0, "4": 0}

    # create topic2 with tag1.parent
    topic2 = create_topic(USER1, {**TOPIC2, "threat_impact": 2, "tags": [tag1.parent_name]})
    solved = _get_topics(USER2, pteam1, tag1, True)
    assert solved.topic_ids == []
    assert solved.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved = _get_topics(USER2, pteam1, tag1, False)
    assert unsolved.topic_ids == [topic1.topic_id, topic2.topic_id]  # sorted by impect&date
    assert unsolved.threat_impact_count == {"1": 1, "2": 1, "3": 0, "4": 0}

    # create topic3 with tag1 & tag2
    topic3 = create_topic(
        USER1, {**TOPIC3, "threat_impact": 1, "tags": [tag1.tag_name, tag2.tag_name]}
    )
    solved = _get_topics(USER2, pteam1, tag1, True)
    assert solved.topic_ids == []
    assert solved.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved = _get_topics(USER2, pteam1, tag1, False)
    assert unsolved.topic_ids == [topic3.topic_id, topic1.topic_id, topic2.topic_id]
    assert unsolved.threat_impact_count == {"1": 2, "2": 1, "3": 0, "4": 0}

    # add tag2 to pteam1
    assert tag1.parent_id == tag2.parent_id
    refs1 = {
        tag1.tag_name: [("fake target", "fake version")],
        tag2.tag_name: [("fake target", "fake version")],
    }
    upload_pteam_tags(USER1, pteam1.pteam_id, "fake group", refs1)

    solved2 = _get_topics(USER2, pteam1, tag2, True)
    assert solved2.topic_ids == []
    assert solved2.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved2 = _get_topics(USER2, pteam1, tag2, False)
    assert unsolved2.topic_ids == [topic3.topic_id, topic2.topic_id]
    assert unsolved2.threat_impact_count == {"1": 1, "2": 1, "3": 0, "4": 0}

    # complete topic3 tag1
    create_topicstatus(
        USER1,
        pteam1.pteam_id,
        topic3.topic_id,
        tag1.tag_id,
        {"topic_status": models.TopicStatusType.completed},
    )

    solved = _get_topics(USER2, pteam1, tag1, True)
    assert solved.topic_ids == [topic3.topic_id]
    assert solved.threat_impact_count == {"1": 1, "2": 0, "3": 0, "4": 0}
    unsolved = _get_topics(USER2, pteam1, tag1, False)
    assert unsolved.topic_ids == [topic1.topic_id, topic2.topic_id]
    assert unsolved.threat_impact_count == {"1": 1, "2": 1, "3": 0, "4": 0}
    solved2 = _get_topics(USER2, pteam1, tag2, True)
    assert solved2.topic_ids == []
    assert solved2.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved2 = _get_topics(USER2, pteam1, tag2, False)
    assert unsolved2.topic_ids == [topic3.topic_id, topic2.topic_id]
    assert unsolved2.threat_impact_count == {"1": 1, "2": 1, "3": 0, "4": 0}

    # delete tag1 from pteam1
    refs2 = {tag2.tag_name: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, "fake group", refs2)

    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _get_topics(USER2, pteam1, tag1, True)
    with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam tag"):
        _get_topics(USER2, pteam1, tag1, False)
    solved2 = _get_topics(USER2, pteam1, tag2, True)
    assert solved2.topic_ids == []
    assert solved2.threat_impact_count == {"1": 0, "2": 0, "3": 0, "4": 0}
    unsolved2 = _get_topics(USER2, pteam1, tag2, False)
    assert unsolved2.topic_ids == [topic3.topic_id, topic2.topic_id]
    assert unsolved2.threat_impact_count == {"1": 1, "2": 1, "3": 0, "4": 0}


def test_disable_pteam():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam4 = create_pteam(USER1, PTEAM4)
    request = {"disabled": True}
    updated_response = client.put(
        f"/pteams/{pteam4.pteam_id}", headers=headers(USER1), json=request
    )
    assert updated_response.status_code == 200
    updated_pteam = schemas.PTeamInfo(**updated_response.json())
    assert updated_pteam.disabled is True

    pteams_response = client.get("/pteams", headers=headers(USER1))
    assert pteams_response.status_code == 200
    pteams_data = pteams_response.json()
    assert len(pteams_data) == 2
    for pteam in pteams_data:
        assert (UUID(pteam["pteam_id"]) == pteam1.pteam_id and pteam["disabled"] is False) or (
            UUID(pteam["pteam_id"]) == pteam4.pteam_id and pteam["disabled"] is True
        )

    pteam_response = client.get(f"/pteams/{pteam4.pteam_id}", headers=headers(USER1))
    assert pteam_response.status_code == 200
    pteam_data = pteam_response.json()
    assert pteam_data["pteam_id"] == str(pteam4.pteam_id)
    assert pteam_data["pteam_name"] == PTEAM4["pteam_name"]
    assert pteam_data["alert_slack"]["webhook_url"] == PTEAM4["alert_slack"]["webhook_url"]
    assert pteam_data["disabled"] is True

    user_response = client.get("/users/me", headers=headers(USER1))
    assert user_response.status_code == 200
    data = user_response.json()
    assert data["email"] == USER1["email"]
    assert data["disabled"] == USER1["disabled"]
    assert data["years"] == USER1["years"]
    assert len(data["pteams"]) == 2
    for pteam in data["pteams"]:
        assert (UUID(pteam["pteam_id"]) == pteam1.pteam_id and pteam["disabled"] is False) or (
            UUID(pteam["pteam_id"]) == pteam4.pteam_id and pteam["disabled"] is True
        )


def test_delete_disabled_pteam_invitation():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM4)
    # create invitation
    invite_to_pteam(USER1, pteam.pteam_id)
    # list invitations
    invitation_response1 = client.get(
        f"/pteams/{pteam.pteam_id}/invitation", headers=headers(USER1)
    )
    assert invitation_response1.status_code == 200
    invitation_data1 = invitation_response1.json()
    assert len(invitation_data1) == 1
    # disbale pteam
    disable_request = {"disabled": True}
    disable_response = client.put(
        f"/pteams/{pteam.pteam_id}", headers=headers(USER1), json=disable_request
    )
    assert disable_response.status_code == 200

    # enable pteam
    enable_request = {"disabled": False}
    enable_response = client.put(
        f"/pteams/{pteam.pteam_id}", headers=headers(USER1), json=enable_request
    )
    assert enable_response.status_code == 200
    # list invitations again
    invitation_response2 = client.get(
        f"/pteams/{pteam.pteam_id}/invitation", headers=headers(USER1)
    )
    assert invitation_response2.status_code == 200
    invitation_data2 = invitation_response2.json()
    assert len(invitation_data2) == 0


def test_summary_of_disabled_pteam(testdb):
    # pteam1 has topic1 with tag1, while pteam4 has topic4 with tag3.
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam4 = create_pteam(USER1, PTEAM4)
    create_topic(USER1, TOPIC1)  # TAG1
    topic4 = create_topic(USER1, TOPIC4)  # TAG3
    tag3 = topic4.tags[0]

    group_x = "group_x"

    refs1 = {TAG1: [("fake target", "fake version")]}
    refs3 = {TAG3: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs1)
    upload_pteam_tags(USER1, pteam4.pteam_id, group_x, refs3)

    # test that tagsummary is updated when pteam4 is not disabled
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam4.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic4.topic_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag3.tag_id),
        )
        .all()
    )

    # disable pteam4
    request = {"disabled": True}
    assert_200(client.put(f"/pteams/{pteam4.pteam_id}", headers=headers(USER1), json=request))
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam4.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag3.tag_id),
        )
        .all()
        == []
    )

    # test that tagsummary is not updated when creating topic3 with tag1 and tag3
    create_topic(USER1, TOPIC3)  # TAG1 & TAG3

    refs_x = {
        TAG1: [("fake target", "fake version")],
        TAG3: [("fake target", "fake version")],
    }
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs_x)
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam4.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag3.tag_id),
        )
        .all()
        == []
    )
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag3.tag_id),
        )
        .all()
    )

    # test that tagsummary is not updated when topic4 is updated
    create_tag(USER1, "TAG4")
    request = {
        "title": "topic4 for update",
        "tags": ["TAG4"],
    }
    data = assert_200(
        client.put(f"/topics/{TOPIC4['topic_id']}", headers=headers(USER1), json=request)
    )
    responsed_topic = schemas.TopicResponse(**data)
    for tag in responsed_topic.tags:
        if tag.tag_id != tag3.tag_id:
            tag4 = tag
    refs_y = {tag4.tag_name: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group_x, refs_y)
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam4.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag4.tag_id),
        )
        .all()
        == []
    )
    assert (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag4.tag_id),
        )
        .all()
    )


def test_auto_close_topic():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],  # fake references
    }

    def _extract_ext_tags(
        _ext_tags: List[dict],
    ) -> Tuple[
        Dict[str, dict[str, List[Tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        Dict[str, List[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
        _tag_to_refs_list: Dict[str, List[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.tag_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.tag_name],
            "vulnerable_versions": {
                tag4.tag_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.tag_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.tag_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name, tag3.tag_name, tag4.tag_name],
            "actions": actions,
        },
    )

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close_topic__parent():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag1:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag2:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag3:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag4:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],  # fake references
    }

    def _extract_ext_tags(
        _ext_tags: List[dict],
    ) -> Tuple[
        Dict[str, dict[str, List[Tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        Dict[str, List[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
        _tag_to_refs_list: Dict[str, List[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag2.parent_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.parent_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.parent_name],
            "vulnerable_versions": {
                tag4.parent_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.parent_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.parent_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [
                tag1.parent_name,
                tag2.parent_name,
                tag3.parent_name,
                tag4.parent_name,
            ],
            "actions": actions,
        },
    )

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
            headers=headers(USER1),
        )
    )
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close_by_pteamtags():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],
    }

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.tag_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.tag_name],
            "vulnerable_versions": {
                tag4.tag_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.tag_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.tag_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name, tag3.tag_name, tag4.tag_name],
            "actions": actions,
        },
    )

    def _extract_ext_tags(
        _ext_tags: List[dict],
    ) -> Tuple[
        Dict[str, dict[str, List[Tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        Dict[str, List[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
        _tag_to_refs_list: Dict[str, List[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    # create pteam after creating topic
    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close__on_upload_pteam_tags_file():
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",  # vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}
    # first time
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    last_executed_at = data["action_logs"][0]["executed_at"]

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    # second time (update)

    ext_tag2["references"][0]["version"] = "1.1"
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # not changed (not vulnerable)
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # vulnerable -> not vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    assert data["action_logs"][0]["executed_at"] == last_executed_at  # not modified

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL


def test_auto_close__on_upload_pteam_tags_file__parent():
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag1:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag2:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",  # vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag2.parent_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.parent_name, tag2.parent_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}
    # first time
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    last_executed_at = data["action_logs"][0]["executed_at"]

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    # second time (update)

    ext_tag2["references"][0]["version"] = "1.1"
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # not changed (not vulnerable)
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # vulnerable -> not vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    assert data["action_logs"][0]["executed_at"] == last_executed_at  # not modified

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL


def test_remove_pteamtags_by_group():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    group1 = "threatconnectome"
    group2 = "flashsense"

    refs0 = {TAG1: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, group1, refs0)
    response2 = upload_pteam_tags(USER1, pteam1.pteam_id, group2, refs0)

    for tag in response2:
        for reference in tag.references:
            assert reference["group"] in [group1, group2]

    assert_204(
        client.delete(
            f"/pteams/{pteam1.pteam_id}/tags",
            headers=headers(USER1),
            params={"group": group1},
        )
    )
    tag_summary = assert_200(
        client.get(f"/pteams/{pteam1.pteam_id}/tags/summary", headers=headers(USER1))
    )
    for tag in tag_summary["tags"]:
        for reference in tag["references"]:
            assert reference["group"] != group1
            assert reference["group"] == group2


def test_get_watchers():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)

    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER1)))
    assert len(data) == 0

    watching_request1 = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request1.request_id, pteam1.pteam_id)

    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER1)))
    assert len(data) == 1
    assert data[0]["ateam_id"] == str(ateam1.ateam_id)

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # get by member
    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER2)))
    assert len(data) == 1
    assert data[0]["ateam_id"] == str(ateam1.ateam_id)

    # get by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER3)))


def test_remove_watcher():
    create_user(USER1)
    create_user(USER2)
    create_user(USER3)
    ateam1 = create_ateam(USER1, ATEAM1)
    pteam1 = create_pteam(USER1, PTEAM1)

    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    watching_request = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam1.pteam_id)

    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER1)))
    assert len(data) == 1

    # delete by not member
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/pteams/{pteam1.pteam_id}/watchers/{ateam1.ateam_id}", headers=headers(USER3)
            )
        )

    # delete by not ADMIN
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have authority"):
        assert_200(
            client.delete(
                f"/pteams/{pteam1.pteam_id}/watchers/{ateam1.ateam_id}", headers=headers(USER2)
            )
        )

    # delete by ADMIN
    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/watchers/{ateam1.ateam_id}", headers=headers(USER1)
    )
    assert response.status_code == 204
    data = assert_200(client.get(f"/pteams/{pteam1.pteam_id}/watchers", headers=headers(USER1)))
    assert len(data) == 0
    data = assert_200(
        client.get(f"/ateams/{ateam1.ateam_id}/watching_pteams", headers=headers(USER1))
    )
    assert len(data) == 0


def test_fix_status_mismatch(testdb: Session):
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",  # vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}

    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)

    # delete records of autoclose
    currentStatus = (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic1.topic_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag1.tag_id),
        )
        .one()
    )
    currentStatus.topic_status = models.TopicStatusType.alerted
    testdb.add(currentStatus)

    ptts = (
        testdb.query(models.PTeamTopicTagStatus)
        .filter(
            models.PTeamTopicTagStatus.status_id == data["status_id"],
            models.PTeamTopicTagStatus.topic_status == "completed",
        )
        .one()
    )
    ptts.topic_status = models.TopicStatusType.alerted
    testdb.add(ptts)

    action_log = (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.logging_id == data["action_logs"][0]["logging_id"])
        .one()
    )
    testdb.delete(action_log)
    testdb.commit()

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_status"] == "alerted"

    # call fix_status_mimatch API
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/fix_status_mismatch",
        headers=headers(USER1),
    )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)


def test_fix_status_mismatch_tag(testdb: Session):
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}

    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> not vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    # tag1
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data_tag1 = response.json()
    assert data_tag1["topic_status"] == "completed"
    assert data_tag1["note"] == "auto closed by system"
    assert data_tag1["user_id"] == str(SYSTEM_UUID)
    assert len(data_tag1["action_logs"]) == 1
    assert data_tag1["action_logs"][0]["user_id"] == str(SYSTEM_UUID)

    # tag2
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data_tag2 = response.json()
    assert data_tag2["topic_status"] == "completed"
    assert data_tag2["note"] == "auto closed by system"
    assert data_tag2["user_id"] == str(SYSTEM_UUID)
    assert len(data_tag2["action_logs"]) == 1
    assert data_tag2["action_logs"][0]["user_id"] == str(SYSTEM_UUID)

    # delete records of autoclose

    # tag1
    currentStatus = (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic1.topic_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag1.tag_id),
        )
        .one()
    )
    currentStatus.topic_status = models.TopicStatusType.alerted
    testdb.add(currentStatus)

    ptts = (
        testdb.query(models.PTeamTopicTagStatus)
        .filter(
            models.PTeamTopicTagStatus.status_id == data_tag1["status_id"],
            models.PTeamTopicTagStatus.topic_status == "completed",
        )
        .one()
    )
    ptts.topic_status = models.TopicStatusType.alerted
    testdb.add(ptts)

    action_log = (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.logging_id == data_tag1["action_logs"][0]["logging_id"])
        .one()
    )
    testdb.delete(action_log)
    testdb.commit()

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["topic_status"] == "alerted"

    # tag2
    currentStatus = (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == str(topic1.topic_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag2.tag_id),
        )
        .one()
    )
    currentStatus.topic_status = models.TopicStatusType.alerted
    testdb.add(currentStatus)

    ptts = (
        testdb.query(models.PTeamTopicTagStatus)
        .filter(
            models.PTeamTopicTagStatus.status_id == data_tag2["status_id"],
            models.PTeamTopicTagStatus.topic_status == "completed",
        )
        .one()
    )
    ptts.topic_status = models.TopicStatusType.alerted
    testdb.add(ptts)

    action_log = (
        testdb.query(models.ActionLog)
        .filter(models.ActionLog.logging_id == data_tag2["action_logs"][0]["logging_id"])
        .one()
    )
    testdb.delete(action_log)
    testdb.commit()

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["topic_status"] == "alerted"

    # call fix_status_mimatch API
    response = client.post(
        f"/pteams/{pteam1.pteam_id}/tags/{tag1.tag_id}/fix_status_mismatch",
        headers=headers(USER1),
    )
    assert response.status_code == 200

    # tag1
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)

    # tag2
    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_status"] == "alerted"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)


def test_upload_pteam_sbom_file_with_syft():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    # To avoid multiple rows error, pteam2 is created for test
    create_pteam(USER1, PTEAM2)

    params = {"group": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "test_syft_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        data = assert_200(
            client.post(
                f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )
        )
    tags = {tag["tag_name"]: tag for tag in data}
    assert "axios:npm:npm" in tags
    assert {
        (r["target"], r["version"], r["group"]) for r in tags["axios:npm:npm"]["references"]
    } == {
        ("/package-lock.json", "1.6.7", params["group"]),
    }


def test_upload_pteam_sbom_file_with_trivy():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    # To avoid multiple rows error, pteam2 is created for test
    create_pteam(USER1, PTEAM2)

    params = {"group": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "test_trivy_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        data = assert_200(
            client.post(
                f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )
        )
    tags = {tag["tag_name"]: tag for tag in data}
    assert "axios:npm:npm" in tags
    assert {
        (r["target"], r["version"], r["group"]) for r in tags["axios:npm:npm"]["references"]
    } == {
        ("package-lock.json", "1.6.7", params["group"]),
        (".", "1.6.7", params["group"]),
    }


def test_upload_pteam_sbom_file_with_empty_file():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "empty.json"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_sbom_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Upload file is empty"


def test_upload_pteam_sbom_file_with_wrong_filename():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "tag.txt"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_sbom_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Please upload a file with .json as extension"


def test_upload_pteam_sbom_file_wrong_content_format():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"group": "threatconnectome", "force_mode": True}
    sbom_file = (
        Path(__file__).resolve().parent.parent / "upload_test" / "tag_with_wrong_format.json"
    )
    with open(sbom_file, "rb") as tags:
        with pytest.raises(HTTPError, match=r"400: Bad Request: Not supported file format"):
            assert_200(
                client.post(
                    f"/pteams/{pteam.pteam_id}/upload_sbom_file",
                    headers=file_upload_headers(USER1),
                    params=params,
                    files={"file": tags},
                )
            )


class TestAutoClose:
    class _Util:
        @staticmethod
        def get_topic_status(
            pteam: schemas.PTeamInfo,
            topic: schemas.Topic,
            tag: schemas.TagResponse,
        ) -> schemas.TopicStatusResponse:
            data = assert_200(
                client.get(
                    f"/pteams/{pteam.pteam_id}/topicstatus/{topic.topic_id}/{tag.tag_id}",
                    headers=headers(USER1),
                )
            )
            return schemas.TopicStatusResponse(**data)

        @staticmethod
        def gen_action_dict(**kwargs) -> dict:
            action = {
                "action": "update alpha to 2.0",
                "action_type": "elimination",
                "recommended": True,
                "ext": {
                    "tags": [TAG1],
                    "vulnerable_versions": {
                        TAG1: [">=1.0 <2.0"],
                    },
                },
                **kwargs,
            }
            return action

        @staticmethod
        def gen_simple_ext(tag: str, vulnerables: Optional[List[str]]) -> dict:
            ext: Dict[str, Any] = {"tags": [tag]}
            if vulnerables is not None:
                ext.update({"vulnerable_versions": {tag: vulnerables}})
            return ext

    class TestEndpointTopics:
        class TestOnCreateTopic:
            pass  # see other test_auto_close*
            # TODO: implement or move tests here

        class TestOnUpdateTopic:
            util: Type
            tag1: schemas.TagResponse
            topic1: schemas.Topic
            action1: schemas.ActionResponse

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1],
                        "actions": [TestAutoClose._Util.gen_action_dict()],
                    },
                )
                self.action1 = topic1.actions[0]
                self.topic1 = topic1

            def test_update_topic__to_enable(self) -> None:
                request = {"disabled": True}
                assert_200(
                    client.put(
                        f"/topics/{self.topic1.topic_id}", headers=headers(USER1), json=request
                    )
                )

                pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, pteam1.pteam_id, "group1", refs0)
                with pytest.raises(HTTPError, match=r"404: Not Found: No such topic"):
                    self.util.get_topic_status(pteam1, self.topic1, self.tag1)

                # test auto-close triggerd when topic enabled
                request = {"disabled": False}
                assert_200(
                    client.put(
                        f"/topics/{self.topic1.topic_id}", headers=headers(USER1), json=request
                    )
                )

                status = self.util.get_topic_status(pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == self.action1.action_id

    class TestEndpointActions:
        class TestOnCreateAction:
            util: Type
            pteam1: schemas.PTeamInfo
            tag1: schemas.TagResponse
            topic1: schemas.Topic

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                self.tag2 = create_tag(USER1, TAG2)
                self.pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "group1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

            def test_add_action__matched(self) -> None:
                # topic1 alerted because of having no actions
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close triggerd when new action created
                action1_dict = self.util.gen_action_dict()
                action1 = create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action1.action_id

                # test auto-close not triggered if already completed
                action2_dict = {
                    **action1_dict,
                    "action": action1_dict["action"] + "xxx",  # not to conflict action_id
                }
                create_action(USER1, action2_dict, self.topic1.topic_id)
                # status should not overwritten by action2
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action1.action_id

            def test_add_action__not_matched(self) -> None:
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close aborted if tag-matched action not found
                action1_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG2, [">=1.0 <2.0"])
                )
                create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close pick only matched actions
                action2_dict = {
                    **action1_dict,
                    "action": action1_dict["action"] + "xxx",  # not to conflict action_id
                    "ext": self.util.gen_simple_ext(TAG1, [">=1 <2.0"]),
                }
                action2 = create_action(USER1, action2_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action2.action_id

        class TestOnDeleteAction:
            util: Type
            pteam1: schemas.PTeamInfo
            tag1: schemas.TagResponse
            topic1: schemas.Topic

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                self.tag2 = create_tag(USER1, TAG2)
                self.pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "group1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

            def test_delete_action(self) -> None:
                # topic1 alerted because of having no actions
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # new action created with uncomparable version
                action1_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG1, [">=alpha <charlie"])
                )
                action1 = create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # new action created with comparable version
                action2_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG1, [">=1.0 <2.0"])
                )
                action2 = create_action(USER1, action2_dict, self.topic1.topic_id)
                # action1 still blocks auto-close
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # delete action1
                assert_204(client.delete(f"/actions/{action1.action_id}", headers=headers(USER1)))
                # now topic1 can be closed with action2
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action2.action_id

    class TestEndpointPTeams:
        class TestOnCreatePTeam:
            pass  # see other test_auto_close*
            # TODO: implement or move tests here

        class TestOnUpdatePTeam:
            util: Type
            pteam1: schemas.PTeamInfo
            tag1: schemas.TagResponse

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                self.pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "group1", refs0)

            def test_update_pteam__to_enable(self) -> None:
                request = {
                    "disabled": True,
                }
                assert_200(
                    client.put(
                        f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=request
                    )
                )

                topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1],
                        "actions": [self.util.gen_action_dict()],
                    },
                )
                action1 = topic1.actions[0]

                with pytest.raises(HTTPError, match=r"404: Not Found: No such pteam"):
                    status = self.util.get_topic_status(self.pteam1, topic1, self.tag1)

                # test auto-close triggerd when pteam enabled
                request = {"disabled": False}
                assert_200(
                    client.put(
                        f"/pteams/{self.pteam1.pteam_id}", headers=headers(USER1), json=request
                    )
                )

                status = self.util.get_topic_status(self.pteam1, topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action1.action_id

        class TestOnAddPTeamTag:
            pass  # see test_auto_close__on_add_pteamtag*
            # TODO: implement or move tests here

        class TestOnUpdatePTeamTag:
            pass  # see test_auto_close__on_update_pteamtag*
            # TODO: implement or move tests here

        class TestOnUploadTagsFile:
            pass  # see test_auto_close__on_upload_pteam_tags_file*
            # TODO: implement or move tests here
