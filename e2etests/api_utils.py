import json
import os
import tempfile
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

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


def get_file_upload_headers(username: str, password: str) -> dict:
    access_token = get_access_token(username, password)["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
    }


def headers(user: dict) -> dict:
    return get_access_token_headers(user["email"], user["pass"])


def headers_with_api_key(user: dict) -> dict:
    headers_with_api = headers(user)
    headers_with_api["X-API-Key"] = os.getenv("SYSTEM_API_KEY")
    return headers_with_api


def file_upload_headers(user: dict) -> dict:
    return get_file_upload_headers(user["email"], user["pass"])


def create_pteam(user: dict, pteam: dict):
    request = {**pteam}

    response = requests.post(f"{api_url}/pteams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def create_vuln(
    user: dict,
    vuln: dict,
) -> dict:
    response = requests.put(
        f'{api_url}/vulns/{vuln["vuln_id"]}', headers=headers_with_api_key(user), json=vuln
    )

    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def upload_pteam_packages(
    user: dict,
    pteam_id: UUID | str,
    service_name: str,
    ext_packages: list[dict[str, Any]],
) -> list:
    params = {"service": service_name}
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
        for ext_package in ext_packages:
            tfile.writelines(json.dumps(ext_package) + "\n")
        tfile.flush()
        tfile.seek(0)
        with open(tfile.name, "rb") as bfile:
            response = requests.post(
                f"{api_url}/pteams/{pteam_id}/upload_packages_file",
                headers=file_upload_headers(user),
                params=params,
                files={"file": bfile},
            )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def get_pteam_services(user: dict, pteam_id: UUID | str):
    response = requests.get(
        f"{api_url}/pteams/{pteam_id}/services",
        headers=file_upload_headers(user),
    )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()
