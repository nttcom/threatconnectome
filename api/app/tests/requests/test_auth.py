from fastapi.testclient import TestClient

from app.main import app
from app.tests.common.auth_utils import get_access_token, refresh_access_token
from app.tests.medium.constants import USER1

client = TestClient(app)


class TestLoginForAccessToken:
    def test_login_user1(self):
        response = get_access_token(USER1["email"], USER1["pass"])
        assert response["access_token"]
        assert response["token_type"].lower() == "bearer"
        assert response["refresh_token"]


class TestRefreshAccessToken:
    def test_refresh_token(self):
        old = get_access_token(USER1["email"], USER1["pass"])
        new = refresh_access_token(old["refresh_token"])
        assert new["access_token"]
        assert new["token_type"].lower() == "bearer"
        assert new["refresh_token"] == old["refresh_token"]
