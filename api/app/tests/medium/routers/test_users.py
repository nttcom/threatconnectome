import pytest
from fastapi.testclient import TestClient

from app import models, persistence
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import USER1, USER2
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.routers.test_auth import (
    get_access_token,
    refresh_access_token,
    refresh_headers,
)
from app.tests.medium.utils import create_user, headers, judge_whether_firebase_or_supabase

client = TestClient(app)


def test_create_user():
    user1 = create_user(USER1)
    assert user1.email == USER1["email"]
    assert user1.years == USER1["years"]
    assert user1.user_id != ZERO_FILLED_UUID


def test_it_should_return_400_when_create_user_with_duplicate_email(testdb):
    email = USER1["email"]
    years = USER1["years"]
    account = models.Account(uid="test_uid1", email=email, years=years)
    persistence.create_account(testdb, account)

    request = {"years": years}
    response = client.post("/users", headers=headers(USER1), json=request)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "This email address is already in use. You'll need to use a different email to sign up."
    )


def test_duplicate_user():
    create_user(USER1)
    with pytest.raises(HTTPError, match="400: Bad Request"):
        create_user(USER1)  # duplicate


def test_create_user_without_auth():
    response = client.post("/users", json={})  # no headers
    assert response.status_code == 401
    assert response.reason_phrase == "Unauthorized"


def test_login_user1():
    response = get_access_token(USER1["email"], USER1["pass"])
    assert response["access_token"]
    assert response["token_type"].lower() == "bearer"
    assert response["refresh_token"]


def test_refresh_token():
    old = get_access_token(USER1["email"], USER1["pass"])
    new = refresh_access_token(old["refresh_token"])
    assert new["access_token"]
    assert new["token_type"].lower() == "bearer"
    assert new["refresh_token"] == old["refresh_token"]


def test_delete_user(mocker):
    create_user(USER1)
    module = judge_whether_firebase_or_supabase()
    delete_user = mocker.patch.object(
        module,
        "delete_user",
    )
    response1 = client.delete("/users/me", headers=headers(USER1))
    delete_user.assert_called_once()
    assert response1.status_code == 204
    response2 = client.get("/users/me", headers=headers(USER1))
    assert response2.status_code == 404


def test_get_my_user_with_refresh():
    user1 = create_user(USER1)
    old = get_access_token(USER1["email"], USER1["pass"])
    _headers = refresh_headers(old["refresh_token"])
    response = client.get("/users/me", headers=_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == USER1["email"]
    assert user["uid"] == user1.uid
    assert user["disabled"] == USER1["disabled"]
    assert user["years"] == USER1["years"]


def test_update_user_by_another_user():
    create_user(USER1)
    user2 = create_user(USER2)

    request = {"years": 2}

    response = client.put(f"/users/{user2.user_id}", headers=headers(USER1), json=request)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Information can only be updated by user himself"


@pytest.mark.parametrize(
    "field_name, expected_response_detail",
    [
        ("disabled", "Cannot specify None for disabled"),
        ("years", "Cannot specify None for years"),
    ],
)
def test_update_user_should_return_400_when_required_fields_is_None(
    field_name, expected_response_detail
):
    user1 = create_user(USER1)
    request = {field_name: None}
    response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)
    assert response.status_code == 400
    assert response.json()["detail"] == expected_response_detail
