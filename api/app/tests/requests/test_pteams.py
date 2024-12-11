import io
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageChops
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import (
    DEFAULT_ALERT_SSVC_PRIORITY,
    MEMBER_UUID,
    NOT_MEMBER_UUID,
    ZERO_FILLED_UUID,
)
from app.main import app
from app.ssvc.ssvc_calculator import calculate_ssvc_priority_by_threat
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    PTEAM1,
    PTEAM2,
    SAMPLE_SLACK_WEBHOOK_URL,
    TAG1,
    TAG2,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
    USER3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_pteam_invitation,
    assert_200,
    assert_204,
    calc_file_sha256,
    compare_references,
    compare_tags,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    file_upload_headers,
    get_pteam_services,
    get_pteam_tags,
    get_service_by_service_name,
    headers,
    invite_to_pteam,
    schema_to_dict,
    set_ticket_status,
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
    assert pteam1.alert_ssvc_priority == PTEAM1["alert_ssvc_priority"]
    assert pteam1.pteam_id != ZERO_FILLED_UUID

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    user_me = response.json()
    assert {UUID(pteam["pteam_id"]) for pteam in user_me["pteams"]} == {pteam1.pteam_id}

    pteam2 = create_pteam(USER1, PTEAM2)
    assert pteam2.pteam_name == PTEAM2["pteam_name"]
    assert pteam2.contact_info == PTEAM2["contact_info"]
    assert pteam2.alert_slack.webhook_url == PTEAM2["alert_slack"]["webhook_url"]
    assert pteam2.alert_ssvc_priority == PTEAM2["alert_ssvc_priority"]
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
    del _pteam["alert_ssvc_priority"]
    del _pteam["alert_mail"]
    pteam1 = create_pteam(USER1, _pteam)
    assert pteam1.contact_info == ""
    assert pteam1.alert_slack.enable is True
    assert pteam1.alert_slack.webhook_url == ""
    assert pteam1.alert_ssvc_priority == DEFAULT_ALERT_SSVC_PRIORITY
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
    assert data["alert_ssvc_priority"] == PTEAM2["alert_ssvc_priority"]
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
    assert data["alert_ssvc_priority"] == PTEAM2["alert_ssvc_priority"]
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

    response = client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json=empty_data)
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_name"] == ""
    assert data["contact_info"] == ""
    assert data["alert_slack"]["webhook_url"] == ""
    assert data["alert_ssvc_priority"] == PTEAM1["alert_ssvc_priority"]


@pytest.mark.parametrize(
    "field_name, expected_response_detail",
    [
        ("pteam_name", "Cannot specify None for pteam_name"),
        ("contact_info", "Cannot specify None for contact_info"),
        ("alert_slack", "Cannot specify None for alert_slack"),
        ("alert_ssvc_priority", "Cannot specify None for alert_ssvc_priority"),
        ("alert_mail", "Cannot specify None for alert_mail"),
    ],
)
def test_update_pteam_should_return_400_when_required_fields_is_None(
    field_name, expected_response_detail
):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    request = {field_name: None}
    response = client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json=request)
    assert response.status_code == 400
    assert response.json()["detail"] == expected_response_detail


def test_get_pteam_services_register_multiple_services():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER1, PTEAM2)
    create_tag(USER1, TAG1)

    # no services at created pteam
    services1 = get_pteam_services(USER1, pteam1.pteam_id)
    services2 = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1 == services2 == []

    refs0 = {TAG1: [("fake target", "fake version")]}

    # add service x to pteam1
    service_x = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)

    services1a = get_pteam_services(USER1, pteam1.pteam_id)
    services2a = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1a[0].service_name == service_x
    assert services2a == []

    # add grserviceoup y to pteam2
    service_y = "service_y"
    upload_pteam_tags(USER1, pteam2.pteam_id, service_y, refs0)

    services1b = get_pteam_services(USER1, pteam1.pteam_id)
    services2b = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1b[0].service_name == service_x
    assert services2b[0].service_name == service_y

    # add service y to pteam1
    upload_pteam_tags(USER1, pteam1.pteam_id, service_y, refs0)

    services1c = get_pteam_services(USER1, pteam1.pteam_id)
    services2c = get_pteam_services(USER1, pteam2.pteam_id)

    assert services1c[0].service_name == service_x or service_y
    assert services1c[1].service_name == service_x or service_y
    assert services2c[0].service_name == service_y

    # only members get services
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        get_pteam_services(USER2, pteam1.pteam_id)


@pytest.mark.parametrize(
    "service_request, expected",
    [
        (
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
        ),
        (
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
            },
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
        ),
    ],
)
def test_get_pteam_services_verify_if_all_responses_are_filled(service_request, expected):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_tag(USER1, TAG1)

    refs0 = {TAG1: [("fake target", "fake version")]}
    service_name = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

    service_id1 = get_service_by_service_name(USER1, pteam1.pteam_id, service_name)["service_id"]

    client.put(
        f"/pteams/{pteam1.pteam_id}/services/{service_id1}",
        headers=headers(USER1),
        json=service_request,
    )

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/services",
        headers=headers(USER1),
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["service_name"] == service_name
    assert data[0]["service_id"] == service_id1
    assert data[0]["description"] == expected["description"]
    assert data[0]["keywords"] == expected["keywords"]
    assert data[0]["system_exposure"] == expected["system_exposure"]
    assert data[0]["service_mission_impact"] == expected["service_mission_impact"]
    assert data[0]["service_safety_impact"] == expected["service_safety_impact"]


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
    service_x = "service_x"
    refs1 = {tag1.tag_name: [("fake target", "fake version")]}
    expected_ref1 = [
        {"service": service_x, "target": "fake target", "version": "fake version"},
    ]
    etags1a = upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs1)

    assert len(etags1a) == 1
    assert compare_tags(etags1a, [tag1])
    assert compare_references(etags1a[0].references, expected_ref1)

    etags1b = get_pteam_tags(USER1, pteam1.pteam_id)
    assert len(etags1b) == 1
    assert compare_tags(etags1b, [tag1])
    assert compare_references(etags1b[0].references, expected_ref1)

    # add tag2 to pteam1
    service_y = "service_y"
    refs2 = {tag2.tag_name: [("fake target 2", "fake version 2")]}
    expected_ref2 = [
        {"service": service_y, "target": "fake target 2", "version": "fake version 2"},
    ]
    etags2a = upload_pteam_tags(USER1, pteam1.pteam_id, service_y, refs2)

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
    response = client.put(
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
    response = client.put(f"/pteams/{pteam1.pteam_id}/authority", json=request)  # no headers
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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

    response = client.put(
        f"/pteams/{pteam1.pteam_id}/authority",
        headers=headers(USER1),
        json=[{"user_id": str(MEMBER_UUID), "authorities": ["admin"]}],
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"

    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/authority", headers=headers(USER2), json=request
    )
    assert response.status_code == 200

    # remove all admins
    request = [
        {"user_id": str(user1.user_id), "authorities": []},
        {"user_id": str(user2.user_id), "authorities": []},
    ]
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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
    response = client.put(
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


def test_success_upload_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_tag(USER1, TAG1)
    refs0 = {TAG1: [("fake target", "fake version")]}
    service_x = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = Path(__file__).resolve().parent / "upload_test" / "image" / "yes_image.png"
    with open(image_filepath, "rb") as image_file:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    assert response.status_code == 200
    assert response.reason_phrase == "OK"


def test_failed_upload_service_thumbnail_when_wrong_image_size():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_tag(USER1, TAG1)
    refs0 = {TAG1: [("fake target", "fake version")]}
    service_x = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = Path(__file__).resolve().parent / "upload_test" / "image" / "error_image.png"
    with open(image_filepath, "rb") as image_file:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Dimensions must be 720 x 480 px"


def test_get_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_tag(USER1, TAG1)
    refs0 = {TAG1: [("fake target", "fake version")]}
    service_x = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = Path(__file__).resolve().parent / "upload_test" / "image" / "yes_image.png"
    with open(image_filepath, "rb") as image_file:
        client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

        response = client.get(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=headers(USER1),
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        diff_image = ImageChops.difference(
            Image.open(image_file), Image.open(io.BytesIO(response.content))
        )
        assert diff_image.getbbox() is None


def test_delete_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_tag(USER1, TAG1)
    refs0 = {TAG1: [("fake target", "fake version")]}
    service_x = "service_x"
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = Path(__file__).resolve().parent / "upload_test" / "image" / "yes_image.png"
    with open(image_filepath, "rb") as image_file:
        client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    delete_response = client.delete(
        f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
        headers=headers(USER1),
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
        headers=headers(USER1),
    )
    assert get_response.status_code == 404


def test_get_dependency(testdb):
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)
    pteam_id = ticket_response["pteam_id"]
    service_id = ticket_response["service_id"]

    dependencies_response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/dependencies", headers=headers(USER1)
    )
    dependency1 = dependencies_response.json()[0]
    dependency_id = dependency1["dependency_id"]

    dependency_response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/dependencies/{dependency_id}",
        headers=headers(USER1),
    )
    assert dependency_response.status_code == 200
    data = dependency_response.json()
    assert data["dependency_id"] == dependency1["dependency_id"]
    assert data["service_id"] == dependency1["service_id"]
    assert data["tag_id"] == dependency1["tag_id"]
    assert data["version"] == dependency1["version"]
    assert data["target"] == dependency1["target"]


