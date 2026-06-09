from fastapi.testclient import TestClient

from app.main import app
from app.tests.common.auth_utils import get_access_token, refresh_access_token
from app.tests.common.constants import USER1

client = TestClient(app)


class TestLoginForAccessToken:
    def test_login_user1(self):
        response = get_access_token(USER1["email"], USER1["pass"])
        assert response["access_token"]
        assert response["token_type"].lower() == "bearer"
        assert response["refresh_token"]


class TestRefreshAccessToken:
    def test_refresh_token(self):
        # Given
        old = get_access_token(USER1["email"], USER1["pass"])

        # When
        new = refresh_access_token(old["refresh_token"])

        # Then
        assert new["access_token"]
        assert new["token_type"].lower() == "bearer"
        assert new["refresh_token"]

        # When
        refreshed = refresh_access_token(new["refresh_token"])

        # Then
        assert refreshed["access_token"]
        assert refreshed["token_type"].lower() == "bearer"
        assert refreshed["refresh_token"]
