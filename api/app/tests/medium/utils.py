import json
import random
import string
import tempfile
from datetime import datetime
from hashlib import sha256
from io import DEFAULT_BUFFER_SIZE, BytesIO
from pathlib import Path
from typing import Sequence
from uuid import UUID

from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.routers.test_auth import get_access_token_headers, get_file_upload_headers

client = TestClient(app)


def assert_200(response) -> dict:
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def assert_204(response):
    if response.status_code != 204:
        raise HTTPError(response)


def schema_to_dict(data) -> dict:
    if isinstance(data, schemas.TagResponse):
        return {
            "tag_name": data.tag_name,
            "tag_id": str(data.tag_id),
            "parent_name": data.parent_name,
            "parent_id": str(data.parent_id) if data.parent_id else None,
        }
    raise ValueError(f"Not implemented for {type(data)}")


def headers(user: dict) -> dict:
    return get_access_token_headers(user["email"], user["pass"])


def file_upload_headers(user: dict) -> dict:
    return get_file_upload_headers(user["email"], user["pass"])


def random_string(number: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=number))


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
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
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


def upload_pteam_tags(
    user: dict,
    pteam_id: UUID | str,
    service: str,
    ext_tags: dict[str, list[tuple[str, str]]],  # {tag: [(target, version), ...]}
) -> list[schemas.ExtTagResponse]:
    params = {"service": service}
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
        for tag_name, etags in ext_tags.items():
            assert all(len(etag) == 2 and None not in etag for etag in etags)  # check test code
            splited_tag_name = tag_name.split(":", 2)
            tag_name_len = len(splited_tag_name)
            package_name = splited_tag_name[0] if tag_name_len > 0 else None
            ecosystem = splited_tag_name[1] if tag_name_len > 1 else None
            package_manager = splited_tag_name[2] if tag_name_len > 2 else None
            refs = [{"target": etag[0], "version": etag[1]} for etag in etags]
            tfile.writelines(
                json.dumps(
                    {
                        "package_name": package_name,
                        "ecosystem": ecosystem,
                        "package_manager": package_manager,
                        "references": refs,
                    }
                )
                + "\n"
            )
        tfile.flush()
        with open(tfile.name, "rb") as bfile:
            data = assert_200(
                client.post(
                    f"/pteams/{pteam_id}/upload_tags_file",
                    headers=file_upload_headers(user),
                    params=params,
                    files={"file": bfile},
                )
            )
    return [schemas.ExtTagResponse(**item) for item in data]


def get_pteam_services(user: dict, pteam_id: str) -> list[schemas.PTeamServiceResponse]:
    data = assert_200(client.get(f"/pteams/{pteam_id}/services", headers=headers(user)))
    return [schemas.PTeamServiceResponse(**item) for item in data]


def get_service_by_service_name(user: dict, pteam_id: UUID | str, service_name: str):
    data = assert_200(client.get(f"/pteams/{pteam_id}", headers=headers(user)))
    return next(filter(lambda x: x["service_name"] == service_name, data["services"]), None)


def create_actionlog(
    user: dict,
    action_id: UUID | str,
    topic_id: UUID | str,
    user_id: UUID | str,
    pteam_id: UUID | str,
    service_id: UUID | str,
    ticket_id: UUID | str,
    executed_at: datetime | None,
) -> schemas.ActionLogResponse:
    request = {
        "action_id": str(action_id),
        "topic_id": str(topic_id),
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


def compare_tags(
    tags1: Sequence[dict | schemas.TagResponse],
    tags2: Sequence[dict | schemas.TagResponse],
) -> bool:
    def _to_tuple(tag_: dict | schemas.TagResponse):
        if isinstance(tag_, schemas.TagResponse):
            tag_ = tag_.model_dump()
        return (
            tag_.get("tag_name"),
            str(tag_.get("tag_id")),
            tag_.get("parent_name"),
            str(parent_id) if (parent_id := tag_.get("parent_id")) else None,
        )

    return [_to_tuple(t1) for t1 in tags1] == [_to_tuple(t2) for t2 in tags2]


def compare_references(refs1: list[dict], refs2: list[dict]) -> bool:
    def _to_tuple_set(refs):
        return {(ref.get("service"), ref.get("target"), ref.get("version")) for ref in refs}

    if not isinstance(refs1, list) or not isinstance(refs2, list):
        return False
    if len(refs1) != len(refs2):
        return False
    return _to_tuple_set(refs1) == _to_tuple_set(refs2)


def get_tickets_related_to_topic_tag(
    user: dict,
    pteam_id: UUID | str,
    service_id: UUID | str,
    topic_id: UUID | str,
    tag_id: UUID | str,
) -> list[dict]:
    response = client.get(
        f"/pteams/{pteam_id}/services/{service_id}/topics/{topic_id}/tags/{tag_id}/tickets",
        headers=headers(user),
    )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def set_ticket_status(user: dict, pteam_id: UUID | str, ticket_id: UUID | str, json: dict) -> dict:
    response = client.put(
        f"/pteams/{pteam_id}/tickets/{ticket_id}/ticketstatuses",
        headers=headers(user),
        json=json,
    )
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def common_put(user: dict, api_path: str, **kwargs) -> dict:
    response = client.put(api_path, headers=headers(user), json=kwargs)
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def calc_file_sha256(file_path: str | Path) -> str:
    with open(file_path, "rb") as fin:
        file_sha256 = sha256()
        while data := fin.read(DEFAULT_BUFFER_SIZE):
            file_sha256.update(BytesIO(data).getbuffer())
        return file_sha256.hexdigest()
