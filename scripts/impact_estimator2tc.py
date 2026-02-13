import argparse
import json
import os
import sys
from functools import partial
from pathlib import Path
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

    def put_ticket(
        self,
        pteam_id: str,
        ticket_id: str,
        ticket_safety_impact: str,
        ticket_safety_impact_change_reason: str,
    ) -> None:
        request = {
            "ticket_safety_impact": ticket_safety_impact,
            "ticket_safety_impact_change_reason": ticket_safety_impact_change_reason,
        }
        self._retry_call(
            requests.put, f"{self.api_url}/pteams/{pteam_id}/tickets/{ticket_id}", json=request
        )


def parse_ticket_dict_by_tickets_data(tickets_data: dict) -> dict:
    ticket_dict = {}
    for ticket in tickets_data.get("tickets", []):
        ticket_id = ticket.get("ticket_id")
        if ticket_id:
            ticket_dict[ticket_id] = {
                "pteam_id": tickets_data.get("pteam_id"),
                "purl": ticket.get("purl"),
                "cve_id": ticket.get("cve_id"),
                "target": ticket.get("target"),
            }
    return ticket_dict


def parse_ticket_dict(tickets_data_path: Path) -> dict:
    try:
        with open(tickets_data_path, encoding="utf-8") as f:
            tickets_data = json.load(f)
            return parse_ticket_dict_by_tickets_data(tickets_data)
    except FileNotFoundError:
        sys.exit(f"Error: Specified file not found. path: {tickets_data_path}")
    except json.JSONDecodeError:
        sys.exit(f"Error: Invalid JSON format in file content. path: {tickets_data_path}")


def parse_process_safety_impact_by_process_safety_impact(process_safety_impact: dict) -> dict:
    dependency_file_dict = {}
    for vulpackage in process_safety_impact.get("vulpackage_dicts", []):
        evaluate_id = vulpackage.get("evaluateId")
        if evaluate_id is not None:
            dependency_file_dict[evaluate_id] = vulpackage.get("dependency_file")
    return dependency_file_dict


def parse_process_safety_impact(process_safety_impact_path: Path) -> dict:
    try:
        with open(process_safety_impact_path, encoding="utf-8") as f:
            process_safety_impact = json.load(f)
            return parse_process_safety_impact_by_process_safety_impact(process_safety_impact)
    except FileNotFoundError:
        sys.exit(f"Error: Specified file not found. path: {process_safety_impact_path}")
    except json.JSONDecodeError:
        sys.exit(f"Error: Invalid JSON format in file content. path: {process_safety_impact_path}")


def parse_safety_impact_by_safety_impact_data(
    dependency_file_dict: dict, safety_impact: dict
) -> dict:
    safety_impact_data = {}
    for safety_impact_result in safety_impact.get("safetyImpactResults", []):
        evaluate_id = safety_impact_result.get("evaluateId")
        dependency_file = dependency_file_dict.get(evaluate_id)

        affected_packages = safety_impact_result.get("affectedPackages")
        if not affected_packages:
            continue
        purl = affected_packages[0].get("purl")

        vulnerability = safety_impact_result.get("vulnerability")
        if not vulnerability:
            continue
        cve_id = vulnerability.get("cveId")

        estimated_damage = safety_impact_result.get("estimatedDamage")
        if not estimated_damage:
            continue
        abstract = estimated_damage.get("abstract")

        safety_impact = safety_impact_result.get("safetyImpact")
        if not safety_impact:
            continue
        safetyImpact_value = safety_impact.get("value")

        key = (purl, cve_id, dependency_file)
        safety_impact_data[key] = {
            "abstract": abstract,
            "safetyImpact": safetyImpact_value,
        }
    return safety_impact_data


def parse_safety_impact_by_safety_impact_file(
    safety_impact_path: Path, dependency_file_dict: dict
) -> dict:
    try:
        with open(safety_impact_path, encoding="utf-8") as f:
            safety_impact = json.load(f)
            return parse_safety_impact_by_safety_impact_data(dependency_file_dict, safety_impact)
    except FileNotFoundError:
        sys.exit(f"Error: Specified file not found. path: {safety_impact_path}")
    except json.JSONDecodeError:
        sys.exit(f"Error: Invalid JSON format in file content. path: {safety_impact_path}")


def parse_safety_impact(safety_impact_path: Path, process_safety_impact_path: Path) -> dict:
    dependency_file_dict = parse_process_safety_impact(process_safety_impact_path)
    return parse_safety_impact_by_safety_impact_file(safety_impact_path, dependency_file_dict)


def set_safety_impact(
    ticket_dict: dict, safety_impact_data: dict, tc_client: ThreatconnectomeClient
) -> None:
    for ticket_id, ticket_data in ticket_dict.items():
        pteam_id = ticket_data.get("pteam_id")
        key = (ticket_data.get("purl"), ticket_data.get("cve_id"), ticket_data.get("target"))
        safety_impact = safety_impact_data.get(key)
        if not safety_impact:
            sys.exit("Error: Unmatch ticket data. ticket_id: " + ticket_id)

        ticket_safety_impact = safety_impact.get("safetyImpact")
        if ticket_safety_impact is None:
            sys.exit("Error: Failed to retrieve safetyImpact properly. ticket_id: " + ticket_id)

        ticket_safety_impact_change_reason = safety_impact.get("abstract")
        tc_client.put_ticket(
            pteam_id, ticket_id, ticket_safety_impact.lower(), ticket_safety_impact_change_reason
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", metavar="API_BASE_URL", type=str, help="API BASE URL of Threatconnectome"
    )
    parser.add_argument(
        "-d",
        dest="tickets_data_path",
        type=Path,
        help="data generated by collect_tickets_data.py",
    )
    parser.add_argument(
        "-s",
        dest="safety_impact_path",
        type=Path,
        help="safety impact data generated by ImpactEstimator",
    )
    parser.add_argument(
        "-p",
        dest="process_safety_impact_path",
        type=Path,
        help="process safety impact data generated by ImpactEstimator",
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

    tc_client = ThreatconnectomeClient(
        args.url,
        refresh_token,
        retry_max=3,
        connect_timeout=60.0,
        read_timeout=60.0,
    )

    ticket_dict = parse_ticket_dict(args.tickets_data_path)
    safety_impact_data = parse_safety_impact(
        args.safety_impact_path, args.process_safety_impact_path
    )
    set_safety_impact(ticket_dict, safety_impact_data, tc_client)


if __name__ == "__main__":
    main()
