# !/usr/bin/env python3

import argparse
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
    connect_timeout: float
    read_timeout: float
    headers: dict

    def __init__(
        self,
        api_url: str,
        refresh_token: str,
        retry_max: int = -1,
        connect_timeout: float = 60.0,
        read_timeout: float = 60.0,
    ):
        self.api_url = api_url.rstrip("/")
        self.refresh_token = refresh_token
        self.retry_max = retry_max
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
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
        kwargs["timeout"] = (self.connect_timeout, self.read_timeout)
        _retry = self.retry_max
        _in_auth_retry = False
        _func = partial(func, *args, **{k: v for k, v in kwargs.items() if k != "headers"})

        def _resp_to_msg(resp: requests.Response) -> str:
            data = resp.json()
            return f"{resp.status_code}: {resp.reason}: {data.get('detail')}"

        while True:
            try:
                resp = _func(headers=self.headers)
            except requests.exceptions.Timeout as error:
                if _retry == 0:
                    raise APIError(f"ERROR: Exceeded retry max: {error}")
                elif _retry > 0:
                    _retry -= 1
                sleep(3)
                continue
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

    def get_pteam(self, pteam_id) -> dict:
        response = self._retry_call(requests.get, f"{self.api_url}/pteams/{pteam_id}")
        return response.json()

    def get_threats(self, params) -> list:
        response = self._retry_call(requests.get, f"{self.api_url}/threats", params=params)
        return response.json()

    def get_dependency(self, pteam_id, service_id, dependency_id):
        response = self._retry_call(
            requests.get,
            f"{self.api_url}/pteams/{pteam_id}/services/{service_id}/dependencies/{dependency_id}",
        )
        return response.json()

    def get_tag(self, tag_id):
        response = self._retry_call(requests.get, f"{self.api_url}/tags/{tag_id}")
        return response.json()

    def get_topic(self, topic_id):
        response = self._retry_call(requests.get, f"{self.api_url}/topics/{topic_id}")
        return response.json()


def get_pteam_and_service_data(
    tc_client: ThreatconnectomeClient, pteam_id: str, service_id: str, output_data: dict
):
    pteam = tc_client.get_pteam(pteam_id)
    output_data.update(pteam_id=pteam["pteam_id"], pteam_name=pteam["pteam_name"])
    for service in pteam["services"]:
        if service_id == service["service_id"]:
            output_data.update(
                service_id=service["service_id"],
                service_name=service["service_name"],
                service_description=service["description"],
            )


def get_threats_data(tc_client: ThreatconnectomeClient, service_id: str) -> list:
    params = {"service_id": service_id}
    threats = tc_client.get_threats(params)
    return threats


def get_tags_data(tc_client: ThreatconnectomeClient, pteam_id: str, service_id: str, threats: list):
    for threat in threats:
        dependency = tc_client.get_dependency(pteam_id, service_id, threat["dependency_id"])
        tag = tc_client.get_tag(dependency["tag_id"])
        threat.update(
            tag_id=dependency["tag_id"], tag_version=dependency["version"], tag_name=tag["tag_name"]
        )
        del threat["dependency_id"]


def get_misp_tag(tc_client: ThreatconnectomeClient, threats: list):
    """
    Remove threat that did not have cve_id in missp_tag.
    """
    _threats: list = []
    for threat in threats:
        topic = tc_client.get_topic(threat["topic_id"])
        cve_id: list = []
        for misp_tag in topic["misp_tags"]:
            if misp_tag["tag_name"] and misp_tag["tag_name"].startswith("CVE"):
                cve_id.append(misp_tag["tag_name"])

        if len(cve_id) == 0:
            continue
        else:
            threat.update(cve_id=cve_id)
            _threats.append(threat)

    return _threats


def output_json_file(threats: dict, pteam_id: str, service_id: str):
    filename = "collect_threats_data" + service_id + ".json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(threats, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", metavar="API_BASE_URL", type=str, help="API BASE URL of Threatconnectome"
    )
    parser.add_argument("-p", dest="pteam_id", type=str, help="set pteam_id")
    parser.add_argument("-s", dest="service_id", type=str, help="set service_id")
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

    tc_client = ThreatconnectomeClient(
        args.url,
        refresh_token,
        retry_max=3,
        connect_timeout=60.0,
        read_timeout=60.0,
    )

    output_data: dict = {}

    get_pteam_and_service_data(tc_client, args.pteam_id, args.service_id, output_data)
    threats = get_threats_data(tc_client, args.service_id)
    get_tags_data(tc_client, args.pteam_id, args.service_id, threats)
    _threats = get_misp_tag(tc_client, threats)
    output_data.update(threats=_threats)
    output_json_file(output_data, args.pteam_id, args.service_id)


if __name__ == "__main__":
    main()
