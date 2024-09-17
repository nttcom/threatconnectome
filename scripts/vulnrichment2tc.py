# !/usr/bin/env python3

import argparse
import glob
import json
import os
import sys
from functools import partial
from time import sleep
from typing import Callable

import requests


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
        self.headers = self._refresh_auth_token(
            {  # headers except auth token
                "accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _refresh_auth_token(self, headers: dict) -> dict:
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

    def _retry_call(
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
                self.headers = self._refresh_auth_token(self.headers)
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

    def search_topics(self, params: dict) -> dict:
        response = self._retry_call(requests.get, f"{self.api_url}/topics/search", params=params)
        return response.json()

    def update_topic(self, topic_id: str, topic_data: dict) -> requests.Response:
        return self._retry_call(requests.put, f"{self.api_url}/topics/{topic_id}", json=topic_data)


def _json_loads(filepath: str | bytes | bytearray):
    with open(filepath, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as error:
            raise Exception(
                "Wrong file content: " + f'{"..." if len(filepath) > 32 else ""}{filepath[32:]!s}'
            ) from error


def _get_cve_data_from_json_data(vulnrichment_json: dict) -> dict[str, tuple]:
    cve_data_dict: dict[str, tuple] = {}

    if "adp" not in vulnrichment_json["containers"]:
        return cve_data_dict

    adp_vulnrichment = next(
        filter(
            lambda x: x["title"] == "CISA ADP Vulnrichment",
            vulnrichment_json["containers"]["adp"],
        )
    )

    metric = next(
        filter(lambda x: "other" in x and x["other"]["type"] == "ssvc", adp_vulnrichment["metrics"])
    )

    content = metric["other"]["content"]

    for option in content["options"]:
        if "Exploitation" in option:
            exploitation = option["Exploitation"]
        if "Automatable" in option:
            automatable = option["Automatable"]

    if exploitation is None or automatable is None:
        return cve_data_dict

    cve_data_dict[content["id"]] = (
        exploitation,
        automatable,
    )

    return cve_data_dict


def _get_cve_data(vulnrichment_path: str) -> dict[str, tuple]:
    cve_data_dict: dict[str, tuple] = {}
    for cve_filepath in glob.iglob(vulnrichment_path + "/**/CVE-*.json", recursive=True):
        try:
            current_cve_data_dict = _get_cve_data_from_json_data(_json_loads(cve_filepath))
            cve_data_dict.update(current_cve_data_dict)
        except OSError as error:
            print(f"Json open error. filepath:{cve_filepath} detail:{error}")
            continue
        except (KeyError, TypeError) as error:
            print(f"Json parsing error. filepath:{cve_filepath} detail:{error}")
            continue
    return cve_data_dict


def _get_exploitation_value(exploitation: str) -> str:
    match exploitation:
        case "active":
            return "active"
        case "poc":
            return "public_poc"
        case "none":
            return "none"
        case _:
            return "none"


def _get_automatable_value(automatable: str) -> str:
    return automatable.lower()


def _update_topics_by_cve_data(
    tc_client: ThreatconnectomeClient, cve_id: str, exploitation: str, automatable: str
) -> None:
    params = {"misp_tag_names": [cve_id]}

    search_response = tc_client.search_topics(params)
    for topicEntry in search_response["topics"]:
        topic_id = topicEntry["topic_id"]
        topic_data = {
            "exploitation": _get_exploitation_value(exploitation),
            "automatable": _get_automatable_value(automatable),
        }
        tc_client.update_topic(topic_id, topic_data)

        response = tc_client.update_topic(topic_id, topic_data)
        if response.status_code == 200:
            print(f"Success put topic. topic_id:{topic_id} cve_id:{cve_id} data: {topic_data}")
        else:
            print(f"Faild put topic. Http status: {response.status_code} {response.reason}")


def _update_topics_by_cve_data_dict(
    tc_client: ThreatconnectomeClient, cve_data_dict: dict[str, tuple]
) -> None:
    for cve_id, cve_tuple in cve_data_dict.items():
        _update_topics_by_cve_data(tc_client, cve_id, cve_tuple[0], cve_tuple[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", metavar="API_BASE_URL", type=str, help="API BASE URL of Threatconnectome"
    )
    parser.add_argument(
        "-v", dest="vulnrichment_path", type=str, help="load the vulnrichment from this path"
    )
    parser.add_argument(
        "-t",
        dest="token",
        type=str,
        help="set the refresh token of Threatconnectome API",
    )
    args = parser.parse_args()
    if args.token:
        refresh_token = args.token
    else:
        refresh_token = os.environ.get("THREATCONNECTOME_REFRESHTOKEN")

    if not refresh_token:
        sys.exit(
            "ERROR: Require the Bearer Token of Threatconnectome.\n"
            "You can use 'export THREATCONNECTOME_REFRESHTOKEN=\"XXXXXX\"'."
        )

    tc_client = ThreatconnectomeClient(args.url, refresh_token, retry_max=3)

    cve_data_dict = _get_cve_data(args.vulnrichment_path)
    _update_topics_by_cve_data_dict(tc_client, cve_data_dict)


if __name__ == "__main__":
    main()