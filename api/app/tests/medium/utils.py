import json
import os
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from io import DEFAULT_BUFFER_SIZE, BytesIO
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient

from app import schemas
from app.auth.firebase_auth_module import FirebaseAuthModule
from app.auth.supabase_auth_module import SupabaseAuthModule
from app.main import app
from app.tests.common.auth_utils import get_access_token_headers, get_file_upload_headers
from app.tests.medium.exceptions import HTTPError

client = TestClient(app)


def assert_200(response) -> dict:
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def headers(user: dict) -> dict:
    return get_access_token_headers(user["email"], user["pass"])


def headers_with_api_key(user: dict) -> dict:
    headers_with_api = headers(user)
    headers_with_api["X-API-Key"] = os.getenv("SYSTEM_API_KEY")
    return headers_with_api


def file_upload_headers(user: dict) -> dict:
    return get_file_upload_headers(user["email"], user["pass"])


def create_user(user: dict) -> schemas.UserResponse:
    request = {**user}
    del request["email"]
    del request["pass"]

    response = client.post("/users", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.UserResponse(**response.json())


def create_pteam(user: dict, pteam: dict) -> schemas.PTeamInfo:
    request = {**pteam}

    response = client.post("/pteams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.PTeamInfo(**response.json())


def invite_to_pteam(
    user: dict,
    pteam_id: UUID | str,
) -> schemas.PTeamInvitationResponse:
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)),
        "limit_count": 1,
    }

    response = client.post(f"/pteams/{pteam_id}/invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.PTeamInvitationResponse(**response.json())


def accept_pteam_invitation(user: dict, invitation_id: UUID) -> schemas.PTeamInfo:
    request = {
        "invitation_id": str(invitation_id),
    }

    response = client.post("/pteams/apply_invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.PTeamInfo(**response.json())


def upload_pteam_packages(
    user: dict,
    pteam_id: UUID | str,
    service_name: str,
    ext_packages: list[dict[str, Any]],
) -> list[schemas.PackageFileResponse]:
    params = {"service": service_name}
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
        for ext_package in ext_packages:
            tfile.writelines(json.dumps(ext_package) + "\n")
        tfile.flush()
        tfile.seek(0)
        with open(tfile.name, "rb") as bfile:
            data = assert_200(
                client.post(
                    f"/pteams/{pteam_id}/upload_packages_file",
                    headers=file_upload_headers(user),
                    params=params,
                    files={"file": bfile},
                )
            )
    return [schemas.PackageFileResponse(**item) for item in data]


def get_pteam_services(user: dict, pteam_id: str) -> list[schemas.PTeamServiceResponse]:
    data = assert_200(client.get(f"/pteams/{pteam_id}/services", headers=headers(user)))
    return [schemas.PTeamServiceResponse(**item) for item in data]


def get_service_by_service_name(user: dict, pteam_id: UUID | str, service_name: str):
    data = assert_200(client.get(f"/pteams/{pteam_id}", headers=headers(user)))
    return next(filter(lambda x: x["service_name"] == service_name, data["services"]), None)


def create_vuln(
    user: dict,
    vuln: dict,
) -> schemas.VulnResponse:
    response = client.put(
        f"/vulns/{vuln['vuln_id']}", headers=headers_with_api_key(user), json=vuln
    )

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.VulnResponse(**response.json())


def create_actionlog(
    user: dict,
    action: str,
    vuln_id: UUID | str,
    user_id: UUID | str,
    pteam_id: UUID | str,
    service_id: UUID | str,
    ticket_id: UUID | str,
    executed_at: datetime | None,
) -> schemas.ActionLogResponse:
    request = {
        "action": action,
        "vuln_id": str(vuln_id),
        "user_id": str(user_id),
        "pteam_id": str(pteam_id),
        "service_id": str(service_id),
        "ticket_id": str(ticket_id),
        "executed_at": str(executed_at) if executed_at else None,
    }

    response = client.post("/actionlogs", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ActionLogResponse(**response.json())


def compare_references(refs1: list[dict], refs2: list[dict]) -> bool:
    def _to_tuple_set(refs):
        return {
            (ref.get("service"), ref.get("target"), ref.get("version"), ref.get("package_manager"))
            for ref in refs
        }

    if not isinstance(refs1, list) or not isinstance(refs2, list):
        return False
    if len(refs1) != len(refs2):
        return False
    return _to_tuple_set(refs1) == _to_tuple_set(refs2)


def get_tickets_related_to_vuln_package(
    user: dict,
    pteam_id: UUID | str,
    service_id: UUID | str,
    vuln_id: UUID | str,
    package_id: UUID | str,
) -> list[dict]:
    response = client.get(
        f"/pteams/{pteam_id}/tickets?service_id={service_id}&vuln_id={vuln_id}&package_id={package_id}",
        headers=headers(user),
    )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def set_ticket_status(user: dict, pteam_id: UUID | str, ticket_id: UUID | str, json: dict) -> dict:
    response = client.put(
        f"/pteams/{pteam_id}/tickets/{ticket_id}",
        headers=headers(user),
        json=json,
    )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def calc_file_sha256(file_path: str | Path) -> str:
    with open(file_path, "rb") as fin:
        file_sha256 = sha256()
        while data := fin.read(DEFAULT_BUFFER_SIZE):
            file_sha256.update(BytesIO(data).getbuffer())
        return file_sha256.hexdigest()


def judge_whether_firebase_or_supabase():
    auth_service = os.environ.get("AUTH_SERVICE")
    match auth_service:
        case "FIREBASE":
            return FirebaseAuthModule
        case "SUPABASE":
            return SupabaseAuthModule
        case _:
            raise Exception(f"Unsupported AUTH_SERVICE: {auth_service}")
