import argparse
import http.client as http_client
import os
import sys
from functools import partial
from time import sleep
from typing import Any, Callable
from uuid import UUID

import requests

http_client.HTTPConnection.debuglevel = 0  # set 1 for detailed debug

ENV_KEY_REFRESH_TOKEN = "THREATCONNECTOME_REFRESH_TOKEN"


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
                # "Content-Type": "application/json",  # oops, this causes upload_tags_file failure
            }
        )

    def refresh_auth_token(self, headers: dict) -> dict:
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

    def upload_tags_file(self, pteam_id: UUID | str, service: str, data: Any, force: bool):
        params = {
            "service": service,
            "force_mode": force,
        }
        files = {
            "file": ("tags_file.jsonl", data),  # filename should end with ".jsonl"
        }
        url = f"{self.api_url}/pteams/{pteam_id}/upload_tags_file"
        response = self.retry_call(requests.post, url, params=params, files=files)
        return response.json()


ARGUMENTS: list[tuple[str, dict]] = [
    (
        "pteam_id",
        {
            "help": "UUID of the pteam",
        },
    ),
    (
        "service",
        {
            "help": "Service name to apply",
        },
    ),
]
OPTIONS: list[tuple[str, str, dict]] = [
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
    (
        "-i",
        "--infile",
        {
            "required": False,
            "type": argparse.FileType("r"),
            "default": sys.stdin,
            "help": "Input file name. default is stdin.",
        },
    ),
    (
        "-b",
        "--block-new-tags",
        {
            "required": False,
            "action": "store_true",
            "default": False,
            "help": "Do not give force option which allows you to create new artifact tags.",
        },
    ),
    (
        "-g",
        "--gradual",
        {
            "required": False,
            "type": int,
            "default": 0,
            "help": "If GURADUAL > 0, try gradual update with specified number of lines.",
        },
    ),
]


def trace_message(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
    sys.stderr.flush()


def main(args: argparse.Namespace) -> None:
    if args.infile == sys.stdin:
        trace_message("reading data from STDIN...")
    tc_client = ThreatconnectomeClient(args.endpoint, args.refresh_token, retry_max=1)

    if args.gradual == 0:
        trace_message("processing update artifact tags.")
        lines = args.infile.read()  # process all lines at once
        tc_client.upload_tags_file(args.pteam_id, args.service, lines, not args.block_new_tags)
        trace_message("update completed.")
    else:
        trace_message("processing guradual update artifact tags.")
        all_lines = list(args.infile)
        all_lines_length = len(all_lines)
        limit = args.gradual if args.gradual < all_lines_length else all_lines_length
        while True:
            if limit > all_lines_length:
                limit = all_lines_length
            trace_message(f"uploading {limit} of {all_lines_length}...", end="")
            lines = "".join(all_lines[:limit])
            tc_client.upload_tags_file(args.pteam_id, args.service, lines, not args.block_new_tags)
            trace_message("done")
            if limit >= all_lines_length:
                break
            limit += args.gradual
        trace_message("guradual update completed.")


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

    if ARGS.gradual < 0:
        raise ValueError("error: argument -g/--gradual: expected 0 or positive integer")

    main(ARGS)
