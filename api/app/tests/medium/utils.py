import random
import string
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi.testclient import TestClient

from app import models, schemas
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
    pteam_id: Union[UUID, str],
    auth: Optional[List[models.PTeamAuthEnum]] = None,
) -> schemas.PTeamInvitationResponse:
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": auth,
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


def create_ateam(user: dict, ateam: dict) -> schemas.ATeamInfo:
    request = {**ateam}

    response = client.post("/ateams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ATeamInfo(**response.json())


def invite_to_ateam(
    user: dict,
    ateam_id: Union[UUID, str],
    authes: Optional[List[models.ATeamAuthEnum]] = None,
) -> schemas.ATeamInvitationResponse:
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": authes,
    }

    response = client.post(f"/ateams/{ateam_id}/invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ATeamInvitationResponse(**response.json())


def create_watching_request(
    user: dict,
    ateam_id: Union[UUID, str],
) -> schemas.ATeamWatchingRequestResponse:
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
    }

    response = client.post(
        f"/ateams/{ateam_id}/watching_request", headers=headers(user), json=request
    )

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ATeamWatchingRequestResponse(**response.json())


def accept_watching_request(user: dict, request_id: UUID, pteam_id: UUID) -> schemas.PTeamInfo:
    request = {
        "request_id": str(request_id),
        "pteam_id": str(pteam_id),
    }

    response = client.post("/ateams/apply_watching_request", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.PTeamInfo(**response.json())


def accept_ateam_invitation(user: dict, invitation_id: UUID) -> schemas.ATeamInfo:
    request = {
        "invitation_id": str(invitation_id),
    }

    response = client.post("/ateams/apply_invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ATeamInfo(**response.json())


def create_gteam(user: dict, gteam: dict) -> schemas.GTeamInfo:
    request = {**gteam}

    response = client.post("/gteams", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.GTeamInfo(**response.json())


def invite_to_gteam(
    user: dict,
    gteam_id: Union[UUID, str],
    authes: Optional[List[models.GTeamAuthEnum]] = None,
) -> schemas.GTeamInvitationResponse:
    request = {
        "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
        "limit_count": 1,
        "authorities": authes,
    }

    response = client.post(f"/gteams/{gteam_id}/invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.GTeamInvitationResponse(**response.json())


def accept_gteam_invitation(user: dict, invitation_id: UUID) -> schemas.GTeamInfo:
    request = {
        "invitation_id": str(invitation_id),
    }

    response = client.post("/gteams/apply_invitation", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.GTeamInfo(**response.json())


def create_tag(user: dict, tag_name: str) -> schemas.TagResponse:
    request = {
        "tag_name": tag_name,
    }
    response = client.post("/tags", headers=headers(user), json=request)
    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.TagResponse(**response.json())


def create_misp_tag(user: dict, tag_name: str) -> schemas.MispTagResponse:
    request = {
        "tag_name": tag_name,
    }
    response = client.post("/misp_tags", headers=headers(user), json=request)
    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.MispTagResponse(**response.json())


def create_zone(user: dict, gteam_id: Union[UUID, str], zone: dict) -> schemas.ZoneInfo:
    request = {**zone}
    response = client.post(f"/gteams/{gteam_id}/zones", headers=headers(user), json=request)
    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ZoneInfo(**response.json())


def create_topic(
    user: dict,
    topic: dict,
    actions: Optional[List[dict]] = None,
    zone_names: Optional[List[str]] = None,
    auto_create_tags: bool = True,
) -> schemas.TopicCreateResponse:
    request = {**topic}
    if actions is not None:
        request.update({"actions": actions})
    if zone_names is not None:
        request.update({"zone_names": zone_names})
    del request["topic_id"]

    response = client.post(f'/topics/{topic["topic_id"]}', headers=headers(user), json=request)

    if response.status_code != 200:
        no_tag_msg = "No such tags: "
        if (
            auto_create_tags
            and response.status_code == 400
            and (detail := response.json().get("detail", "")).startswith(no_tag_msg)
        ):
            for tag_name in detail[len(no_tag_msg) :].split(", "):  # split tag_names CSV
                create_tag(user, tag_name)
            return create_topic(user, topic, actions, zone_names, auto_create_tags=False)
        raise HTTPError(response)
    return schemas.TopicCreateResponse(**response.json())


def update_topic(
    user: dict,
    topic: schemas.TopicEntry,
    params: dict,
) -> schemas.TopicResponse:
    data = assert_200(client.put(f"/topics/{topic.topic_id}", headers=headers(user), json=params))
    return schemas.TopicResponse(**data)


def search_topics(
    user: dict,
    params: dict,
) -> schemas.SearchTopicsResponse:
    data = assert_200(client.get("/topics/search", headers=headers(user), params=params))
    return schemas.SearchTopicsResponse(**data)


def create_action(
    user: dict,
    action: dict,
    topic_id: Union[str, UUID],
    ext: Optional[dict] = None,
    zone_names: Optional[List[str]] = None,
) -> schemas.ActionResponse:
    request: dict = {**action, "topic_id": str(topic_id)}
    if ext is not None:
        request.update({"ext": ext})
    if zone_names is not None:
        request.update({"zone_names": zone_names})
    data = assert_200(client.post("/actions", headers=headers(user), json=request))
    return schemas.ActionResponse(**data)


def create_actionlog(
    user: dict,
    action_id: UUID,
    topic_id: UUID,
    user_id: UUID,
    pteam_id: UUID,
    executed_at: Optional[datetime],
) -> schemas.ActionLogResponse:
    request = {
        "action_id": str(action_id),
        "topic_id": str(topic_id),
        "user_id": str(user_id),
        "pteam_id": str(pteam_id),
        "executed_at": str(executed_at) if executed_at else None,
    }

    response = client.post("/actionlogs", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.ActionLogResponse(**response.json())


def compare_ext_tags(
    tags1: List[Union[dict, schemas.ExtTagResponse]],
    tags2: List[Union[dict, schemas.ExtTagResponse]],
) -> bool:
    def _to_tuple_set(tags):
        return set((dict(x)["tag_name"], dict(x)["text"]) for x in tags)

    return _to_tuple_set(tags1) == _to_tuple_set(tags2)


def create_badge(
    user: dict, recipient_id: UUID, metadata: dict, badge: dict, pteam_id: UUID
) -> schemas.SecBadgeBody:
    request = {
        "recipient": str(recipient_id),
        "metadata": metadata,
        **badge,
        "pteam_id": str(pteam_id),
    }

    response = client.post("/achievements", headers=headers(user), json=request)

    if response.status_code != 200:
        raise HTTPError(response)
    return schemas.SecBadgeBody(**response.json())


def create_topicstatus(
    user: dict, pteam_id: UUID, topic_id: UUID, tag_id: UUID, json: dict
) -> schemas.TopicStatusResponse:
    response = assert_200(
        client.post(
            f"/pteams/{pteam_id}/topicstatus/{topic_id}/{tag_id}",
            headers=headers(user),
            json=json,
        )
    )
    return schemas.TopicStatusResponse(**response)


def common_put(user: dict, api_path: str, **kwargs) -> dict:
    response = client.put(api_path, headers=headers(user), json=kwargs)
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()
