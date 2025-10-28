import pytest
from fastapi.testclient import TestClient

from app import models, persistence
from app.constants import ZERO_FILLED_UUID
from app.main import app
from app.tests.medium.constants import PTEAM1, PTEAM2, USER1, USER2
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    create_pteam,
    create_user,
    headers,
    judge_whether_firebase_or_supabase,
)

client = TestClient(app)


class TestGetMyUserInfo:
    def test_get_my_user_with_refresh(self):
        # Given
        user1 = create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        request1 = {"favorite_pteam_id": str(pteam1.pteam_id)}
        client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request1)

        # When
        response = client.get("/users/me", headers=headers(USER1))

        # Then
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == USER1["email"]
        assert user["uid"] == user1.uid
        assert user["disabled"] == USER1["disabled"]
        assert user["years"] == USER1["years"]
        assert user["favorite_pteam_id"] == str(pteam1.pteam_id)


class TestCreateUser:
    def test_create_user(self):
        user1 = create_user(USER1)
        assert user1.email == USER1["email"]
        assert user1.years == USER1["years"]
        assert user1.user_id != ZERO_FILLED_UUID

    def test_it_should_return_400_when_create_user_with_duplicate_email(self, testdb):
        email = USER1["email"]
        years = USER1["years"]
        account = models.Account(uid="test_uid1", email=email, years=years)
        persistence.create_account(testdb, account)

        request = {"years": years}
        response = client.post("/users", headers=headers(USER1), json=request)
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "This email address is already in use. "
            "You'll need to use a different email to sign up."
        )

    def test_duplicate_user(self):
        create_user(USER1)
        with pytest.raises(HTTPError, match="400: Bad Request"):
            create_user(USER1)  # duplicate

    def test_create_user_without_auth(self):
        response = client.post("/users", json={})  # no headers
        assert response.status_code == 401


class TestUpdateUser:
    def test_update_user_by_another_user(self):
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
        self, field_name, expected_response_detail
    ):
        user1 = create_user(USER1)
        request = {field_name: None}
        response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)
        assert response.status_code == 400
        assert response.json()["detail"] == expected_response_detail

    def test_it_should_return_400_when_favorite_pteam_id_does_not_exist(self):
        # Given
        user1 = create_user(USER1)

        # When
        request = {"favorite_pteam_id": "123e4567-e89b-12d3-a456-426614174000"}
        response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "pteam_id does not exist"

    def test_it_should_return_400_when_user_is_not_a_member_of_the_pteam(self):
        # Given
        create_user(USER1)
        user2 = create_user(USER2)
        pteam1 = create_pteam(USER1, PTEAM1)

        # When
        request = {"favorite_pteam_id": str(pteam1.pteam_id)}
        response = client.put(f"/users/{user2.user_id}", headers=headers(USER2), json=request)

        # Then
        assert response.status_code == 400
        assert response.json()["detail"] == "User is not a member of the PTeam"

    def test_it_should_return_200_when_correct_request(self):
        # Given
        user1 = create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)

        # When
        request = {"favorite_pteam_id": str(pteam1.pteam_id), "years": 10, "disabled": True}
        response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["favorite_pteam_id"] == str(pteam1.pteam_id)
        assert data["years"] == 10
        assert data["disabled"] is True

    def test_it_should_return_200_when_the_favorite_pteam_id_is_changed_twice(self):
        # Given
        user1 = create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        pteam2 = create_pteam(USER1, PTEAM2)

        # When
        request1 = {"favorite_pteam_id": str(pteam1.pteam_id)}
        client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request1)
        request2 = {"favorite_pteam_id": str(pteam2.pteam_id)}
        response = client.put(f"/users/{user1.user_id}", headers=headers(USER1), json=request2)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["favorite_pteam_id"] == str(pteam2.pteam_id)


class TestDeleteUser:
    def test_delete_user(self, mocker):
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