def test_get_dependency_with_wrong_pteam_id(testdb):
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)
    pteam_id = ticket_response["pteam_id"]
    service_id = ticket_response["service_id"]

    dependencies_response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/dependencies", headers=headers(USER1)
    )
    dependency1 = dependencies_response.json()[0]
    dependency_id = dependency1["dependency_id"]

    wrong_pteam_id = str(uuid4())
    dependency_response = client.get(
        f"/pteams/{wrong_pteam_id}/services/{service_id}/dependencies/{dependency_id}",
        headers=headers(USER1),
    )
    assert dependency_response.status_code == 404
    assert dependency_response.json() == {"detail": "No such pteam"}


def test_get_dependency_with_wrong_service_id(testdb):
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)
    pteam_id = ticket_response["pteam_id"]
    service_id = ticket_response["service_id"]

    dependencies_response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/dependencies", headers=headers(USER1)
    )
    dependency1 = dependencies_response.json()[0]
    dependency_id = dependency1["dependency_id"]

    wrong_service_id = str(uuid4())
    dependency_response = client.get(
        f"/pteams/{pteam_id}/services/{wrong_service_id}/dependencies/{dependency_id}",
        headers=headers(USER1),
    )
    assert dependency_response.status_code == 404
    assert dependency_response.json() == {"detail": "No such service"}


def test_get_dependency_with_wrong_dependency_id(testdb):
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)
    pteam_id = ticket_response["pteam_id"]
    service_id = ticket_response["service_id"]
    wrong_dependency_id = str(uuid4())
    dependency_response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/dependencies/{wrong_dependency_id}",
        headers=headers(USER1),
    )
    assert dependency_response.status_code == 404
    assert dependency_response.json() == {"detail": "No such dependency"}


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
    response = client.put(
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


def test_get_pteam_topics():
    user1 = create_user(USER1)
    create_user(USER2)
    create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # add tag1 to pteam1
    service_x = "service_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)

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


def test_get_pteam_topics__by_not_member():
    create_user(USER1)
    create_user(USER2)
    create_tag(USER1, TAG1)
    pteam1 = create_pteam(USER1, PTEAM1)

    # add tag1 to pteam1
    service_x = "service_x"
    refs0 = {TAG1: [("fake target 1", "fake version 1")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, service_x, refs0)

    response = client.get(f"/pteams/{pteam1.pteam_id}/topics", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


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

    def _compare_responsed_tags(_tags1: list[dict], _tags2: list[dict]) -> bool:
        if not isinstance(_tags1, list) or not isinstance(_tags2, list):
            return False
        if len(_tags1) != len(_tags2):
            return False
        return all(_compare_ext_tags(_tags1[_idx], _tags2[_idx]) for _idx in range(len(_tags1)))

    params = {"service": "threatconnectome", "force_mode": True}

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
        [{"service": params["service"], "target": "api/Pipfile.lock", "version": "1.0"}],
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
        [{"service": params["service"], "target": "api/Pipfile.lock", "version": "1.0"}],
    )
    assert compare_references(
        tags["test1"]["references"],
        [
            {"service": params["service"], "target": "api/Pipfile.lock", "version": "1.0"},
            {"service": params["service"], "target": "api3/Pipfile.lock", "version": "0.1"},
        ],
    )

    # upload duplicated lines
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
        [{"service": params["service"], "target": "api/Pipfile.lock", "version": "1.0"}],
    )
    assert compare_references(
        tags["test1"]["references"],
        [
            {"service": params["service"], "target": "api/Pipfile.lock", "version": "1.0"},
            {"service": params["service"], "target": "api3/Pipfile.lock", "version": "0.1"},
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
        [{"service": params["service"], "target": "", "version": ""}],
    )
    assert tags["alpha:alpha2:alpha3"]["tag_id"] == str(tag1.tag_id)  # already existed tag


def test_upload_pteam_tags_file__complex():
    create_user(USER1)
    tag_aaa = create_tag(USER1, "a:a:a")
    tag_bbb = create_tag(USER1, "b:b:b")
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})

    service_a = {"service": "service-a", "force_mode": True}
    service_b = {"service": "service-b", "force_mode": True}

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

    def _compare_ext_tags(_tag1: dict, _tag2: dict) -> bool:
        if not isinstance(_tag1, dict) or not isinstance(_tag2, dict):
            return False
        _keys = {"tag_name", "tag_id", "parent_name", "parent_id"}
        if any(_tag1.get(_key) != _tag2.get(_key) for _key in _keys):
            return False
        return compare_references(_tag1["references"], _tag1["references"])

    def _compare_responsed_tags(_tags1: list[dict], _tags2: list[dict]) -> bool:
        if not isinstance(_tags1, list) or not isinstance(_tags2, list):
            return False
        if len(_tags1) != len(_tags2):
            return False
        return all(_compare_ext_tags(_tags1[_idx], _tags2[_idx]) for _idx in range(len(_tags1)))

    # add a:a:a as service-a
    lines = [
        {
            "tag_name": tag_aaa.tag_name,
            "references": [{"target": "target1", "version": "1.0"}],
        },
    ]
    data = _eval_upload_tags_file(lines, service_a)
    exp1 = {
        **schema_to_dict(tag_aaa),
        "references": [
            {"target": "target1", "version": "1.0", "service": "service-a"},
        ],
    }
    assert _compare_responsed_tags(data, [exp1])

    # add b:b:b as service-b
    lines = [
        {
            "tag_name": tag_bbb.tag_name,
            "references": [
                {"target": "target2", "version": "1.0"},
                {"target": "target2", "version": "1.1"},  # multiple version in one target
            ],
        }
    ]
    data = _eval_upload_tags_file(lines, service_b)
    exp2 = {
        **schema_to_dict(tag_bbb),
        "references": [
            {"target": "target2", "version": "1.0", "service": "service-b"},
            {"target": "target2", "version": "1.1", "service": "service-b"},
        ],
    }
    assert _compare_responsed_tags(data, [exp1, exp2])

    # update service-a with b:b:b, without a:a:a
    lines = [
        {
            "tag_name": tag_bbb.tag_name,
            "references": [
                {"target": "target1", "version": "1.2"},
            ],
        }
    ]
    data = _eval_upload_tags_file(lines, service_a)
    exp3 = {
        **schema_to_dict(tag_bbb),
        "references": [
            *exp2["references"],
            {"target": "target1", "version": "1.2", "service": "service-a"},
        ],
    }
    assert _compare_responsed_tags(data, [exp3])


