import json
import os
import tempfile
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


def file_upload_headers(user: dict) -> dict:
    return get_file_upload_headers(user["email"], user["pass"])


def create_pteam(user: dict, pteam: dict):
    request = {**pteam}

    response = requests.post(f"{api_url}/pteams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def create_topic(
    user: dict,
    topic: dict,
    actions: list[dict] | None = None,
    zone_names: list[str] | None = None,
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


def upload_pteam_tags(
    user: dict,
    pteam_id: UUID | str,
    service: str,
    ext_tags: dict[str, list[tuple[str, str]]],  # {tag: [(target, version), ...]}
    force_mode: bool = True,
) -> dict:
    params = {"service": service, "force_mode": str(force_mode)}
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
        for tag_name, etags in ext_tags.items():
            assert all(len(etag) == 2 and None not in etag for etag in etags)  # check test code
            refs = [{"target": etag[0], "version": etag[1]} for etag in etags]
            tfile.writelines(json.dumps({"tag_name": tag_name, "references": refs}) + "\n")
        tfile.flush()
        with open(tfile.name, "rb") as bfile:
            response = requests.post(
                f"{api_url}/pteams/{pteam_id}/upload_tags_file",
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
