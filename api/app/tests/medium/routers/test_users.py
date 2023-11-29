from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import BADGE1, METADATA1, PTEAM1, USER1, USER2
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.routers.test_auth import (
    get_access_token,
    refresh_access_token,
    refresh_headers,
)
from app.tests.medium.utils import create_badge, create_pteam, create_user, headers

client = TestClient(app)


def test_create_user():
    user1 = create_user(USER1)
    assert user1.email == USER1["email"]
    assert user1.years == USER1["years"]
    assert user1.user_id != ZERO_FILLED_UUID
    assert user1.favorite_badge is None


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


def test_delete_user():
    create_user(USER1)
    response1 = client.delete("/users", headers=headers(USER1))
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


def test_update_user_with_favorite_badge():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    badge1 = create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    request = {"favorite_badge": str(badge1.badge_id)}

    response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["favorite_badge"] == badge1.badge_id

    # clear favorite badge
    request = {"favorite_badge": ""}
    response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)
    data = response.json()
    assert data["favorite_badge"] is None


def test_update_user_with_invalid_favorite_badge():
    wrong_uuid = uuid4()
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    request = {"favorite_badge": str(wrong_uuid)}

    response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == f"no such secbadge: {str(wrong_uuid)}"