def test_upload_pteam_tags_file_with_empty_file():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"service": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent / "upload_test" / "empty.jsonl"
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

    params = {"service": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent / "upload_test" / "tag.txt"
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

    params = {"service": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent / "upload_test" / "no_tag_key.jsonl"
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

    params = {"service": "threatconnectome", "force_mode": True}
    tag_file = Path(__file__).resolve().parent / "upload_test" / "tag_with_wrong_format.jsonl"
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


def test_service_tagged_ticket_ids_with_wrong_pteam_id(testdb):
    # create ticket_status table
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["ticket_id"],
        json_data,
    )

    # with wrong pteam_id
    pteam_id = str(uuid4())
    response = client.get(
        f"/pteams/{pteam_id}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No such pteam"}


def test_service_tagged_ticket_ids_with_wrong_pteam_member(testdb):
    # create ticket_status table
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["ticket_id"],
        json_data,
    )

    # with wrong pteam member
    create_user(USER2)
    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{ticket_response['tag_id']}/topic_ids",
        headers=headers(USER2),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not a pteam member"}


def test_service_tagged_ticket_ids_with_wrong_service_id(testdb):
    # create ticket_status table
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["ticket_id"],
        json_data,
    )

    # with wrong service_id
    service_id = str(uuid4())
    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{service_id}/tags/{ticket_response['tag_id']}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No such service"}


def test_service_tagged_ticket_ids_with_service_not_in_pteam(testdb):
    # create ticket_status table
    ticket_response1 = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)
    ticket_response2 = ticket_utils.create_ticket(testdb, USER2, PTEAM2, TOPIC2)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        ticket_response1["ticket_id"],
        json_data,
    )

    # with service not in pteam
    response = client.get(
        f"/pteams/{ticket_response1['pteam_id']}/services/{ticket_response2['service_id']}/tags/{ticket_response1['tag_id']}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No such service"}


def test_service_tagged_tikcet_ids_with_wrong_tag_id(testdb):
    # create ticket_status table
    ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response["pteam_id"],
        ticket_response["service_id"],
        ticket_response["ticket_id"],
        json_data,
    )

    # with wrong tag_id
    tag_id = str(uuid4())
    response = client.get(
        f"/pteams/{ticket_response['pteam_id']}/services/{ticket_response['service_id']}/tags/{tag_id}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No such tag"}


def test_service_tagged_ticket_ids_with_valid_but_not_service_tag(testdb):
    # create ticket_status table
    ticket_response1 = ticket_utils.create_ticket(testdb, USER1, PTEAM1, TOPIC1)

    json_data = {
        "topic_status": "acknowledged",
        "note": "string",
        "assignees": [],
        "scheduled_at": None,
    }
    set_ticket_status(
        USER1,
        ticket_response1["pteam_id"],
        ticket_response1["service_id"],
        ticket_response1["ticket_id"],
        json_data,
    )

    # with valid but not service tag
    str1 = "a1:a2:a3"
    tag = create_tag(USER1, str1)
    response = client.get(
        f"/pteams/{ticket_response1['pteam_id']}/services/{ticket_response1['service_id']}/tags/{tag.tag_id}/topic_ids",
        headers=headers(USER1),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "No such service tag"}


def test_remove_pteamtags_by_service():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service1 = "threatconnectome"
    service2 = "flashsense"

    refs0 = {TAG1: [("fake target", "fake version")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, service1, refs0)
    response2 = upload_pteam_tags(USER1, pteam1.pteam_id, service2, refs0)

    for tag in response2:
        for reference in tag.references:
            assert reference["service"] in [service1, service2]

    assert_204(
        client.delete(
            f"/pteams/{pteam1.pteam_id}/tags",
            headers=headers(USER1),
            params={"service": service1},
        )
    )


def test_upload_pteam_sbom_file_with_syft():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    # To avoid multiple rows error, pteam2 is created for test
    create_pteam(USER1, PTEAM2)

    params = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "test_syft_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["service_name"] == params["service"]
    assert data["sbom_file_sha256"] == calc_file_sha256(sbom_file)


def test_upload_pteam_sbom_file_with_trivy():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    # To avoid multiple rows error, pteam2 is created for test
    create_pteam(USER1, PTEAM2)

    params = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "test_trivy_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/upload_sbom_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["service_name"] == params["service"]
    assert data["sbom_file_sha256"] == calc_file_sha256(sbom_file)


def test_upload_pteam_sbom_file_with_empty_file():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "empty.json"
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

    params = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "tag.txt"
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


def test_it_should_return_422_when_upload_sbom_with_over_255_char_servicename():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    # create 256 alphanumeric characters
    service_name = "a" * 256

    params = {"service": service_name, "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "test_trivy_cyclonedx.json"
    with open(sbom_file, "rb") as tags:
        response = client.post(
            f"/pteams/{pteam.pteam_id}/upload_sbom_file",
            headers=file_upload_headers(USER1),
            params=params,
            files={"file": tags},
        )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Length of Service name exceeds 255 characters"


@pytest.mark.skip(reason="TODO: need api to get background task status")
def test_upload_pteam_sbom_file_wrong_content_format():
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)

    params = {"service": "threatconnectome", "force_mode": True}
    sbom_file = Path(__file__).resolve().parent / "upload_test" / "tag_with_wrong_format.json"
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


class TestGetPTeamServiceTagsSummary:
    ssvc_priority_count_zero: dict[str, int] = {
        ssvc_priority.value: 0 for ssvc_priority in list(models.SSVCDeployerPriorityEnum)
    }

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        return data["access_token"]

    @staticmethod
    def _get_service_id_by_service_name(user: dict, pteam_id: UUID | str, service_name: str) -> str:
        response = client.get(f"/pteams/{pteam_id}/services", headers=headers(user))
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        service = next(filter(lambda x: x["service_name"] == service_name, data))
        return service["service_id"]

    def test_returns_summary_even_if_no_topics(self):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"
        refs0 = {tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)

        # no topics, no threats, no tickets

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/services/{service_id1}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TopicStatusType)
                },
            }
        ]

    def test_returns_summary_even_if_no_threats(self):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"
        refs0 = {tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)
        # create topic1
        create_topic(USER1, TOPIC1)  # Tag1

        # no threats nor tickets

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/services/{service_id1}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TopicStatusType)
                },
            }
        ]

    def test_returns_summary_if_having_alerted_ticket(self, testdb):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        vulnerable_version = "1.2.0"  # vulnerable
        refs0 = {tag1.tag_name: [(test_target, vulnerable_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)
        # add actionable topic1
        action1 = {
            "action": "action one",
            "action_type": "elimination",
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {
                    tag1.tag_name: ["< 1.2.3"],  # > vulnerable_version
                },
            },
        }
        topic1 = create_topic(USER1, TOPIC1, actions=[action1])  # Tag1
        db_threat1 = testdb.scalars(select(models.Threat)).one()

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/services/{service_id1}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        expected_ssvc_priority = calculate_ssvc_priority_by_threat(db_threat1)
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            expected_ssvc_priority.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(topic1.updated_at),
                "status_count": {
                    **{status_type.value: 0 for status_type in list(models.TopicStatusType)},
                    models.TopicStatusType.alerted.value: 1,  # default status is ALERTED
                },
            }
        ]


