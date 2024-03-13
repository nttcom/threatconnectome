# !/usr/bin/env python3.10

import argparse
import http.client as http_client
import os
import sys
from functools import partial
from time import sleep
from typing import Callable, Dict, List, Set, Tuple
from uuid import UUID

import requests

http_client.HTTPConnection.debuglevel = 0  # set 1 for detailed debug

ENV_KEY_REFRESH_TOKEN = "THREATCONNECTOME_REFRESH_TOKEN"

RETCODE_ALL_MATCHED_TOPICS_COMPLETED = 0
RETCODE_SOME_MATCHED_TOPICS_LEFT_UNCOMPLETED = 1
RETCODE_NO_TOPICS_MATCHED_WITH_MISP_TAG = 2
RETCODE_NOT_MATCHED_WITH_PTEAM_WATCHING_TARGETS = 3


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

    def get_pteam_tags(self, pteam_id: UUID | str) -> dict:
        url = f"{self.api_url}/pteams/{pteam_id}/tags"
        response = self.retry_call(requests.get, url)
        return response.json()

    def search_topics_by_misp_tag(self, misp_tag: str, offset: int = 0, limit: int = 100) -> dict:
        params = {
            "misp_tag_names": [misp_tag],
            "offset": offset,
            "limit": limit,
        }
        url = f"{self.api_url}/topics/search"
        response = self.retry_call(requests.get, url, params=params)
        return response.json()

    def get_topic(self, topic_id: UUID | str) -> dict:
        url = f"{self.api_url}/topics/{topic_id}"
        response = self.retry_call(requests.get, url)
        return response.json()

    def get_pteam_topic_tag_status(
        self,
        pteam_id: UUID | str,
        topic_id: UUID | str,
        tag_id: UUID | str,
    ) -> dict:
        url = f"{self.api_url}/pteams/{pteam_id}/topicstatus/{topic_id}/{tag_id}"
        response = self.retry_call(requests.get, url)
        return response.json()


ARGUMENTS: List[Tuple[str, dict]] = [
    (
        "pteam_id",
        {
            "help": "UUID of the pteam",
        },
    ),
    (
        "misp_tag",
        {
            "help": "MISP tag to get status",
        },
    ),
]
OPTIONS: List[Tuple[str, str, dict]] = [
    (
        "-e",
        "--endpoint",
        {
            "required": True,
            "help": "API endpoint url. (e.g. https://tc.service.org/api)",
        },
    ),
    (
        "-r",
        "--refresh-token",
        {
            "required": False,
            "default": os.environ.get(ENV_KEY_REFRESH_TOKEN),
            "help": "Refresh token to access api server."
            + f" default is environment variable: {ENV_KEY_REFRESH_TOKEN}.",
        },
    ),
]


