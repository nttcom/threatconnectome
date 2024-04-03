import tempfile
from datetime import datetime
from typing import IO, Any
from uuid import UUID

from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.tests.medium.exceptions import HTTPError

client = TestClient(app)


def assert_200(response) -> dict:
    if response.status_code != 200:
        raise HTTPError(response)
    return response.json()


def assert_204(response) -> None:
    if response.status_code != 204:
        raise HTTPError(response)


def get_access_token(user: dict) -> dict:  # user = {"email": x, "pass": y}
    body = {
        "username": user["email"],
        "password": user["pass"],
    }
    return assert_200(client.post("/auth/token", data=body))


def headers(user: dict) -> dict:  # user = {"email": x, "pass": y}
    access_token = get_access_token(user)["access_token"]
    return {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def _remove_content_type_from_headers(headers: dict) -> dict:
    return {k: v for (k, v) in headers.items() if k != "Content-Type"}


def _fix_to_json_serializable(data: dict) -> dict:
    if isinstance(data, list):
        return [_fix_to_json_serializable(x) for x in data]
    ret = {}
    for key, value in data.items():
        fixed_value: Any = value
        if isinstance(value, list):
            fixed_value = [_fix_to_json_serializable(x) for x in value]
        elif isinstance(value, dict):
            fixed_value = _fix_to_json_serializable(value)
        elif isinstance(value, UUID) or isinstance(value, datetime):
            fixed_value = str(value)
        ret[key] = fixed_value
    return ret


class TestUser:
    account: schemas.UserResponse
    api: "API"
    util: "Util"

    @staticmethod
    def _create_account(headers: dict, data: dict) -> schemas.UserResponse:
        request = {"years": data.get("years") or 0}
        ret = assert_200(client.post("/users", headers=headers, json=request))
        return schemas.UserResponse(**ret)

    @classmethod
    def create(cls, user: dict) -> "TestUser":
        return TestUser(user)

    def __init__(self, user: dict):  # user = {email: x, pass: y, years: z}
        _headers = headers(user)
        self.account = self._create_account(_headers, user)
        self.api = API(_headers)
        self.util = Util(self.api)


class API:
    headers: dict

    def __init__(self, headers: dict):
        self.headers = headers

    ### User

    #   Note: use TestUser.create() to create user

    def get_user_me(self) -> schemas.UserResponse:
        url = "/users/me"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.UserResponse(**ret)

    def update_user(self, user_id: UUID | str, data: dict) -> schemas.UserResponse:
        url = f"/users/{user_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.UserResponse(**ret)

    def delete_user(self) -> None:
        url = "/users"
        assert_204(client.delete(url, headers=self.headers))

    ### Artifact Tag

    def get_all_tags(self) -> list[schemas.TagResponse]:
        url = "/tags"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.TagResponse(**x) for x in ret]

    def create_tag(self, data: dict) -> schemas.TagResponse:
        url = "/tags"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.TagResponse(**ret)

    def search_tags(self, params: dict) -> list[schemas.TagResponse]:
        url = "/tags/search"
        ret = assert_200(client.get(url, headers=self.headers, params=params))
        return [schemas.TagResponse(**x) for x in ret]

    def delete_tag(self, tag_id: UUID | str) -> None:
        url = f"/tags/{tag_id}"
        assert_204(client.delete(url, headers=self.headers))

    ### Misp Tag

    def get_all_misp_tags(self) -> list[schemas.MispTagResponse]:
        url = "/misp_tags"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.MispTagResponse(**x) for x in ret]

    def search_misp_tags(self, params: dict) -> list[schemas.MispTagResponse]:
        url = "/misp_tags/search"
        ret = assert_200(client.get(url, headers=self.headers, params=params))
        return [schemas.MispTagResponse(**x) for x in ret]

    def create_misp_tag(self, data: dict) -> schemas.MispTagResponse:
        url = "/misp_tags"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.MispTagResponse(**ret)

    ### Topic

    def get_all_topics(self) -> list[schemas.TopicEntry]:
        url = "/topics"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.TopicEntry(**x) for x in ret]

    def search_topics(self, params: dict) -> schemas.SearchTopicsResponse:
        url = "/topics/search"
        ret = assert_200(client.get(url, headers=self.headers, params=params))
        return schemas.SearchTopicsResponse(**ret)

    def get_topic(self, topic_id: UUID | str) -> schemas.TopicResponse:
        url = f"/topics/{topic_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.TopicResponse(**ret)

    def fetch_data_from_flashsense(self, topic_id: UUID | str) -> schemas.FsTopicSummary:
        url = "/topics/fetch_fs/{topic_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.FsTopicSummary(**ret)

    def create_topic(self, topic_id: UUID | str, data: dict) -> schemas.TopicCreateResponse:
        url = f"/topics/{topic_id}"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.TopicCreateResponse(**ret)

    def update_topic(self, topic_id: UUID | str, data: dict) -> schemas.TopicResponse:
        url = f"/topics/{topic_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.TopicResponse(**ret)

    def delete_topic(self, topic_id: UUID | str, data: dict) -> None:
        url = f"/topics/{topic_id}"
        assert_204(client.delete(url, headers=self.headers))

    def get_pteam_topic_actions(
        self,
        topic_id: UUID | str,
        pteam_id: UUID | str,
    ) -> schemas.TopicActionsResponse:
        url = f"/topics/{topic_id}/actions/pteam/{pteam_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.TopicActionsResponse(**ret)

    def get_user_topic_actions(self, topic_id: UUID | str) -> list[schemas.ActionResponse]:
        url = f"/topics/{topic_id}/actions/user/me"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ActionResponse(**x) for x in ret]

    ### PTeam

    def get_all_pteams(self) -> list[schemas.PTeamEntry]:
        url = "/pteams"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.PTeamEntry(**x) for x in ret]

    def get_pteam_auth_info(self) -> schemas.PTeamAuthInfo:
        url = "/pteams/auth_info"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamAuthInfo(**ret)

    def accept_pteam_invitation(self, data: dict) -> schemas.PTeamInfo:
        data = _fix_to_json_serializable(data)
        url = "/pteams/apply_invitation"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.PTeamInfo(**ret)

    def get_invited_pteam(self, invitation_id: UUID | str) -> schemas.PTeamInviterResponse:
        url = f"/pteams/invitation/{invitation_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamInviterResponse(**ret)

    def get_pteam(self, pteam_id: UUID | str) -> schemas.PTeamInfo:
        url = f"/pteams/{pteam_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamInfo(**ret)

    def get_pteam_groups(self, pteam_id: UUID | str) -> schemas.PTeamGroupResponse:
        url = f"/pteams/{pteam_id}/groups"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamGroupResponse(**ret)

    def get_pteam_tags(self, pteam_id: UUID | str) -> list[schemas.ExtTagResponse]:
        url = f"/pteams/{pteam_id}/tags"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ExtTagResponse(**x) for x in ret]

    def get_pteam_tags_summary(self, pteam_id: UUID | str) -> schemas.PTeamTagsSummary:
        url = f"/pteams/{pteam_id}/tags/summary"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamTagsSummary(**ret)

    def get_pteam_tag_solved_topic_ids(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
    ) -> schemas.PTeamTaggedTopics:
        url = f"/pteams/{pteam_id}/tags/{tag_id}/solved_topic_ids"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamTaggedTopics(**ret)

    def get_pteam_tag_unsolved_topic_ids(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
    ) -> schemas.PTeamTaggedTopics:
        url = f"/pteams/{pteam_id}/tags/{tag_id}/unsolved_topic_ids"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamTaggedTopics(**ret)

    def get_pteam_topics(self, pteam_id: UUID | str) -> list[schemas.TopicResponse]:
        url = f"/pteams/{pteam_id}/topics"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.TopicResponse(**x) for x in ret]

    def create_pteam(self, data: dict) -> schemas.PTeamInfo:
        data = _fix_to_json_serializable(data)
        url = "/pteams"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.PTeamInfo(**ret)

    def update_pteam_auth(
        self,
        pteam_id: UUID | str,
        data: dict,
    ) -> list[schemas.PTeamAuthResponse]:
        data = _fix_to_json_serializable(data)
        url = f"/pteams/{pteam_id}/authority"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.PTeamAuthResponse(**x) for x in ret]

    def get_pteam_auth(self, pteam_id: UUID | str) -> list[schemas.PTeamAuthResponse]:
        url = f"/pteams/{pteam_id}/authority"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.PTeamAuthResponse(**x) for x in ret]

    def get_pteam_tag(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
    ) -> schemas.PTeamtagExtResponse:
        url = f"/pteams/{pteam_id}/tags/{tag_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamtagExtResponse(**ret)

    def upload_pteam_sbom_file(
        self,
        pteam_id: UUID | str,
        group: str,
        sbom_file: IO,
        force_mode: bool = False,
    ) -> list[schemas.ExtTagResponse]:
        url = f"/pteams/{pteam_id}/upload_sbom_file"
        files = {"file": sbom_file}
        params = {
            "group": group,
            "force_mode": str(force_mode),
        }
        headers = _remove_content_type_from_headers(self.headers)
        ret = assert_200(client.post(url, headers=headers, files=files, params=params))
        return [schemas.ExtTagResponse(**x) for x in ret]

    def upload_pteam_tags_file(
        self,
        pteam_id: UUID | str,
        group: str,
        tags_file: IO,
        force_mode: bool = False,
    ) -> list[schemas.ExtTagResponse]:
        url = f"/pteams/{pteam_id}/upload_tags_file"
        files = {"file": tags_file}
        params = {
            "group": group,
            "force_mode": str(force_mode),
        }
        headers = _remove_content_type_from_headers(self.headers)
        ret = assert_200(client.post(url, headers=headers, files=files, params=params))
        return [schemas.ExtTagResponse(**x) for x in ret]

    def delete_pteam_group(self, pteam_id: UUID | str, group: str) -> None:
        url = f"/pteams/{pteam_id}/tags"
        params = {"group": group}
        assert_204(client.delete(url, headers=self.headers, params=params))

    def update_pteam(self, pteam_id: UUID | str, data: dict) -> schemas.PTeamInfo:
        data = _fix_to_json_serializable(data)
        url = f"/pteams/{pteam_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.PTeamInfo(**ret)

    def get_pteam_topic_status_summary(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
    ) -> schemas.PTeamTopicStatusesSummary:
        url = f"/pteams/{pteam_id}/topicstatusessummary/{tag_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.PTeamTopicStatusesSummary(**ret)

    def set_pteam_tag_topic_status(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
        topic_id: UUID | str,
        data: dict,
    ) -> schemas.TopicStatusResponse:
        data = _fix_to_json_serializable(data)
        url = f"/pteams/{pteam_id}/topicstatus/{topic_id}/{tag_id}"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.TopicStatusResponse(**ret)

    def get_pteam_topic_status(
        self,
        pteam_id: UUID | str,
        tag_id: UUID | str,
        topic_id: UUID | str,
    ) -> schemas.TopicStatusResponse:
        url = f"/pteams/{pteam_id}/topicstatus/{topic_id}/{tag_id}"
        ret = assert_200(client.post(url, headers=self.headers))
        return schemas.TopicStatusResponse(**ret)

    def get_pteam_members(self, pteam_id: UUID | str) -> list[schemas.UserResponse]:
        url = f"/pteams/{pteam_id}/members"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.UserResponse(**x) for x in ret]

    def delete_pteam_member(self, pteam_id: UUID | str, user_id: UUID | str) -> None:
        url = f"/pteams/{pteam_id}/members/{user_id}"
        assert_204(client.delete(url, headers=self.headers))

    def create_pteam_invitation(
        self,
        pteam_id: UUID | str,
        data: dict,
    ) -> schemas.PTeamInvitationResponse:
        data = _fix_to_json_serializable(data)
        url = f"/pteams/{pteam_id}/invitation"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.PTeamInvitationResponse(**ret)

    def get_all_pteam_invitations(
        self,
        pteam_id: UUID | str,
    ) -> list[schemas.PTeamInvitationResponse]:
        url = f"/pteams/{pteam_id}/invitation"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.PTeamInvitationResponse(**x) for x in ret]

    def delete_pteam_invitation(self, pteam_id: UUID | str, invitation_id: UUID | str) -> None:
        url = f"/pteams/{pteam_id}/invitation/{invitation_id}"
        assert_204(client.delete(url, headers=self.headers))

    def get_pteam_watchers(self, pteam_id: UUID | str) -> list[schemas.ATeamEntry]:
        url = f"/pteams/{pteam_id}/watchers"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamEntry(**x) for x in ret]

    def delete_pteam_watcher(self, pteam_id: UUID | str, ateam_id: UUID | str) -> None:
        url = f"/pteams/{pteam_id}/watchers/{ateam_id}"
        assert_204(client.delete(url, headers=self.headers))

    def fix_pteam_status_mismatch(self, pteam_id: UUID | str) -> None:
        url = f"/pteams/{pteam_id}/fix_status_mismatch"
        assert_200(client.post(url, headers=self.headers))

    def fix_pteam_tag_status_mismatch(self, pteam_id: UUID | str, tag_id: UUID | str) -> None:
        url = f"/pteams/{pteam_id}/tags/{tag_id}"
        assert_200(client.post(url, headers=self.headers))

    # ATeam

    def get_all_ateams(self) -> list[schemas.ATeamEntry]:
        url = "/ateams"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamEntry(**x) for x in ret]

    def create_ateam(self, data: dict) -> schemas.ATeamInfo:
        data = _fix_to_json_serializable(data)
        url = "/ateams"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ATeamInfo(**ret)

    def get_ateam_auth_info(self) -> schemas.ATeamAuthInfo:
        url = "/ateams/auth_info"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.ATeamAuthInfo(**ret)

    def get_invited_ateam(self, invitation_id: UUID | str) -> schemas.ATeamInviterResponse:
        url = "/ateams/invitation/{invitation_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.ATeamInviterResponse(**ret)

    def accept_ateam_invitation(self, data: dict) -> schemas.ATeamInfo:
        data = _fix_to_json_serializable(data)
        url = "/ateams/apply_invitation"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ATeamInfo(**ret)

    def get_requested_ateam(self, request_id: UUID | str) -> schemas.ATeamRequesterResponse:
        url = f"/ateams/watching_request/{request_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.ATeamRequesterResponse(**ret)

    def accept_ateam_watching_request(self, data: dict) -> schemas.PTeamInfo:
        data = _fix_to_json_serializable(data)
        url = "/ateams/apply_watching_request"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.PTeamInfo(**ret)

    def get_ateam(self, ateam_id: UUID | str) -> schemas.ATeamInfo:
        url = "/ateams/{ateam_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.ATeamInfo(**ret)

    def update_ateam(self, ateam_id: UUID | str, data: dict) -> schemas.ATeamInfo:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.ATeamInfo(**ret)

    def update_ateam_auth(
        self,
        ateam_id: UUID | str,
        data: dict,
    ) -> list[schemas.ATeamAuthResponse]:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}/authority"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return [schemas.ATeamAuthResponse(**x) for x in ret]

    def get_ateam_auth(self, ateam_id: UUID | str) -> list[schemas.ATeamAuthResponse]:
        url = f"/ateams/{ateam_id}/authority"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamAuthResponse(**x) for x in ret]

    def get_ateam_members(self, ateam_id: UUID | str) -> list[schemas.UserResponse]:
        url = f"/ateams/{ateam_id}/members"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.UserResponse(**x) for x in ret]

    def delete_ateam_member(self, ateam_id: UUID | str, user_id: UUID | str) -> None:
        url = f"/ateams/{ateam_id}/members/{user_id}"
        assert_204(client.delete(url, headers=self.headers))

    def create_ateam_invitation(
        self,
        ateam_id: UUID | str,
        data: dict,
    ) -> schemas.ATeamInvitationResponse:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}/invitation"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ATeamInvitationResponse(**ret)

    def get_all_ateam_invitations(
        self,
        ateam_id: UUID | str,
    ) -> list[schemas.ATeamInvitationResponse]:
        url = f"/ateams/{ateam_id}/invitation"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamInvitationResponse(**x) for x in ret]

    def delete_ateam_invitation(self, ateam_id: UUID | str, invitation_id: UUID | str) -> None:
        url = f"/ateams/{ateam_id}/invitation/{invitation_id}"
        assert_204(client.delete(url, headers=self.headers))

    def get_ateam_watching_pteams(self, ateam_id: UUID | str) -> list[schemas.PTeamEntry]:
        url = f"/ateams/{ateam_id}/watching_pteams"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.PTeamEntry(**x) for x in ret]

    def delete_ateam_watching_pteam(self, ateam_id: UUID | str, pteam_id: UUID | str) -> None:
        url = f"/ateams/{ateam_id}/watching_pteams/{pteam_id}"
        assert_204(client.delete(url, headers=self.headers))

    def create_ateam_watching_request(
        self,
        ateam_id: UUID | str,
        data: dict,
    ) -> schemas.ATeamWatchingRequestResponse:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}/watching_request"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ATeamWatchingRequestResponse(**ret)

    def get_all_ateam_watching_requests(
        self,
        ateam_id: UUID | str,
    ) -> list[schemas.ATeamWatchingRequestResponse]:
        url = f"/ateams/{ateam_id}/watching_request"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamWatchingRequestResponse(**x) for x in ret]

    def delete_ateam_watching_request(self, ateam_id: UUID | str, request_id: UUID | str) -> None:
        url = f"/ateams/{ateam_id}/watching_request/{request_id}"
        assert_204(client.delete(url, headers=self.headers))

    def get_ateam_topic_statuses(
        self,
        ateam_id: UUID | str,
        params: dict,
    ) -> schemas.ATeamTopicStatusResponse:
        url = f"/ateams/{ateam_id}/topicstatus"
        ret = assert_200(client.get(url, headers=self.headers, params=params))
        return schemas.ATeamTopicStatusResponse(**ret)

    def get_ateam_topic_comments(
        self,
        ateam_id: UUID | str,
        topic_id: UUID | str,
    ) -> list[schemas.ATeamTopicCommentResponse]:
        url = f"/ateams/{ateam_id}/topiccomment/{topic_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ATeamTopicCommentResponse(**x) for x in ret]

    def add_ateam_topic_comment(
        self,
        ateam_id: UUID | str,
        topic_id: UUID | str,
        data: dict,
    ) -> schemas.ATeamTopicCommentResponse:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}/topiccomment/{topic_id}"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ATeamTopicCommentResponse(**ret)

    def update_ateam_topic_comment(
        self,
        ateam_id: UUID | str,
        topic_id: UUID | str,
        comment_id: UUID | str,
        data: dict,
    ) -> schemas.ATeamTopicCommentResponse:
        data = _fix_to_json_serializable(data)
        url = f"/ateams/{ateam_id}/topiccomment/{topic_id}/{comment_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.ATeamTopicCommentResponse(**ret)

    def delete_ateam_topic_comment(
        self,
        ateam_id: UUID | str,
        topic_id: UUID | str,
        comment_id: UUID | str,
    ) -> None:
        url = f"/ateams/{ateam_id}/topiccomment/{topic_id}/{comment_id}"
        assert_204(client.delete(url, headers=self.headers))

    # Action

    def create_action(self, data: dict) -> schemas.ActionResponse:
        data = _fix_to_json_serializable(data)
        url = "/actions"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ActionResponse(**ret)

    def get_action(self, action_id: UUID | str) -> schemas.ActionResponse:
        url = f"/actions/{action_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.ActionResponse(**ret)

    def update_action(self, action_id: UUID | str, data: dict) -> schemas.ActionResponse:
        data = _fix_to_json_serializable(data)
        url = f"/actions/{action_id}"
        ret = assert_200(client.put(url, headers=self.headers, json=data))
        return schemas.ActionResponse(**ret)

    def delete_action(self, action_id: UUID | str) -> None:
        url = f"/actions/{action_id}"
        assert_204(client.delete(url, headers=self.headers))

    # Action Log

    def get_all_action_logs(self) -> list[schemas.ActionLogResponse]:
        url = "actionlogs"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ActionLogResponse(**x) for x in ret]

    def create_action_log(self, data: dict) -> schemas.ActionLogResponse:
        data = _fix_to_json_serializable(data)
        url = "/actionlogs"
        ret = assert_200(client.post(url, headers=self.headers, json=data))
        return schemas.ActionLogResponse(**ret)

    def get_topic_action_logs(self, topic_id: UUID | str) -> list[schemas.ActionLogResponse]:
        url = f"/actionlogs/topics/{topic_id}"
        ret = assert_200(client.get(url, headers=self.headers))
        return [schemas.ActionLogResponse(**x) for x in ret]

    # External

    def check_webhook_url(self, data: dict) -> None:
        data = _fix_to_json_serializable(data)
        url = "/external/slack/check"
        assert_200(client.post(url, headers=self.headers, json=data))

    def check_email(self, data: dict) -> None:
        data = _fix_to_json_serializable(data)
        url = "external/email/check"
        assert_200(client.post(url, headers=self.headers, json=data))

    def check_flashsense(self) -> None:
        url = "/external/flashsense/check"
        assert_200(client.post(url, headers=self.headers))

    def get_flashsense_info(self) -> schemas.FsServerInfo:
        url = "/external/flashsense/info"
        ret = assert_200(client.get(url, headers=self.headers))
        return schemas.FsServerInfo(**ret)


class Util:
    api: "API"

    def __init__(self, api: "API"):
        self.api = api

    def upload_tags_file(
        self,
        pteam: schemas.PTeamInfo,
        group: str,
        lines: list[str],
        force_mode: bool = False,
    ) -> list[schemas.ExtTagResponse]:
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
            for line in lines:
                tfile.writelines(line + "\n")
            tfile.flush()
            with open(tfile.name, "rb") as tags_file:
                return self.api.upload_pteam_tags_file(pteam.pteam_id, group, tags_file, force_mode)

    def invite_to_pteam(self, pteam: schemas.PTeamInfo) -> schemas.PTeamInvitationResponse:
        request = {"expiration": datetime(3000, 1, 1), "limit_count": 1}
        return self.api.create_pteam_invitation(pteam.pteam_id, request)

    def accept_pteam_invitation(self, invitation: schemas.PTeamInvitationResponse) -> None:
        request = {"invitation_id": invitation.invitation_id}
        self.api.accept_pteam_invitation(request)