class TestGetPTeamTagsSummary:
    ssvc_priority_count_zero: dict[str, int] = {
        ssvc_priority.value: 0 for ssvc_priority in list(models.SSVCDeployerPriorityEnum)
    }

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        return data["access_token"]

    @staticmethod
    def _get_service_id_by_service_name(user: dict, pteam_id: UUID | str, service_name: str) -> str:
        response = client.get(f"/pteams/{pteam_id}/services", headers=headers(user))
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        service = next(filter(lambda x: x["service_name"] == service_name, data))
        return service["service_id"]

    def test_returns_summary_even_if_no_topics(self):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"
        refs0 = {tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)

        # no topics, no threats, no tickets

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "service_ids": [service_id1],
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TopicStatusType)
                },
            }
        ]

    def test_returns_summary_even_if_no_threats(self):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "test version"
        refs0 = {tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)
        # create topic1
        create_topic(USER1, TOPIC1)  # Tag1

        # no threats nor tickets

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            models.SSVCDeployerPriorityEnum.DEFER.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "service_ids": [service_id1],
                "ssvc_priority": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TopicStatusType)
                },
            }
        ]

    def test_returns_summary_if_having_alerted_ticket(self, testdb):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        vulnerable_version = "1.2.0"  # vulnerable
        refs0 = {tag1.tag_name: [(test_target, vulnerable_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service)
        # add actionable topic1
        action1 = {
            "action": "action one",
            "action_type": "elimination",
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {
                    tag1.tag_name: ["< 1.2.3"],  # > vulnerable_version
                },
            },
        }
        topic1 = create_topic(USER1, TOPIC1, actions=[action1])  # Tag1
        db_threat1 = testdb.scalars(select(models.Threat)).one()

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        expected_ssvc_priority = calculate_ssvc_priority_by_threat(db_threat1)
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            expected_ssvc_priority.value: 1,
        }
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "service_ids": [service_id1],
                "ssvc_priority": expected_ssvc_priority.value,
                "updated_at": datetime.isoformat(topic1.updated_at),
                "status_count": {
                    **{status_type.value: 0 for status_type in list(models.TopicStatusType)},
                    models.TopicStatusType.alerted.value: 1,  # default status is ALERTED
                },
            }
        ]

    def test_returns_summary_even_if_multiple_services_are_registrered(self, testdb):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service1 = "test_service1"
        test_service2 = "test_service2"
        test_target = "test target"
        vulnerable_version = "1.2.0"  # vulnerable
        refs0 = {tag1.tag_name: [(test_target, vulnerable_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service1, refs0)
        upload_pteam_tags(USER1, pteam1.pteam_id, test_service2, refs0)
        service_id1 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service1)
        service_id2 = self._get_service_id_by_service_name(USER1, pteam1.pteam_id, test_service2)

        # add actionable topic1
        action1 = {
            "action": "action one",
            "action_type": "elimination",
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {
                    tag1.tag_name: ["< 1.2.3"],  # > vulnerable_version
                },
            },
        }
        topic1 = create_topic(USER1, TOPIC1, actions=[action1])  # Tag1
        db_threats = testdb.scalars(select(models.Threat)).all()

        # get summary
        url = f"/pteams/{pteam1.pteam_id}/tags/summary"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        summary = response.json()
        expected_ssvc_priority = min(  # we have only 1 tag
            calculate_ssvc_priority_by_threat(db_threat) for db_threat in db_threats
        )
        assert summary["ssvc_priority_count"] == {
            **self.ssvc_priority_count_zero,
            expected_ssvc_priority: 1,
        }

        assert len(summary["tags"][0]["service_ids"]) == 2
        assert set(summary["tags"][0]["service_ids"]) == {service_id1, service_id2}

        del summary["tags"][0]["service_ids"]
        assert summary["tags"] == [
            {
                "tag_id": str(tag1.tag_id),
                "tag_name": tag1.tag_name,
                "parent_id": str(tag1.parent_id) if tag1.parent_id else None,
                "parent_name": tag1.parent_name if tag1.parent_name else None,
                "ssvc_priority": expected_ssvc_priority,
                "updated_at": datetime.isoformat(topic1.updated_at),
                "status_count": {
                    **{status_type.value: 0 for status_type in list(models.TopicStatusType)},
                    models.TopicStatusType.alerted.value: 2,  # default status is ALERTED
                },
            }
        ]


