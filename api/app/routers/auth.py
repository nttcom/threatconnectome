import json
import os

import requests
from fastapi import APIRouter, Form, HTTPException, status
from pydantic import SecretStr

from ..schemas import RefreshTokenRequest, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/token", response_model=Token)
def login_for_access_token(username: str = Form(), password: SecretStr = Form()) -> Token:
    # get_access_token_from_firebase(username, password.get_secret_value())
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

    data: dict = resp.json()
    if not resp.ok:
        error_message: str = data["error"]["message"]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message if error_message else "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=data["idToken"], token_type="bearer", refresh_token=data["refreshToken"]
    )


@router.post("/refresh", response_model=Token)
def refresh_access_token(request: RefreshTokenRequest) -> Token:
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": request.refresh_token,
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
