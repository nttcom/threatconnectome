import json
import os

import requests
from firebase_admin import auth, credentials, initialize_app

from app.auth.auth_exception import AuthErrorType, AuthException
from app.auth.auth_module import AuthModule

from ..schemas import Token


class FirebaseAuthModule(AuthModule):
    def __init__(self):
        super().__init__()
        self.cred = credentials.Certificate(os.environ["FIREBASE_CRED"])
        initialize_app(self.cred)

    def login_for_access_token(self, username, password) -> tuple[Token, str | None]:
        payload = {
            "email": username,
            "password": password.get_secret_value(),
            "returnSecureToken": True,
        }

        api_key = os.getenv("FIREBASE_API_KEY", "")
        # https://github.com/firebase/firebase-admin-python/blob/master/firebase_admin/_auth_utils.py
        id_toolkit = "identitytoolkit.googleapis.com/v1"
        sign_in_url_without_scheme = f"{id_toolkit}/accounts:signInWithPassword?key={api_key}"
        emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
        if emulator_host != "":
            sign_in_url = f"http://{emulator_host}/{sign_in_url_without_scheme}"
        else:
            sign_in_url = f"https://{sign_in_url_without_scheme}"

        try:
            resp = requests.post(
                sign_in_url,
                json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
        except requests.exceptions.Timeout as firebase_timeout:
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Could not validate credentials"
            ) from firebase_timeout

        data = resp.json()
        if not resp.ok:
            error_message = data["error"]["message"]
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                error_message if error_message else "Could not validate credentials",
            )
        return (
            Token(
                access_token=data["idToken"],
                token_type="bearer",
                refresh_token=data["refreshToken"],
            ),
            data["localId"],
        )

    def refresh_access_token(self, refresh_token) -> tuple[Token, str | None]:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        # see https://firebase.google.com/docs/reference/rest/auth#section-refresh-token
        api_key = os.environ["FIREBASE_API_KEY"]
        refresh_path = f"securetoken.googleapis.com/v1/token?key={api_key}"
        emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
        if emulator_host != "":
            refresh_token_url = f"http://{emulator_host}/{refresh_path}"
        else:
            refresh_token_url = f"https://{refresh_path}"

        try:
            resp = requests.post(
                refresh_token_url,
                json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
        except requests.exceptions.Timeout as firebase_timeout:
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR,
                "Could not refresh token",
            ) from firebase_timeout

        data: dict = resp.json()
        if not resp.ok:
            error_message: str = data["error"]["message"]
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                error_message if error_message else "Could not refresh token",
            )
        return (
            Token(
                access_token=data["id_token"],
                token_type=data["token_type"],
                refresh_token=data["refresh_token"],
            ),
            data["user_id"],
        )

    def check_and_get_user_info(self, token):
        super().check_token(token)
        try:
            decoded_token = auth.verify_id_token(token.credentials, check_revoked=True)
        except auth.ExpiredIdTokenError as error:
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                "Token has expired",
            ) from error
        except auth.RevokedIdTokenError as error:
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                "Token has revoked",
            ) from error
        except auth.CertificateFetchError as error:
            raise AuthException(
                AuthErrorType.SERVICE_UNAVAILABLE,
                "Failed to obtain required credentials",
            ) from error
        except auth.UserDisabledError as error:
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                "Disabled user",
            ) from error
        except (auth.InvalidIdTokenError, ValueError) as error:
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                "Could not validate credentials",
            ) from error

        user_info = auth.get_user(decoded_token["uid"])

        # check email verified if not using firebase emulator
        emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
        if emulator_host == "" and user_info.email_verified is False:
            raise AuthException(
                AuthErrorType.UNAUTHORIZED,
                "Email is not verified. Try logging in on UI and verify email.",
            )

        email = user_info.email
        # if user_info.email is empty, get email from auth provider data
        if email is None:
            if len(user_info.provider_data) > 0:
                email = user_info.provider_data[0].email

        return user_info.uid, email

    def delete_user(self, uid):
        try:
            auth.delete_user(uid)
        except auth.ValueError as error:
            raise AuthException(
                AuthErrorType.SERVICE_UNAVAILABLE, "user ID is None, empty or malformed"
            ) from error
        except auth.FirebaseError as error:
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Error deleting user"
            ) from error
