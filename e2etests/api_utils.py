import os
from typing import List, Optional
from urllib.parse import urljoin

import requests

from exceptions import HTTPError

base_url = os.getenv("BASE_URL", "http://localhost")
api_url = urljoin(base_url, "/api")


def get_access_token(username: str, password: str) -> dict:
    body = {
        "username": username,
        "password": password,
    }

    response = requests.post(f"{api_url}/auth/token", data=body)

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


def headers(user: dict) -> dict:
    return get_access_token_headers(user["email"], user["pass"])


def create_pteam(user: dict, pteam: dict):
    request = {**pteam}

    response = requests.post(f"{api_url}/pteams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def create_topic(
    user: dict,
    topic: dict,
    actions: Optional[List[dict]] = None,
    zone_names: Optional[List[str]] = None,
):
    request = {**topic}
    if actions is not None:
        request.update({"actions": actions})
    if zone_names is not None:
        request.update({"zone_names": zone_names})
    del request["topic_id"]

    response = requests.post(
        f'{api_url}/topics/{topic["topic_id"]}', headers=headers(user), json=request
    )

    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()
