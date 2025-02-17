import json
import os

import requests
from fastapi import HTTPException, status
from firebase_admin import auth, credentials, initialize_app

from app.auth.auth_module import AuthModule

from ..schemas import Token


class FirebaseAuthModule(AuthModule):
    def __init__(self):
        super().__init__()
        self.cred = credentials.Certificate(os.environ["FIREBASE_CRED"])
        initialize_app(self.cred)

    def login_for_access_token(self, username, password) -> Token:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from firebase_timeout

        data = resp.json()
        if not resp.ok:
            error_message = data["error"]["message"]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message if error_message else "Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Token(
            access_token=data["idToken"], token_type="bearer", refresh_token=data["refreshToken"]
        )

    def refresh_access_token(self, refresh_token) -> Token:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from firebase_timeout

        data: dict = resp.json()
        if not resp.ok:
            error_message: str = data["error"]["message"]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message if error_message else "Could not refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Token(
            access_token=data["id_token"],
            token_type=data["token_type"],
            refresh_token=data["refresh_token"],
        )

    def check_and_get_user_info(self, token):
        super().check_token(token)
        try:
            decoded_token = auth.verify_id_token(token.credentials, check_revoked=True)
        except auth.ExpiredIdTokenError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            ) from error
        except auth.RevokedIdTokenError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has revoked",
            ) from error
        except auth.CertificateFetchError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to obtain required credentials",
            ) from error
        except auth.UserDisabledError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Disabled user",
            ) from error
        except (auth.InvalidIdTokenError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from error

        user_info = auth.get_user(decoded_token["uid"])

        # check email verified if not using firebase emulator
        emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
        if emulator_host == "" and user_info.email_verified is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not verified. Try logging in on UI and verify email.",
            )

        email = user_info.email
        # if user_info.email is empty, get email from auth provider data
        if email is None:
            if len(user_info.provider_data) > 0:
                email = user_info.provider_data[0].email

        return user_info.uid, email
