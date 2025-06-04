from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import (
    DEFAULT_ALERT_SSVC_PRIORITY,
    ZERO_FILLED_UUID,
)
from app.main import app
from app.tests.common import ticket_utils
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
    USER3,
    VULN1,
)
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_pteam,
    create_user,
    file_upload_headers,
    headers,
    invite_to_pteam,
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
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in user_me["pteam_roles"]} == {
        pteam1.pteam_id
    }

    pteam2 = create_pteam(USER1, PTEAM2)
    assert pteam2.pteam_name == PTEAM2["pteam_name"]
    assert pteam2.contact_info == PTEAM2["contact_info"]
    assert pteam2.alert_slack.webhook_url == PTEAM2["alert_slack"]["webhook_url"]
    assert pteam2.alert_ssvc_priority == PTEAM2["alert_ssvc_priority"]
    assert pteam2.pteam_id != ZERO_FILLED_UUID

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    user_me = response.json()
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in user_me["pteam_roles"]} == {
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


def test_it_should_return_401_when_create_pteam_without_auth():
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


def test_it_should_return_403_when_update_pteam_by_not_admin():
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


def test_it_should_return_400_when_try_delete_last_admin():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get("/users/me", headers=headers(USER1))
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user1.user_id)
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in data["pteam_roles"]} == {pteam1.pteam_id}

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
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in data["pteam_roles"]} == {pteam1.pteam_id}

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
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in data["pteam_roles"]} == {pteam1.pteam_id}

    # invite another member (not ADMIN)
    user2 = create_user(USER2)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    # make the other member ADMIN
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
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
    assert data["pteam_roles"] == []

    # user1 does not belong to pteam1
    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER2))
    assert response.status_code == 200
    members_map = {UUID(x["user_id"]): x for x in response.json()}
    assert members_map.get(user1.user_id) is None


def test_delete_member__by_admin():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    user3 = create_user(USER3)
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
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}",
        headers=headers(USER1),
        json={"is_admin": True},
    )

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
    assert {UUID(pteam["pteam"]["pteam_id"]) for pteam in members[0]["pteam_roles"]} == {
        pteam1.pteam_id
    }
    assert {pteam["is_admin"] for pteam in members[0]["pteam_roles"]} == {True}

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
        {
            UUID(p["pteam"]["pteam_id"])
            for p in members_map.get(user1.user_id).get("pteam_roles", [])
        }
        == {
            UUID(p["pteam"]["pteam_id"])
            for p in members_map.get(user2.user_id).get("pteam_roles", [])
        }
        == {pteam1.pteam_id}
    )
    assert {
        pteam["is_admin"] for pteam in members_map.get(user1.user_id).get("pteam_roles", [])
    } == {True}
    assert {
        pteam["is_admin"] for pteam in members_map.get(user2.user_id).get("pteam_roles", [])
    } == {False}


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
        {
            UUID(p["pteam"]["pteam_id"])
            for p in members_map.get(user1.user_id).get("pteam_roles", [])
        }
        == {
            UUID(p["pteam"]["pteam_id"])
            for p in members_map.get(user2.user_id).get("pteam_roles", [])
        }
        == {pteam1.pteam_id}
    )
    assert {
        pteam["is_admin"] for pteam in members_map.get(user1.user_id).get("pteam_roles", [])
    } == {True}
    assert {
        pteam["is_admin"] for pteam in members_map.get(user2.user_id).get("pteam_roles", [])
    } == {False}


def test_test_it_should_return_when_get_pteam_members_by_not_member():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    response = client.get(f"/pteams/{pteam1.pteam_id}/members", headers=headers(USER2))
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"


def test_it_should_return_200_when_admin_updates_pteam_members():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER1), json=request
    )
    assert response.status_code == 200
    assert response.json()["pteam_id"] == str(pteam1.pteam_id)
    assert response.json()["user_id"] == str(user2.user_id)
    assert response.json()["is_admin"] == request["is_admin"]


def test_it_should_return_200_when_admin_updates_itself():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request1 = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER1), json=request1
    )
    assert response.status_code == 200

    request2 = {"is_admin": False}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER2), json=request2
    )
    assert response.status_code == 200
    assert response.json()["pteam_id"] == str(pteam1.pteam_id)
    assert response.json()["user_id"] == str(user2.user_id)
    assert response.json()["is_admin"] == request2["is_admin"]


def test_it_should_return_403_when_no_admin_update_pteam_members():
    create_user(USER1)
    create_user(USER2)
    user3 = create_user(USER3)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER3, invitation.invitation_id)

    request = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user3.user_id}", headers=headers(USER2), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.json()["detail"] == "You do not have authority"


def test_it_should_return_403_when_no_admin_update_itself():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER2), json=request
    )
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.json()["detail"] == "You do not have authority"


def test_it_should_return_403_when_admin_update_no_members():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user2.user_id}", headers=headers(USER1), json=request
    )

    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.json()["detail"] == "Not a pteam member"


