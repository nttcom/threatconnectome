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
    api_key: str | None
    retry_max: int  # 0 for never, negative for forever
    connect_timeout: float
    read_timeout: float
    headers: dict

    def __init__(
        self,
        api_url: str,
        refresh_token: str,
        api_key: str | None = None,
        retry_max: int = -1,
        connect_timeout: float = 60.0,
        read_timeout: float = 60.0,
    ):
        self.api_url = api_url.rstrip("/")
        self.refresh_token = refresh_token
        self.api_key = api_key
        self.retry_max = retry_max
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

        base_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        self.headers = self._refresh_auth_token(base_headers)

    def _refresh_auth_token(self, headers: dict) -> dict:
        resp = requests.post(
            f"{self.api_url}/auth/refresh",
            headers={"Content-Type": "application/json"},
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
        use_api_key: bool = False,
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
            try:
                data = resp.json()
                return f"{resp.status_code}: {resp.reason}: {data.get('detail')}"
            except ValueError:
                return f"{resp.status_code}: {resp.reason}: {resp.text}"

        while True:
            request_headers = self.headers.copy()
            if use_api_key and self.api_key:
                request_headers["X-API-Key"] = self.api_key

            try:
                resp = _func(headers=request_headers)
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

    def get_vulns(self, params: dict) -> dict:
        response = self._retry_call(
            requests.get, f"{self.api_url}/vulns", params=params, use_api_key=False
        )
        return response.json()

    def update_vuln(self, vuln_id: str, vuln_data: dict) -> requests.Response:
        return self._retry_call(
            requests.put, f"{self.api_url}/vulns/{vuln_id}", json=vuln_data, use_api_key=True
        )


def _json_loads(filepath: str | bytes | bytearray):
    with open(filepath, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as error:
            raise Exception(
                "Wrong file content: " + f'{"..." if len(filepath) > 32 else ""}{filepath[32:]!s}'
            ) from error


def _get_cve_data_from_json_data(vulnrichment_json: dict) -> tuple:
    if "adp" not in vulnrichment_json["containers"]:
        return ()

    adp_vulnrichment = next(
        filter(
            lambda x: x.get("title") == "CISA ADP Vulnrichment",
            vulnrichment_json["containers"]["adp"],
        ),
        None,
    )
    if not adp_vulnrichment:
        return ()

    if all("other" not in x for x in adp_vulnrichment["metrics"]):
        return ()

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
        return ()

    return (content["id"], exploitation, automatable)


def _get_cve_data_list(vulnrichment_path: str) -> list[tuple]:
    cve_data_list: list[tuple] = []
    for cve_filepath in glob.iglob(vulnrichment_path + "/**/CVE-*.json", recursive=True):
        try:
            current_cve_data = _get_cve_data_from_json_data(_json_loads(cve_filepath))
            if len(current_cve_data) == 3:
                cve_data_list.append(current_cve_data)
        except OSError as error:
            print(f"Json open error. filepath:{cve_filepath} detail:{error}")
            continue
        except (KeyError, TypeError) as error:
            print(f"Json parsing error. filepath:{cve_filepath} detail:{error}")
            continue
    cve_data_list.sort()
    print(f"Find cve data. count:{len(cve_data_list)}")
    for cve_data in cve_data_list:
        print(cve_data[0])
    return cve_data_list


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


def _update_vulns_by_cve_data(
    tc_client: ThreatconnectomeClient, cve_id: str, exploitation: str, automatable: str
) -> None:
    params = {"cve_ids": [cve_id]}

    vulns_response = tc_client.get_vulns(params)
    for vuln in vulns_response["vulns"]:
        vuln_id = vuln["vuln_id"]
        vuln_data = {
            "exploitation": _get_exploitation_value(exploitation),
            "automatable": _get_automatable_value(automatable),
        }
        response = tc_client.update_vuln(vuln_id, vuln_data)
        if response.status_code == 200:
            print(f"Success put vuln. vuln_id:{vuln_id} cve_id:{cve_id} data: {vuln_data}")
        else:
            print(f"Faild put vuln. Http status: {response.status_code} {response.reason}")


def _update_vulns_by_cve_data_dict(
    tc_client: ThreatconnectomeClient, cve_data_list: list[tuple]
) -> None:
    for cve_data in cve_data_list:
        _update_vulns_by_cve_data(tc_client, cve_data[0], cve_data[1], cve_data[2])


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
    parser.add_argument(
        "-k",
        "--api-key",
        dest="api_key",
        type=str,
        help="set the API key for patching vulnerability information in threatconnectome",
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

    # Get API key from argument or environment variable
    if args.api_key:
        api_key = args.api_key
    else:
        api_key = os.environ.get("SYSTEM_API_KEY")

    if not api_key:
        sys.exit(
            "ERROR: Require the API Key for Threatconnectome.\n"
            "You can use '-k API_KEY' or 'export SYSTEM_API_KEY=\"XXXXXX\"'."
        )

    tc_client = ThreatconnectomeClient(
        args.url,
        refresh_token,
        api_key=api_key,
        retry_max=3,
        connect_timeout=60.0,
        read_timeout=60.0,
    )

    cve_data_list = _get_cve_data_list(args.vulnrichment_path)
    _update_vulns_by_cve_data_dict(tc_client, cve_data_list)


if __name__ == "__main__":
    main()