def trace_message(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
    sys.stderr.flush()


def _divide_tag_groups(tags: dict) -> Dict[str | None, List[str]]:
    ret_dict: Dict[str | None, List[str]] = {}  # {parent_id: [tag_ids]}
    for tag in tags:
        tag_id = tag["tag_id"]
        parent_id = tag["parent_id"]
        tmp_list = ret_dict.get(parent_id, [])
        tmp_list.append(tag_id)
        ret_dict[parent_id] = tmp_list
    return ret_dict


def main(args: argparse.Namespace) -> None:
    tc_client = ThreatconnectomeClient(args.endpoint, args.refresh_token, retry_max=1)

    # get pteam tags & gen watching tags
    pteam_tags_list = tc_client.get_pteam_tags(args.pteam_id)
    pteam_tags_dict = {t["tag_id"]: t for t in pteam_tags_list}
    pteam_tag_groups = _divide_tag_groups(pteam_tags_list)
    pteam_parent_ids = set(pteam_tag_groups.keys())

    # search related topics matched with misp_tag
    search_result = tc_client.search_topics_by_misp_tag(args.misp_tag)
    if search_result["num_topics"] == 0:
        print(f"No topic matched with misp_tag: {args.misp_tag}")
        sys.exit(RETCODE_NO_TOPICS_MATCHED_WITH_MISP_TAG)

    # get left topics if cannot get at once
    related_topics = search_result["topics"]
    if search_result["num_topics"] > 100:  # 100 is the limit of search topics api
        offset = 100
        while offset < search_result["num_topics"]:
            tmp_result = tc_client.search_topics_by_misp_tag(args.misp_tag, offset=offset)
            related_topics.extend(tmp_result["topics"])
            offset += 100

    # process each topics
    topics_dict: Dict[str, dict] = {}  # topic_id: topic
    topic_to_pteam_tags_set: Dict[str, Set[str]] = {}  # topic_id: {tag_id, ...}
    for topic_summary in related_topics:
        # check if the topic is pteam's watching target
        topic = tc_client.get_topic(topic_summary["topic_id"])
        topic_id = topic["topic_id"]
        topic_tag_groups = _divide_tag_groups(topic["tags"])
        topic_parent_ids = set(topic_tag_groups.keys())

        # compare topic_tags and pteam_tags by each tag groups
        matched_parent_ids = topic_parent_ids & pteam_parent_ids
        if not matched_parent_ids:
            continue  # this topic is not a pteam watching target
        actual_pteam_tag_ids = set()  # save pteam tags to get topic status
        for parent_id in matched_parent_ids:
            actual_topic_tag_ids = set(topic_tag_groups.get(parent_id, []))
            pteam_tag_ids = set(pteam_tag_groups.get(parent_id, []))
            if parent_id and parent_id in actual_topic_tag_ids:
                # topic tags include parent, thus add all pteam tags
                actual_pteam_tag_ids |= pteam_tag_ids
            else:  # topic tags are children only, add exactly matched pteam tags only
                actual_pteam_tag_ids |= actual_topic_tag_ids & pteam_tag_ids
        if not actual_pteam_tag_ids:
            # for the case topic and pteam has different parent-less tags
            # e.g. topic_tags = [test1:xxx] and pteam_tags = [test2:xxx]
            continue  # this topic is not a pteam watching target

        # save infos to get details later
        topics_dict[topic_id] = topic
        topic_to_pteam_tags_set[topic_id] = actual_pteam_tag_ids

    if len(topics_dict) == 0:
        print(f"Your PTeam does not watch any topics matched with misp_tag: {args.misp_tag}")
        sys.exit(RETCODE_NOT_MATCHED_WITH_PTEAM_WATCHING_TARGETS)

    # get topic statuses for each pteam tags
    solved_topic_tags = []
    unsolved_topic_statuses: Dict[str, List[dict]] = {}  # topic_id: [status, ...]
    for topic_id, pteam_tag_ids in topic_to_pteam_tags_set.items():
        statuses = []
        for pteam_tag_id in pteam_tag_ids:
            status = tc_client.get_pteam_topic_tag_status(args.pteam_id, topic_id, pteam_tag_id)
            if status["topic_status"] == "completed":
                solved_topic_tags.append({"topic_id": topic_id, "pteam_tag_id": pteam_tag_id})
                continue
            statuses.append(status)
        if statuses:
            unsolved_topic_statuses[topic_id] = statuses

    if not unsolved_topic_statuses:
        print(f"Your PTeam has already comleted all of related {len(solved_topic_tags)} topics.")
        solved_summary = []
        for solved in solved_topic_tags:
            topic = topics_dict[solved["topic_id"]]
            pteam_tag = pteam_tags_dict[solved["pteam_tag_id"]]
            solved_summary.append(f"  - {pteam_tag['tag_name']}\t{topic['title']}")
        print("\n".join(sorted(solved_summary)))
        sys.exit(RETCODE_ALL_MATCHED_TOPICS_COMPLETED)

    print(f"Your PTeam has unsolved {len(unsolved_topic_statuses)} topics")
    for idx, [topic_id, statuses] in enumerate(unsolved_topic_statuses.items()):
        topic = topics_dict[topic_id]
        impact_labels = {
            1: "Immediate",
            2: "Off-cycle",
            3: "Acceptable",
            4: "None",
        }
        print(f"==[ {idx} ]==")
        print(f"Title: {topic['title']}")
        print(f"TopicID: {topic['topic_id']}")
        print(f"ThreatImpact: {impact_labels.get(topic['threat_impact'])}")
        print("Artifact tags & statuses")
        str_statuses = []
        for status in statuses:
            tag = pteam_tags_dict[status["tag_id"]]
            str_statuses.append(f"  {tag['tag_name']}\t{status['topic_status'] or 'alerted'}")
        print("\n".join(sorted(str_statuses)))
    sys.exit(RETCODE_SOME_MATCHED_TOPICS_LEFT_UNCOMPLETED)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    for name, opts in ARGUMENTS:
        PARSER.add_argument(name, **opts)
    for sname, lname, opts in OPTIONS:
        PARSER.add_argument(sname, lname, **opts)
    ARGS = PARSER.parse_args()

    if not ARGS.refresh_token:
        raise ValueError(
            f"the argument: -r/--refresh-token or environment variable: {ENV_KEY_REFRESH_TOKEN}"
            + " is required"
        )

    main(ARGS)