def test_it_should_return_403_when_outsider_try_update_pteam_members():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {"is_admin": True}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER2), json=request
    )

    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.json()["detail"] == "You do not have authority"


def test_it_should_return_400_when_try_to_remove_last_admin():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = {"is_admin": False}
    response = client.put(
        f"/pteams/{pteam1.pteam_id}/members/{user1.user_id}", headers=headers(USER1), json=request
    )
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Removing last ADMIN is not allowed"


class TestDeletePteam:
    @pytest.fixture(scope="function")
    def pteam_setup(self, testdb: Session):
        service_name1 = "test_service1"
        ticket_response = ticket_utils.create_ticket(testdb, USER1, PTEAM1, service_name1, VULN1)
        created_pteam_id = ticket_response["pteam_id"]
        created_service_id = ticket_response["service_id"]

        dependencies_response = client.get(
            f"/pteams/{created_pteam_id}/dependencies?service_id={created_service_id}",
            headers=headers(USER1),
        )
        created_dependency = dependencies_response.json()[0]

        image_filepath = (
            Path(__file__).resolve().parent.parent / "upload_test" / "image" / "yes_image.png"
        )
        with open(image_filepath, "rb") as image_file:
            client.post(
                f"/pteams/{created_pteam_id}/services/{created_service_id}/thumbnail",
                headers=file_upload_headers(USER1),
                files={"uploaded": image_file},
            )

        return {
            "pteam_id": ticket_response["pteam_id"],
            "service_id": ticket_response["service_id"],
            "dependency_id": created_dependency["dependency_id"],
            "threat_id": ticket_response["threat_id"],
            "ticket_id": ticket_response["ticket_id"],
        }

    def test_delete_pteam_if_user_is_pteam_admin(self, testdb: Session, pteam_setup):
        # delete pteam
        pteam_id = pteam_setup["pteam_id"]
        delete_pteam_response = client.delete(
            f"/pteams/{pteam_id}",
            headers=headers(USER1),
        )
        assert delete_pteam_response.status_code == 204

        # check deleted_pteam
        deleted_pteam = testdb.scalars(
            select(models.PTeam).where(models.PTeam.pteam_id == pteam_setup["pteam_id"])
        ).one_or_none()
        deleted_pteam_account_role = testdb.scalars(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.pteam_id == pteam_setup["pteam_id"]
            )
        ).one_or_none()
        deleted_pteam_slack = testdb.scalars(
            select(models.PTeamSlack).where(models.PTeamSlack.pteam_id == pteam_setup["pteam_id"])
        ).one_or_none()
        deleted_pteam_mail = testdb.scalars(
            select(models.PTeamMail).where(models.PTeamMail.pteam_id == pteam_setup["pteam_id"])
        ).one_or_none()
        deleted_service = testdb.scalars(
            select(models.Service).where(models.Service.service_id == pteam_setup["service_id"])
        ).one_or_none()
        deleted_service_thumbnail = testdb.scalars(
            select(models.ServiceThumbnail).where(
                models.ServiceThumbnail.service_id == pteam_setup["service_id"]
            )
        ).one_or_none()
        deleted_dependency = testdb.scalars(
            select(models.Dependency).where(
                models.Dependency.dependency_id == pteam_setup["dependency_id"]
            )
        ).one_or_none()
        deleted_threat = testdb.scalars(
            select(models.Threat).where(models.Threat.threat_id == pteam_setup["threat_id"])
        ).one_or_none()
        deleted_ticket = testdb.scalars(
            select(models.Ticket).where(models.Ticket.ticket_id == pteam_setup["ticket_id"])
        ).one_or_none()
        deleted_ticket_status = testdb.scalars(
            select(models.TicketStatus).where(
                models.TicketStatus.ticket_id == pteam_setup["ticket_id"]
            )
        ).one_or_none()

        assert deleted_pteam is None
        assert deleted_pteam_account_role is None
        assert deleted_pteam_slack is None
        assert deleted_pteam_mail is None
        assert deleted_service is None
        assert deleted_service_thumbnail is None
        assert deleted_dependency is None
        assert deleted_threat is None
        assert deleted_ticket is None
        assert deleted_ticket_status is None

    def test_raise_403_if_user_is_not_pteam_admin(self, pteam_setup):
        create_user(USER2)
        pteam_id = pteam_setup["pteam_id"]

        # delete pteam
        delete_pteam_response = client.delete(
            f"/pteams/{pteam_id}",
            headers=headers(USER2),
        )

        assert delete_pteam_response.status_code == 403
        assert delete_pteam_response.json()["detail"] == "You do not have authority"

    def test_raise_404_if_invalid_pteam_id(self, pteam_setup):
        wrong_pteam_id = str(uuid4())

        # delete pteam
        delete_pteam_response = client.delete(
            f"/pteams/{wrong_pteam_id}",
            headers=headers(USER1),
        )

        assert delete_pteam_response.status_code == 404
        assert delete_pteam_response.json()["detail"] == "No such pteam"