class TestTicketStatus:

    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self.user1 = create_user(USER1)
            self.user2 = create_user(USER2)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
            accept_pteam_invitation(USER2, invitation1.invitation_id)

            self.tag1 = create_tag(USER1, TAG1)
            # add test_service to pteam1
            test_service = "test_service"
            test_target = "test target"
            test_version = "1.2.3"
            refs0 = {self.tag1.tag_name: [(test_target, test_version)]}
            upload_pteam_tags(USER1, self.pteam1.pteam_id, test_service, refs0)
            self.service_id1 = self._get_service_id_by_service_name(
                USER1, self.pteam1.pteam_id, test_service
            )

        @pytest.fixture(scope="function", autouse=False)
        def actionable_topic1(self):
            action1 = self._gen_action([self.tag1.tag_name])
            self.topic1 = create_topic(
                USER1, {**TOPIC1, "tags": [self.tag1.tag_name], "actions": [action1]}
            )
            tickets = self._get_tickets(
                self.pteam1.pteam_id, self.service_id1, self.topic1.topic_id, self.tag1.tag_id
            )
            self.ticket_id1 = tickets[0]["ticket_id"]

        @pytest.fixture(scope="function", autouse=False)
        def not_actionable_topic1(self):
            self.topic1 = create_topic(
                USER1, {**TOPIC1, "tags": [self.tag1.tag_name], "actions": []}
            )
            self.ticket_id1 = None

        @staticmethod
        def _get_access_token(user: dict) -> str:
            body = {
                "username": user["email"],
                "password": user["pass"],
            }
            response = client.post("/auth/token", data=body)
            if response.status_code != 200:
                raise HTTPError(response)
            data = response.json()
            return data["access_token"]

        @staticmethod
        def _get_service_id_by_service_name(
            user: dict, pteam_id: UUID | str, service_name: str
        ) -> str:
            response = client.get(f"/pteams/{pteam_id}/services", headers=headers(user))
            if response.status_code != 200:
                raise HTTPError(response)
            data = response.json()
            service = next(filter(lambda x: x["service_name"] == service_name, data))
            return service["service_id"]

        @staticmethod
        def _gen_action(tag_names: list[str]) -> dict:
            return {
                "action": f"sample action for {str(tag_names)}",
                "action_type": models.ActionType.elimination,
                "recommended": True,
                "ext": {
                    "tags": tag_names,
                    "vulnerable_versions": {tag_name: ["<999.99.9"] for tag_name in tag_names},
                },
            }

        def _get_tickets(self, pteam_id: str, service_id: str, topic_id: str, tag_id: str) -> dict:
            url = (
                f"/pteams/{pteam_id}/services/{service_id}"
                f"/topics/{topic_id}/tags/{tag_id}/tickets"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            return client.get(url, headers=_headers).json()

        def _set_ticket_status(
            self, pteam_id: str, service_id: str, ticket_id: str, request: dict
        ) -> dict:
            url = f"/pteams/{pteam_id}/services/{service_id}/ticketstatus/{ticket_id}"
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            return client.put(url, headers=_headers, json=request).json()

    class TestGet(Common):

        def test_returns_initial_status_if_no_status_created(self, actionable_topic1):
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.get(url, headers=_headers)
            assert response.status_code == 200

            now = datetime.now()
            data = response.json()
            expected_status = {
                "status_id": data["status_id"],  # do not check
                "ticket_id": str(self.ticket_id1),
                "topic_status": models.TopicStatusType.alerted.value,
                "user_id": None,
                "created_at": data["created_at"],  # check later
                "assignees": [],
                "note": None,
                "scheduled_at": None,
                "action_logs": [],
            }
            assert data == expected_status

            created_at = datetime.fromisoformat(data["created_at"])
            assert now - timedelta(seconds=10) < created_at < now

        def test_returns_current_status_if_status_created(self, actionable_topic1):
            status_request = {
                "topic_status": models.TopicStatusType.scheduled.value,
                "assignees": [str(self.user2.user_id)],
                "note": "assign user2 and schedule at 2345/6/7",
                "scheduled_at": "2345-06-07T08:09:10",
            }
            set_response = self._set_ticket_status(
                self.pteam1.pteam_id, self.service_id1, self.ticket_id1, status_request
            )

            # get ticket status
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.get(url, headers=_headers)
            assert response.status_code == 200

            data = response.json()
            expected_status = {
                "status_id": set_response["status_id"],
                "ticket_id": str(self.ticket_id1),
                "user_id": str(self.user1.user_id),
                "created_at": set_response["created_at"],
                "action_logs": [],
                **status_request,
            }
            assert data == expected_status

    class TestSet(Common):

        def common_setup_for_set_ticket_status(self, topic_status, need_scheduled_at, scheduled_at):
            status_request = {
                "assignees": [str(self.user2.user_id)],
            }
            if topic_status is not None:
                status_request["topic_status"] = topic_status
            if need_scheduled_at:
                status_request["scheduled_at"] = scheduled_at
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            return response

        def test_set_requested_status(self, actionable_topic1):
            status_request = {
                "topic_status": models.TopicStatusType.scheduled.value,
                "assignees": [str(self.user2.user_id)],
                "note": "assign user2 and schedule at 2345/6/7",
                "scheduled_at": "2345-06-07T08:09:10",
            }
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            assert response.status_code == 200

            data = response.json()
            # check not-none only because we do not have values to compare
            for key in {"status_id", "created_at"}:
                assert data[key] is not None
                del data[key]
            expected_status = {
                "ticket_id": str(self.ticket_id1),
                "user_id": str(self.user1.user_id),
                "action_logs": [],
                **status_request,
            }
            assert data == expected_status

        @pytest.mark.parametrize(
            "field_name, expected_response_detail",
            [
                ("topic_status", "Cannot specify None for topic_status"),
                ("logging_ids", "Cannot specify None for logging_ids"),
                ("assignees", "Cannot specify None for assignees"),
            ],
        )
        def test_it_should_return_400_when_required_fields_is_None(
            self,
            actionable_topic1,
            field_name,
            expected_response_detail,
        ):
            status_request = {field_name: None}
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "topic_status, scheduled_at, expected_response_detail",
            [
                (models.TopicStatusType.alerted.value, None, "Wrong topic status"),
                (
                    models.TopicStatusType.alerted.value,
                    None,
                    "Wrong topic status",
                ),
                (
                    models.TopicStatusType.alerted.value,
                    "2000-01-01T00:00:00",
                    "Wrong topic status",
                ),
                (
                    models.TopicStatusType.alerted.value,
                    "2345-06-07T08:09:10",
                    "Wrong topic status",
                ),
            ],
        )
        def test_it_should_return_400_when_topic_status_is_alerted(
            self,
            actionable_topic1,
            topic_status,
            scheduled_at,
            expected_response_detail,
        ):
            response = self.common_setup_for_set_ticket_status(topic_status, True, scheduled_at)
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "topic_status, scheduled_at, expected_response_detail",
            [
                (
                    models.TopicStatusType.acknowledged.value,
                    "2000-01-01T00:00:00",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TopicStatusType.acknowledged.value,
                    "2345-06-07T08:09:10",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TopicStatusType.completed.value,
                    "2000-01-01T00:00:00",
                    "If status is not scheduled, do not specify schduled_at",
                ),
                (
                    models.TopicStatusType.completed.value,
                    "2345-06-07T08:09:10",
                    "If status is not scheduled, do not specify schduled_at",
                ),
            ],
        )
        def test_it_should_return_400_when_topic_status_is_not_scheduled_and_schduled_at_is_time(
            self,
            actionable_topic1,
            topic_status,
            scheduled_at,
            expected_response_detail,
        ):
            response = self.common_setup_for_set_ticket_status(topic_status, True, scheduled_at)
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "topic_status, need_scheduled_at, scheduled_at, expected_response_detail",
            [
                (
                    models.TopicStatusType.scheduled.value,
                    False,
                    None,
                    "If status is scheduled, specify schduled_at",
                ),
                (
                    models.TopicStatusType.scheduled.value,
                    True,
                    None,
                    "If status is scheduled, unable to reset schduled_at",
                ),
                (
                    models.TopicStatusType.scheduled.value,
                    True,
                    "2000-01-01T00:00:00",
                    "If status is scheduled, schduled_at must be a future time",
                ),
            ],
        )
        def test_it_should_return_400_when_schduled_at_is_not_future_time(
            self,
            actionable_topic1,
            topic_status,
            need_scheduled_at,
            scheduled_at,
            expected_response_detail,
        ):
            # when topic_status is schduled and schduled at is not future time, return 200.

            response = self.common_setup_for_set_ticket_status(
                topic_status, need_scheduled_at, scheduled_at
            )
            assert response.status_code == 400
            assert response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "topic_status, need_scheduled_at, scheduled_at, expected_response_status_code",
            [
                (models.TopicStatusType.acknowledged.value, False, None, 200),
                (
                    models.TopicStatusType.acknowledged.value,
                    True,
                    None,
                    200,
                ),
                (models.TopicStatusType.scheduled.value, True, "2345-06-07T08:09:10", 200),
                (models.TopicStatusType.completed.value, False, None, 200),
                (models.TopicStatusType.completed.value, True, None, 200),
            ],
        )
        def test_it_should_return_200_when_topic_status_and_schduled_at_have_the_correct_values(
            self,
            actionable_topic1,
            topic_status,
            need_scheduled_at,
            scheduled_at,
            expected_response_status_code,
        ):
            response = self.common_setup_for_set_ticket_status(
                topic_status, need_scheduled_at, scheduled_at
            )
            assert response.status_code == expected_response_status_code
            set_response = response.json()
            assert set_response["ticket_id"] == self.ticket_id1
            assert set_response["topic_status"] == topic_status
            assert set_response["user_id"] == str(self.user1.user_id)
            assert set_response["assignees"] == [str(self.user2.user_id)]
            assert set_response["scheduled_at"] == scheduled_at

        @pytest.mark.parametrize(
            "current_topic_status, current_scheduled_at, expected_response_detail",
            [
                (
                    models.TopicStatusType.completed.value,
                    None,
                    "If current status is not scheduled and previous status is schduled, "
                    "need to reset schduled_at",
                ),
                (
                    models.TopicStatusType.acknowledged.value,
                    None,
                    "If current status is not scheduled and previous status is schduled, "
                    "need to reset schduled_at",
                ),
            ],
        )
        def test_it_should_return_400_when_previous_status_is_schduled_and_schduled_at_is_reset(
            self,
            actionable_topic1,
            current_topic_status,
            current_scheduled_at,
            expected_response_detail,
        ):
            # When previou topic_status is schduled and current topic_status is not schduled,
            # return 400 if current_scheduled_at does not contain
            # a value to reset None.

            previous_topic_status = models.TopicStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_topic_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_topic_status, False, current_scheduled_at
            )
            assert current_response.status_code == 400
            assert current_response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "current_topic_status, current_scheduled_at, expected_response_detail",
            [
                (
                    None,
                    None,
                    "If status is scheduled, unable to reset schduled_at",
                ),
                (
                    None,
                    "2000-01-01T00:00:00",
                    "If status is scheduled, schduled_at must be a future time",
                ),
            ],
        )
        def test_it_should_return_400_when_topic_status_and_scheduled_at_is_not_appropriate(
            self,
            actionable_topic1,
            current_topic_status,
            current_scheduled_at,
            expected_response_detail,
        ):
            # When previou topic_status is schduled and current topic_status is None,
            # return 400 if current_scheduled_at does not contain
            # future time or None.

            previous_topic_status = models.TopicStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_topic_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_topic_status, True, current_scheduled_at
            )
            assert current_response.status_code == 400
            assert current_response.json()["detail"] == expected_response_detail

        @pytest.mark.parametrize(
            "current_topic_status, need_scheduled_at, "
            + "current_scheduled_at, expected_response_status_code",
            [
                (
                    None,
                    False,
                    None,
                    200,
                ),
                (
                    models.TopicStatusType.completed.value,
                    True,
                    None,
                    200,
                ),
            ],
        )
        def test_it_should_return_200_when_previous_and_current_status_have_the_correct_values(
            self,
            actionable_topic1,
            current_topic_status,
            need_scheduled_at,
            current_scheduled_at,
            expected_response_status_code,
        ):
            # When previou topic_status is schduled and current topic_status is None,
            # return 200 if current_scheduled_at contain None.

            # When previou topic_status is schduled and current topic_status is completed,
            # return 200 if current_scheduled_at contain
            # a value to reset None.

            previous_topic_status = models.TopicStatusType.scheduled.value
            previous_scheduled_at = "2345-06-07T08:09:10"
            previous_response = self.common_setup_for_set_ticket_status(
                previous_topic_status, True, previous_scheduled_at
            )
            assert previous_response.status_code == 200

            current_response = self.common_setup_for_set_ticket_status(
                current_topic_status, need_scheduled_at, current_scheduled_at
            )
            assert current_response.status_code == expected_response_status_code

            set_response = current_response.json()
            assert set_response["ticket_id"] == self.ticket_id1
            assert set_response["user_id"] == str(self.user1.user_id)
            assert set_response["assignees"] == [str(self.user2.user_id)]

            _current_topic_status = current_topic_status
            if current_topic_status is None:
                _current_topic_status = models.TopicStatusType.scheduled.value
            assert set_response["topic_status"] == _current_topic_status

            if need_scheduled_at:
                _scheduled_at = current_scheduled_at
            else:
                _scheduled_at = previous_scheduled_at
            assert set_response["scheduled_at"] == _scheduled_at

        def test_it_should_set_requester_if_assignee_is_not_specify_and_saved_current_user(
            self, actionable_topic1
        ):
            status_request = {
                "topic_status": models.TopicStatusType.completed.value,
                "note": "assign None",
            }
            url = (
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
                f"/ticketstatus/{self.ticket_id1}"
            )
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            response = client.put(url, headers=_headers, json=status_request)
            if response.status_code != 200:
                raise HTTPError(response)

            data = response.json()
            assert data["assignees"] == [str(self.user1.user_id)]


