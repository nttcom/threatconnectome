# !/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from time import sleep
from typing import Callable
from uuid import UUID

import requests

ARGUMENTS: list[tuple[str, dict]] = [  # arg_name, options
    (
        "url",
        {"metavar": "API_BASE_URL", "type": str, "help": "API BASE URL of Threatconnectome"},
    ),
    (
        "--team",
        {
            "dest": "team",
            "action": "store_true",
            "help": "register teams (& tags)",
        },
    ),
    (
        "--topic",
        {
            "dest": "topic",
            "action": "store_true",
            "help": "register topics (& related actions)",
        },
    ),
    (
        "--all",
        {
            "dest": "all",
            "action": "store_true",
            "help": "register teams & topics",
        },
    ),
]
OPTIONS: list[tuple[str, str, dict]] = [  # short_name, long_name, options
    (
        "-t",
        "--token",
        {
            "type": str,
            "help": "set the refresh token of Threatconnectome API",
        },
    ),
]


class APIError(Exception):
    pass


class ThreatconnectomeClient:
    api_url: str
    refresh_token: str
    retry_max: int  # 0 for never, negative for forever
    headers: dict

    def __init__(
        self,
        api_url: str,
        refresh_token: str,
        retry_max: int = -1,
    ):
        self.api_url = api_url.rstrip("/")
        self.refresh_token = refresh_token
        self.retry_max = retry_max
        self.headers = self.refresh_auth_token(
            {  # headers except auth token
                "accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def refresh_auth_token(self, headers: dict) -> dict:
        resp = requests.post(
            f"{self.api_url}/auth/refresh",
            headers={"ContentType": "application/json"},
            json={"refresh_token": self.refresh_token},
        )
        new_token = resp.json().get("access_token")
        return {
            **headers,  # keep original headers except below
            "Authorization": f"Bearer {new_token}",
        }

    def retry_call(
        self,
        func: Callable[..., requests.Response],
        *args,
        **kwargs,
    ) -> requests.Response:
        # Note:
        #   func should have kwarg "headers":
        #     def func(*args, **kwargs, headers={}) -> Response:
        #   self.headers is used for kwarg "headers", and auto-refreshed on 401 error.
        _retry = self.retry_max
        _in_auth_retry = False
        _func = partial(func, *args, **{k: v for k, v in kwargs.items() if k != "headers"})

        def _resp_to_msg(resp: requests.Response) -> str:
            data = resp.json()
            return f"{resp.status_code}: {resp.reason}: {data.get('detail')}"

        while True:
            resp = _func(headers=self.headers)
            if resp.status_code in {200, 204}:
                print(f"Http status: {resp.status_code} {resp.reason}")
                return resp
            if resp.status_code == 401:
                if _in_auth_retry:
                    raise APIError(f"ERROR: {_resp_to_msg(resp)}")
                _in_auth_retry = True
                self.headers = self.refresh_auth_token(self.headers)
                continue
            if resp.status_code < 500:
                # unrecoverable error: raise without retry
                raise APIError(f"ERROR: {_resp_to_msg(resp)}")
            # maybe recoverable error
            if _retry == 0:
                raise APIError(f"ERROR: Exceeded retry max: {_resp_to_msg(resp)}")
            elif _retry > 0:
                _retry -= 1
            sleep(3)

    def create_pteam(self, dict: dict) -> dict:
        api_endpoint = f"{self.api_url}/pteams"
        print(f"Post {api_endpoint}")
        response = self.retry_call(requests.post, api_endpoint, json=dict)
        return response.json()

    def create_ateam(self, dict: dict) -> dict:
        api_endpoint = f"{self.api_url}/ateams"
        print(f"Post {api_endpoint}")
        response = self.retry_call(requests.post, api_endpoint, json=dict)
        return response.json()

    def create_watching_request(
        self,
        ateam_id: UUID | str,
    ) -> dict:
        api_endpoint = f"{self.api_url}/ateams/{ateam_id}/watching_request"
        request = {
            "expiration": str(datetime(3000, 1, 1, 0, 0, 0, 0)),
            "limit_count": 5,
        }
        print(f"Post {api_endpoint}")
        response = self.retry_call(requests.post, api_endpoint, json=request)
        return response.json()

    def accept_watching_request(self, request_id: UUID | str, pteam_id: UUID | str) -> dict:
        api_endpoint = f"{self.api_url}/ateams/apply_watching_request"
        print(f"Post {api_endpoint}")
        request = {
            "request_id": str(request_id),
            "pteam_id": str(pteam_id),
        }
        response = self.retry_call(requests.post, api_endpoint, json=request)
        return response.json()

    def upload_tags_file(self, pteam_id: UUID | str, file, group: str):
        api_endpoint = f"{self.api_url}/pteams/{pteam_id}/upload_tags_file"
        print(f"Post {api_endpoint}")
        response = requests.post(
            api_endpoint,
            headers=self.refresh_auth_token({"accept": "application/json"}),
            params={"group": group, "force_mode": "true"},
            files={"file": file},
        )
        print(f"Http status: {response.status_code} {response.reason}")
        return response.json()

    def get_topics(self) -> dict:
        response = self.retry_call(requests.get, f"{self.api_url}/topics")
        return response.json()

    def get_topic(self, topic_id) -> dict:
        response = self.retry_call(requests.get, f"{self.api_url}/topics/{topic_id}")
        return response.json()

    def create_tag(self, tag_name: str) -> None:
        api_endpoint = f"{self.api_url}/tags"
        print(f"Post {api_endpoint} to create tag: {tag_name}")
        self.retry_call(requests.post, api_endpoint, json={"tag_name": tag_name})

    def with_auto_create_tags(
        self,
        func: Callable[..., None],
        *args,
        **kwargs,
    ) -> None:
        while True:
            try:
                func(*args, **kwargs)
            except APIError as error:
                no_tags_error_pref = "ERROR: 400: Bad Request: No such tags: "
                if (err_msg := str(error)).startswith(no_tags_error_pref):
                    print(err_msg)
                    for tag_name in err_msg[len(no_tags_error_pref) :].split(", "):
                        self.create_tag(tag_name)
                    continue  # try again
                raise error
            return

    def _create_topic(self, topic_id: str, topic: dict) -> None:
        api_endpoint = f"{self.api_url}/topics/{topic_id}"
        print(f"Post {api_endpoint}")
        self.retry_call(requests.post, api_endpoint, json=topic)

    def create_topic(self, topic_id: str, topic: dict) -> None:
        self.with_auto_create_tags(self._create_topic, topic_id, topic)

    def _update_topic_and_actions(self, topic_id: str, topic: dict) -> None:
        api_endpoint = f"{self.api_url}/topics/{topic_id}"
        print(f"Put {api_endpoint}")
        response = self.retry_call(requests.put, api_endpoint, json=topic)
        for action in topic.get("actions") or []:
            try:
                api_endpoint = f"{self.api_url}/actions"
                print(f"Post {api_endpoint}")
                response = self.retry_call(
                    requests.post, api_endpoint, json={**action, "topic_id": topic_id}
                )
            except APIError as error:
                if str(error) == "ERROR: 400: Bad Request: Action id already exists":
                    api_endpoint = f"{self.api_url}/actions/{action['action_id']}"
                    print(f"Put {api_endpoint}")
                    self.retry_call(requests.put, api_endpoint, json=action)
                    print(f"Http status: {response.status_code} {response.reason}")
                else:
                    raise error

    def update_topic_and_actions(self, topic_id: str, topic: dict) -> None:
        self.with_auto_create_tags(self._update_topic_and_actions, topic_id, topic)


def main() -> None:
    PARSER = argparse.ArgumentParser()
    for sname, lname, opts in OPTIONS:
        PARSER.add_argument(sname, lname, **opts)
    for name, opts in ARGUMENTS:
        PARSER.add_argument(name, **opts)
    ARGS = PARSER.parse_args()

    if ARGS.token:
        refresh_token = ARGS.token
    else:
        refresh_token = os.environ.get("THREATCONNECTOME_REFRESHTOKEN")
    if not refresh_token:
        sys.exit(
            "ERROR: Require the Bearer Token of Threatconnectome.\n"
            "You can use 'export THREATCONNECTOME_REFRESHTOKEN=\"XXXXXX\"'."
        )

    tc_client = ThreatconnectomeClient(ARGS.url, refresh_token, retry_max=3)
    sampledata_dir = Path(__file__).resolve().parent / "sample-data"

    if ARGS.team or ARGS.all:
        print("# register teams")
        with open(sampledata_dir / "teams.json") as f:
            teams_data = json.load(f)

        pteam1 = tc_client.create_pteam(teams_data["pteams"][0])
        ateam1 = tc_client.create_ateam(teams_data["ateams"][0])
        watching_req1 = tc_client.create_watching_request(ateam1["ateam_id"])
        tc_client.accept_watching_request(watching_req1["request_id"], pteam1["pteam_id"])

        print("# register pteamtags")
        with open(sampledata_dir / "tags-backend.jsonl", "rb") as f:
            tc_client.upload_tags_file(pteam1["pteam_id"], f, "webapp-backend")
        with open(sampledata_dir / "tags-frontend.jsonl", "rb") as f:
            tc_client.upload_tags_file(pteam1["pteam_id"], f, "webapp-frontend")

    if ARGS.topic or ARGS.all:
        print("# register topics & actions")
        existing_topics = tc_client.get_topics()
        existing_topic_ids = {x["topic_id"] for x in existing_topics}

        with open(sampledata_dir / "topics.json") as f:
            topics_data = json.load(f)
        for topic in topics_data:
            if topic["topic_id"] not in existing_topic_ids:
                tc_client.create_topic(topic["topic_id"], topic)


if __name__ == "__main__":
    main()
