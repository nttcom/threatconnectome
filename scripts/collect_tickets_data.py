import argparse
import json
import os
import sys
import urllib.parse
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

    def get_pteam(self, pteam_id) -> dict:
        try:
            response = self._retry_call(requests.get, f"{self.api_url}/pteams/{pteam_id}")
        except APIError as error:
            sys.exit("Is the pteam_id correct?\n" + str(error))
        return response.json()

    def get_tickets(self, pteam_id, params) -> list:
        try:
            response = self._retry_call(
                requests.get, f"{self.api_url}/pteams/{pteam_id}/tickets", params=params
            )
        except APIError as error:
            sys.exit("There is no tickets tied to service_id\n" + str(error))

        return response.json()

    def get_dependency(self, pteam_id, dependency_id):
        try:
            response = self._retry_call(
                requests.get,
                f"{self.api_url}/pteams/{pteam_id}/dependencies/{dependency_id}",
            )
        except APIError as error:
            sys.exit("Is the pteam_id correct?\n" + str(error))
        return response.json()

    def get_vuln(self, vuln_id):
        response = self._retry_call(requests.get, f"{self.api_url}/vulns/{vuln_id}")
        return response.json()


def get_pteam_and_service_data(
    tc_client: ThreatconnectomeClient, pteam_id: str, service_id: str
) -> dict:
    pteam_and_service_data: dict = {}
    pteam = tc_client.get_pteam(pteam_id)
    pteam_and_service_data.update(pteam_id=pteam["pteam_id"], pteam_name=pteam["pteam_name"])
    for service in pteam["services"]:
        if service_id == service["service_id"]:
            pteam_and_service_data.update(
                service_id=service["service_id"],
                service_name=service["service_name"],
                service_description=service["description"],
                service_safety_impact=service["service_safety_impact"],
            )
            break

    if "service_name" not in pteam_and_service_data:
        sys.exit("ERROR: The pairing of pteam_id and service_id is incorrect")

    return pteam_and_service_data


def get_tickets_data(tc_client: ThreatconnectomeClient, pteam_id: str, service_id: str) -> list:
    params = {"service_id": service_id}
    tickets = tc_client.get_tickets(pteam_id, params)

    if len(tickets) == 0:
        sys.exit("The tickets data associated with service_id is empty")

    return tickets


def generate_purl(package_name: str, package_ecosystem: str, package_version: str) -> str:
    # The type must NOT be percent-encoded
    name = urllib.parse.quote(package_name)
    version = urllib.parse.quote(package_version)

    return f"pkg:{package_ecosystem}/{name}@{version}"


def add_package_data_to_ticket(
    tc_client: ThreatconnectomeClient, pteam_id: str, tickets: list
) -> list:
    tickets_with_packages_data: list = []
    for ticket in tickets:
        dependency = tc_client.get_dependency(pteam_id, ticket["dependency_id"])
        purl = generate_purl(
            dependency["package_name"],
            dependency["package_ecosystem"],
            dependency["package_version"],
        )

        ticket_with_package_data = {
            "purl": purl,
            "ticket_id": ticket["ticket_id"],
            "ticket_safety_impact": ticket["ticket_safety_impact"],
            "vuln_id": ticket["vuln_id"],
            "package_version_id": dependency["package_version_id"],
            "version": dependency["package_version"],
            "package_id": dependency["package_id"],
            "package_name": dependency["package_name"],
            "ecosystem": dependency["package_ecosystem"],
            "package_manager": dependency["package_manager"],
            "target": dependency["target"],
        }
        tickets_with_packages_data.append(ticket_with_package_data)

    return tickets_with_packages_data


def add_cve_data_to_ticket(tc_client: ThreatconnectomeClient, tickets: list) -> list:
    """
    Remove ticket that did not have cve_id.
    """
    ticket_with_cve_data: list = []
    for ticket in tickets:
        vuln = tc_client.get_vuln(ticket["vuln_id"])

        if vuln["cve_id"] and vuln["cve_id"].startswith("CVE"):
            ticket.update(cve_id=vuln["cve_id"])
            ticket_with_cve_data.append(ticket)

    return ticket_with_cve_data


def output_json_file(tickets: dict, service_id: str):
    filename = "collect_tickets_data_" + service_id + ".json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)


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

    pteam_and_service_data = get_pteam_and_service_data(tc_client, args.pteam_id, args.service_id)
    tickets = get_tickets_data(tc_client, args.pteam_id, args.service_id)
    tickets_with_packages_data = add_package_data_to_ticket(tc_client, args.pteam_id, tickets)
    tickets_with_package_and_cve_data = add_cve_data_to_ticket(
        tc_client, tickets_with_packages_data
    )

    output_data: dict = {}
    output_data = pteam_and_service_data
    output_data.update(tickets=tickets_with_package_and_cve_data)
    output_json_file(output_data, args.service_id)


if __name__ == "__main__":
    main()