class TestGetTickets:

    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        self.user1 = create_user(USER1)
        self.user2 = create_user(USER2)
        self.pteam1 = create_pteam(USER1, PTEAM1)
        invitation1 = invite_to_pteam(USER1, self.pteam1.pteam_id)
        accept_pteam_invitation(USER2, invitation1.invitation_id)

        self.tag1 = create_tag(USER1, TAG1)
        # add test_service to pteam1
        test_service = "test_service"
        test_target = "test target"
        test_version = "1.2.3"
        refs0 = {self.tag1.tag_name: [(test_target, test_version)]}
        upload_pteam_tags(USER1, self.pteam1.pteam_id, test_service, refs0)
        self.service_id1 = self._get_service_id_by_service_name(
            USER1, self.pteam1.pteam_id, test_service
        )

    @pytest.fixture(scope="function", autouse=False)
    def actionable_topic1(self):
        action1 = self._gen_action([self.tag1.tag_name])
        self.topic1 = create_topic(
            USER1, {**TOPIC1, "tags": [self.tag1.tag_name], "actions": [action1]}
        )

    @pytest.fixture(scope="function", autouse=False)
    def not_actionable_topic1(self):
        self.topic1 = create_topic(USER1, {**TOPIC1, "tags": [self.tag1.tag_name], "actions": []})

    @staticmethod
    def _get_access_token(user: dict) -> str:
        body = {
            "username": user["email"],
            "password": user["pass"],
        }
        response = client.post("/auth/token", data=body)
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        return data["access_token"]

    @staticmethod
    def _get_service_id_by_service_name(user: dict, pteam_id: UUID | str, service_name: str) -> str:
        response = client.get(f"/pteams/{pteam_id}/services", headers=headers(user))
        if response.status_code != 200:
            raise HTTPError(response)
        data = response.json()
        service = next(filter(lambda x: x["service_name"] == service_name, data))
        return service["service_id"]

    @staticmethod
    def _gen_action(tag_names: list[str]) -> dict:
        return {
            "action": f"sample action for {str(tag_names)}",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": tag_names,
                "vulnerable_versions": {tag_name: ["<999.99.9"] for tag_name in tag_names},
            },
        }

    def _set_ticket_status(
        self, pteam_id: str, service_id: str, ticket_id: str, request: dict
    ) -> dict:
        url = f"/pteams/{pteam_id}/services/{service_id}/ticketstatus/{ticket_id}"
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        return client.put(url, headers=_headers, json=request).json()

    def test_returns_empty_if_no_tickets(self, not_actionable_topic1):
        url = (
            f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
            f"/topics/{self.topic1.topic_id}/tags/{self.tag1.tag_id}/tickets"
        )
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_ticket_with_initial_status_if_no_status_created(
        self, testdb, actionable_topic1
    ):
        db_dependency1 = testdb.scalars(select(models.Dependency)).one()
        db_threat1 = testdb.scalars(select(models.Threat)).one()
        db_ticket1 = testdb.scalars(select(models.Ticket)).one()
        db_status1 = testdb.scalars(select(models.TicketStatus)).one()
        expected_ticket_response1 = {
            "ticket_id": str(db_ticket1.ticket_id),
            "threat_id": str(db_threat1.threat_id),
            "created_at": datetime.isoformat(db_ticket1.created_at),
            "ssvc_deployer_priority": (
                None
                if db_ticket1.ssvc_deployer_priority is None
                else db_ticket1.ssvc_deployer_priority.value
            ),
            "threat": {
                "threat_id": str(db_threat1.threat_id),
                "topic_id": str(self.topic1.topic_id),
                "dependency_id": str(db_dependency1.dependency_id),
                "threat_safety_impact": (
                    str(db_threat1.threat_safety_impact.value)
                    if db_threat1.threat_safety_impact
                    else db_threat1.threat_safety_impact
                ),
            },
            "ticket_status": {
                "status_id": db_status1.status_id,  # do not check
                "ticket_id": str(db_ticket1.ticket_id),
                "topic_status": models.TopicStatusType.alerted.value,
                "user_id": None,
                "created_at": datetime.isoformat(db_status1.created_at),  # check later
                "assignees": [],
                "note": None,
                "scheduled_at": None,
                "action_logs": [],
            },
        }

        url = (
            f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
            f"/topics/{self.topic1.topic_id}/tags/{self.tag1.tag_id}/tickets"
        )
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        now = datetime.now()
        data = response.json()
        assert len(data) == 1
        ticket1 = data[0]
        assert ticket1 == expected_ticket_response1
        status1_created_at = datetime.fromisoformat(ticket1["ticket_status"]["created_at"])
        assert now - timedelta(seconds=10) < status1_created_at < now

    def test_returns_ticket_with_current_status_if_status_created(self, testdb, actionable_topic1):
        db_dependency1 = testdb.scalars(select(models.Dependency)).one()
        db_threat1 = testdb.scalars(select(models.Threat)).one()
        db_ticket1 = testdb.scalars(select(models.Ticket)).one()
        status_request = {
            "topic_status": models.TopicStatusType.scheduled.value,
            "assignees": [str(self.user2.user_id)],
            "note": "assign user2 and schedule at 2345/6/7",
            "scheduled_at": "2345-06-07T08:09:10",
        }
        self._set_ticket_status(
            self.pteam1.pteam_id, self.service_id1, db_ticket1.ticket_id, status_request
        )

        db_ticket_status1 = testdb.scalars(select(models.TicketStatus)).one()
        expected_ticket_response1 = {
            "ticket_id": str(db_ticket1.ticket_id),
            "threat_id": str(db_threat1.threat_id),
            "created_at": datetime.isoformat(db_ticket1.created_at),
            "ssvc_deployer_priority": (
                None
                if db_ticket1.ssvc_deployer_priority is None
                else db_ticket1.ssvc_deployer_priority.value
            ),
            "threat": {
                "threat_id": str(db_threat1.threat_id),
                "topic_id": str(self.topic1.topic_id),
                "dependency_id": str(db_dependency1.dependency_id),
                "threat_safety_impact": (
                    str(db_threat1.threat_safety_impact.value)
                    if db_threat1.threat_safety_impact
                    else db_threat1.threat_safety_impact
                ),
            },
            "ticket_status": {
                "status_id": str(db_ticket_status1.status_id),
                "ticket_id": str(db_ticket1.ticket_id),
                "user_id": str(self.user1.user_id),
                "created_at": datetime.isoformat(db_ticket_status1.created_at),
                "action_logs": [],
                **status_request,
            },
        }

        url = (
            f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}"
            f"/topics/{self.topic1.topic_id}/tags/{self.tag1.tag_id}/tickets"
        )
        user1_access_token = self._get_access_token(USER1)
        _headers = {
            "Authorization": f"Bearer {user1_access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        response = client.get(url, headers=_headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        ticket1 = data[0]
        assert ticket1 == expected_ticket_response1


class TestUpdatePTeamService:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            self.tag1 = create_tag(USER1, TAG1)
            test_service = "test_service"
            test_target = "test target"
            test_version = "1.2.3"
            refs0 = {self.tag1.tag_name: [(test_target, test_version)]}
            upload_pteam_tags(USER1, self.pteam1.pteam_id, test_service, refs0)
            self.service_id1 = get_service_by_service_name(
                USER1, self.pteam1.pteam_id, test_service
            )["service_id"]

        @staticmethod
        def _get_access_token(user: dict) -> str:
            body = {
                "username": user["email"],
                "password": user["pass"],
            }
            response = client.post("/auth/token", data=body)
            if response.status_code != 200:
                raise HTTPError(response)
            data = response.json()
            return data["access_token"]

    class TestKeywords(Common):
        @pytest.mark.parametrize(
            "keywords, expected",
            [
                (None, "Cannot specify None for keywords"),
                ([], []),
                (["1"], ["1"]),
                (["1", "2"], ["1", "2"]),
                (["3", "1", "2"], ["1", "2", "3"]),
                (["2", "4", "1", "3"], ["1", "2", "3", "4"]),
                (["1", "2", "3", "4", "5"], ["1", "2", "3", "4", "5"]),
                (["1", "2", "3", "4", "5", "6"], "Too many keywords, max number: 5"),
                (["1", "2", "3", "3", "1", "2"], ["1", "2", "3"]),  # duplications are unified
            ],
        )
        def test_number_of_keywords(self, keywords, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": keywords}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, str):  # error cases
                assert response.status_code == 400
                assert response.json()["detail"] == expected
            else:
                assert response.status_code == 200
                assert response.json()["keywords"] == expected

        error_too_long_keyword = (
            "Too long keyword. Max length is 20 in half-width or 10 in full-width"
        )
        chars_20_in_half = "123456789_123456789_"
        chars_10_in_full = "１２３４５６７８９０"
        complex_20_in_half = "123456789_１２３４５"

        @pytest.mark.parametrize(
            "keyword, expected",
            [
                ("", []),
                ("   ", []),
                (chars_20_in_half, [chars_20_in_half]),
                (" " + chars_20_in_half + " ", [chars_20_in_half]),
                (chars_20_in_half + "x", error_too_long_keyword),
                (chars_10_in_full, [chars_10_in_full]),
                (" " + chars_10_in_full + " ", [chars_10_in_full]),
                ("　" + chars_10_in_full + "　", [chars_10_in_full]),  # \u3000 is also stripped
                (chars_10_in_full + "x", error_too_long_keyword),
                (chars_10_in_full + "ｘ", error_too_long_keyword),
                (complex_20_in_half, [complex_20_in_half]),
                (" " + complex_20_in_half + " ", [complex_20_in_half]),
                ("　" + complex_20_in_half + "　", [complex_20_in_half]),
                (complex_20_in_half + "x", error_too_long_keyword),
                (complex_20_in_half + "ｘ", error_too_long_keyword),
            ],
        )
        def test_length_of_keyword(self, keyword, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": [keyword]}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, str):  # error cases
                assert response.status_code == 400
                assert response.json()["detail"] == expected
            else:
                assert response.status_code == 200
                assert response.json()["keywords"] == expected

        def test_it_should_return_200_when_keyword_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": "keywords not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["keywords"] == []

    class TestDescription(Common):

        error_too_long_description = (  # HACK: define as a tuple instead of str
            "Too long description. Max length is 300 in half-width or 150 in full-width",
        )
        chars_300_in_half = "123456789_" * 30
        chars_150_in_full = "１２３４５６７８９＿" * 15
        complex_300_in_half = "123456789_１２３４５６７８９＿" * 10

        @pytest.mark.parametrize(
            "description, expected",
            [
                (None, None),
                ("", None),
                ("   ", None),
                (chars_300_in_half, chars_300_in_half),
                (chars_300_in_half + "  ", chars_300_in_half),
                (chars_300_in_half + "x", error_too_long_description),
                (chars_150_in_full, chars_150_in_full),
                (chars_150_in_full + " ", chars_150_in_full),
                (chars_150_in_full + "　", chars_150_in_full),
                (chars_150_in_full + "ｘ", error_too_long_description),
                (complex_300_in_half, complex_300_in_half),
                (complex_300_in_half + " ", complex_300_in_half),
                (complex_300_in_half + "　", complex_300_in_half),
                (complex_300_in_half + "x", error_too_long_description),
                (complex_300_in_half + "ｘ", error_too_long_description),
            ],
        )
        def test_length_of_description(self, description, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": description}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, tuple):  # error case
                assert response.status_code == 400
                assert response.json()["detail"] == expected[0]
            else:
                assert response.status_code == 200
                assert response.json()["description"] == expected

        def test_it_should_return_200_when_description_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": []}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["description"] is None

    class TestSystemExposure(Common):
        @pytest.mark.parametrize(
            "system_exposure, expected",
            [
                ("open", models.SystemExposureEnum.OPEN),
                ("controlled", models.SystemExposureEnum.CONTROLLED),
                ("small", models.SystemExposureEnum.SMALL),
            ],
        )
        def test_it_should_return_200_when_system_exposure_is_SystemExposureEnum(
            self, system_exposure, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"system_exposure": system_exposure}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["system_exposure"] == expected

        def test_it_should_return_200_when_system_exposure_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"description": "system_exposure not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["system_exposure"] == models.SystemExposureEnum.OPEN

        error_msg_system_exposure = "Input should be 'open', 'controlled' or 'small'"

        def test_it_should_return_400_when_system_exposure_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"system_exposure": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for system_exposure"

        @pytest.mark.parametrize(
            "system_exposure, expected",
            [
                (1, error_msg_system_exposure),
                ("test", error_msg_system_exposure),
            ],
        )
        def test_it_should_return_422_when_system_exposure_is_not_SystemExposureEnum(
            self, system_exposure, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"system_exposure": system_exposure}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected

    class TestMissionImpact(Common):
        @pytest.mark.parametrize(
            "service_mission_impact, expected",
            [
                ("mission_failure", models.MissionImpactEnum.MISSION_FAILURE),
                ("mef_failure", models.MissionImpactEnum.MEF_FAILURE),
                ("mef_support_crippled", models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED),
                ("degraded", models.MissionImpactEnum.DEGRADED),
            ],
        )
        def test_it_should_return_200_when_mission_impact_is_MissionImpactEnum(
            self, service_mission_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_mission_impact": service_mission_impact}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_mission_impact"] == expected

        def test_it_should_return_200_when_mission_impact_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"description": "service_mission_impact not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            assert (
                response.json()["service_mission_impact"]
                == models.MissionImpactEnum.MISSION_FAILURE
            )

        error_msg_service_mission_impact = (
            "Input should be 'mission_failure', 'mef_failure', 'mef_support_crippled' or 'degraded'"
        )

        def test_it_should_return_400_when_mission_impact_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_mission_impact": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for service_mission_impact"

        @pytest.mark.parametrize(
            "service_mission_impact, expected",
            [
                (
                    1,
                    error_msg_service_mission_impact,
                ),
                (
                    "test",
                    error_msg_service_mission_impact,
                ),
            ],
        )
        def test_it_should_return_422_when_mission_impact_is_not_MissionImpactEnum(
            self, service_mission_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_mission_impact": service_mission_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected

    class TestSafetyImpactEnum(Common):
        @pytest.mark.parametrize(
            "safety_impact, expected",
            [
                ("catastrophic", models.SafetyImpactEnum.CATASTROPHIC),
                ("critical", models.SafetyImpactEnum.CRITICAL),
                ("marginal", models.SafetyImpactEnum.MARGINAL),
                ("negligible", models.SafetyImpactEnum.NEGLIGIBLE),
            ],
        )
        def test_it_should_return_200_when_safety_impact_is_SafetyImpactEnum(
            self, safety_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_safety_impact": safety_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_safety_impact"] == expected

        def test_it_should_return_200_when_safety_impact_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": "safety_impact not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            assert response.json()["service_safety_impact"] == models.SafetyImpactEnum.NEGLIGIBLE

        def test_it_should_return_400_when_safety_impact_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_safety_impact": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for safety_impact"

        error_msg_safety_impact = (
            "Input should be 'catastrophic', 'critical', 'marginal' or 'negligible'"
        )

        @pytest.mark.parametrize(
            "safety_impact, expected",
            [
                (1, error_msg_safety_impact),
                ("test", error_msg_safety_impact),
            ],
        )
        def test_it_should_return_422_when_safety_impact_is_not_SafetyImpactEnum(
            self, safety_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_safety_impact": safety_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected

    class TestNotification:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            def _gen_pteam_params(idx: int) -> dict:
                return {
                    "pteam_name": f"pteam{idx}",
                    "alert_slack": {
                        "enable": True,
                        "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
                    },
                    "alert_mail": {
                        "enable": True,
                        "address": f"account{idx}@example.com",
                    },
                    "alert_ssvc_priority": "out_of_cycle",
                }

            def _gen_topic_params(tags: list[schemas.TagResponse]) -> dict:
                topic_id = str(uuid4())
                return {
                    "topic_id": topic_id,
                    "title": "test topic " + topic_id,
                    "abstract": "test abstract " + topic_id,
                    "threat_impact": 1,
                    "tags": [tag.tag_name for tag in tags],
                    "misp_tags": [],
                    "actions": [
                        {
                            "topic_id": topic_id,
                            "action": "update to 999.9.9",
                            "action_type": models.ActionType.elimination,
                            "recommended": True,
                            "ext": {
                                "tags": [tag.tag_name for tag in tags],
                                "vulnerable_versions": {
                                    tag.tag_name: ["< 999.9.9"] for tag in tags
                                },
                            },
                        },
                    ],
                    "exploitation": "active",
                    "automatable": "yes",
                }

            self.user1 = create_user(USER1)
            self.pteam0 = create_pteam(USER1, _gen_pteam_params(0))
            self.tag1 = create_tag(USER1, TAG1)
            test_service0 = "test_service0"
            test_target = "test target"
            test_version = "1.2.3"
            refs0 = {self.tag1.tag_name: [(test_target, test_version)]}
            upload_pteam_tags(USER1, self.pteam0.pteam_id, test_service0, refs0)
            self.service_id0 = get_service_by_service_name(
                USER1, self.pteam0.pteam_id, test_service0
            )["service_id"]
            self.topic = create_topic(USER1, _gen_topic_params([self.tag1]))

        @staticmethod
        def _get_access_token(user: dict) -> str:
            body = {
                "username": user["email"],
                "password": user["pass"],
            }
            response = client.post("/auth/token", data=body)
            if response.status_code != 200:
                raise HTTPError(response)
            data = response.json()
            return data["access_token"]

        def test_alert_by_mail_if_vulnerabilities_are_found_when_updating_service(
            self, mocker, testdb: Session
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            ## ssvc_deployer_priority is out_of_cycle
            request = {
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.CRITICAL.value,
            }

            send_alert_to_pteam = mocker.patch("app.business.ticket_business.send_alert_to_pteam")
            response = client.put(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200

            ## get ticket_id
            response_ticket = client.get(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}/topics/{self.topic.topic_id}/tags/{self.tag1.tag_id}/tickets",
                headers=_headers,
            )
            ticket_id = response_ticket.json()[0]["ticket_id"]

            alerts = testdb.scalars(
                select(models.Alert)
                .where(models.Alert.ticket_id == str(ticket_id))
                .order_by(models.Alert.alerted_at.desc())
            ).all()

            assert alerts

            assert alerts[0].ticket.threat.topic_id == str(self.topic.topic_id)

            send_alert_to_pteam.assert_called_once()
            send_alert_to_pteam.assert_called_with(alerts[0])

        def test_not_alert_by_mail_if_unchange_ssvc_priority_when_updating_service(
            self, mocker, testdb: Session
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            ## ssvc_deployer_priority is immediate
            request = {
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "service_safety_impact": models.SafetyImpactEnum.CATASTROPHIC.value,
            }

            send_alert_to_pteam = mocker.patch("app.business.ticket_business.send_alert_to_pteam")
            response = client.put(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            send_alert_to_pteam.assert_not_called()

        def test_not_alert_with_ticket_status_is_completed(self, mocker):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            ## Change the status of the ticket to completed
            response_ticket = client.get(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}/topics/{self.topic.topic_id}/tags/{self.tag1.tag_id}/tickets",
                headers=_headers,
            )
            assert response_ticket.status_code == 200
            data = response_ticket.json()
            request_ticket_status = {"topic_status": models.TopicStatusType.completed.value}
            response_ticket_status = client.put(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}/ticketstatus/{data[0]['ticket_id']}",
                headers=_headers,
                json=request_ticket_status,
            )
            assert response_ticket_status.status_code == 200

            ## ssvc_deployer_priority is immediate
            request = {
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "safety_impact": models.SafetyImpactEnum.CATASTROPHIC.value,
            }
            send_alert_to_pteam = mocker.patch("app.business.ticket_business.send_alert_to_pteam")
            response = client.put(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            send_alert_to_pteam.assert_not_called()

        def test_not_alert_when_ssvc_deployer_priority_is_lower_than_alert_ssvc_priority_in_pteam(
            self, mocker
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            ## ssvc_deployer_priority is scheduled
            request = {
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            }

            send_alert_to_pteam = mocker.patch("app.business.ticket_business.send_alert_to_pteam")
            response = client.put(
                f"/pteams/{self.pteam0.pteam_id}/services/{self.service_id0}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            send_alert_to_pteam.assert_not_called()
