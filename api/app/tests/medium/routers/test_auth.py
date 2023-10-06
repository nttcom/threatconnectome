from fastapi.testclient import TestClient

from app.main import app
from app.tests.medium.exceptions import HTTPError

client = TestClient(app)


def get_access_token(username: str, password: str) -> dict:
    body = {
        "username": username,
        "password": password,
    }

    response = client.post("/auth/token", data=body)

    if response.status_code != 200:
        raise HTTPError(response)
    data = response.json()
    return data


def refresh_access_token(refresh_token: str) -> dict:
    body = {"refresh_token": refresh_token}

    response = client.post("/auth/refresh", json=body)

    if response.status_code != 200:
        raise HTTPError(response)
    data = response.json()
    return data


def get_access_token_headers(username: str, password: str) -> dict:
    access_token = get_access_token(username, password)["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def get_file_upload_headers(username: str, password: str) -> dict:
    access_token = get_access_token(username, password)["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
    }


def refresh_headers(refresh_token: str) -> dict:
    access_token = refresh_access_token(refresh_token)["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
