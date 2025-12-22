# !/usr/bin/env python3

import argparse
import json
import os
import random
import re
import sys
import uuid
from functools import partial
from pathlib import Path
from time import sleep
from typing import Callable

import requests
from boltdb import BoltDB

vuln_filter = ["GHSA-", "CVE-", "PYSEC-", "OSV-", "GO-"]
allow_list = [
    # b"CBL-Mariner 1.0",
    # b"CBL-Mariner 2.0",
    # b"Oracle Linux 5",
    # b"Oracle Linux 6",
    # b"Oracle Linux 7",
    # b"Oracle Linux 8",
    # b"Oracle Linux 9",
    # b"Photon OS 1.0",
    # b"Photon OS 2.0",
    # b"Photon OS 3.0",
    # b"Photon OS 4.0",
    # b"Photon OS 5.0",
    # b"Red Hat",
    # b"Red Hat CPE",
    # b"SUSE Linux Enterprise 11",
    # b"SUSE Linux Enterprise 11.1",
    # b"SUSE Linux Enterprise 11.2",
    # b"SUSE Linux Enterprise 11.3",
    # b"SUSE Linux Enterprise 11.4",
    # b"SUSE Linux Enterprise 12",
    # b"SUSE Linux Enterprise 12.1",
    # b"SUSE Linux Enterprise 12.2",
    # b"SUSE Linux Enterprise 12.3",
    # b"SUSE Linux Enterprise 12.4",
    # b"SUSE Linux Enterprise 12.5",
    # b"SUSE Linux Enterprise 15",
    # b"SUSE Linux Enterprise 15.1",
    # b"SUSE Linux Enterprise 15.2",
    # b"SUSE Linux Enterprise 15.3",
    # b"SUSE Linux Enterprise 15.4",
    # b"SUSE Linux Enterprise 15.5",
    # b"alma 8",
    # b"alma 9",
    # b"alpine 3.10",
    # b"alpine 3.11",
    # b"alpine 3.12",
    # b"alpine 3.13",
    # b"alpine 3.14",
    b"alpine 3.15",
    b"alpine 3.16",
    b"alpine 3.17",
    b"alpine 3.18",
    b"alpine 3.19",
    b"alpine 3.20",
    b"alpine 3.21",
    b"alpine 3.22",
    # b"alpine 3.2",
    # b"alpine 3.3",
    # b"alpine 3.4",
    # b"alpine 3.5",
    # b"alpine 3.6",
    # b"alpine 3.7",
    # b"alpine 3.8",
    # b"alpine 3.9",
    # b"alpine edge",
    # b"amazon linux 1",
    # b"amazon linux 2",
    # b"amazon linux 2022",
    # b"amazon linux 2023",
    # b"bitnami::Bitnami Vulnerability Database",
    b"cargo::GitHub Security Advisory Rust",
    # b"chainguard",
    # b"cocoapods::GitHub Security Advisory Swift",
    # b"composer::GitHub Security Advisory Composer",
    b"composer::PHP Security Advisories Database",
    # b"conan::GitLab Advisory Database Community",
    # b"data-source",
    b"debian 10",
    b"debian 11",
    b"debian 12",
    b"debian 13",
    # b"debian 7",
    # b"debian 8",
    # b"debian 9",
    # b"erlang::GitHub Security Advisory Erlang",
    b"go::GitHub Security Advisory Go",
    b"go::The Go Vulnerability Database",
    # b"k8s::Official Kubernetes CVE Feed",
    b"maven::GitHub Security Advisory Maven",
    b"maven::GitLab Advisory Database Community",
    b"npm::GitHub Security Advisory npm",
    b"npm::Node.js Ecosystem Security Working Group",
    # b"nuget::GitHub Security Advisory NuGet",
    # b"openSUSE Leap 15.0",
    # b"openSUSE Leap 15.1",
    # b"openSUSE Leap 15.2",
    # b"openSUSE Leap 15.3",
    # b"openSUSE Leap 15.4",
    # b"openSUSE Leap 15.5",
    # b"openSUSE Leap 42.1",
    # b"openSUSE Leap 42.2",
    # b"openSUSE Leap 42.3",
    b"pip::GitHub Security Advisory pip",
    # b"pub::GitHub Security Advisory Pub",
    b"rocky 8",
    b"rocky 9",
    b"rubygems::GitHub Security Advisory RubyGems",
    b"rubygems::Ruby Advisory Database",
    # b"swift::GitHub Security Advisory Swift",
    # b"ubuntu 12.04",
    # b"ubuntu 12.04-ESM",
    # b"ubuntu 12.10",
    # b"ubuntu 13.04",
    # b"ubuntu 13.10",
    # b"ubuntu 14.04",
    # b"ubuntu 14.04-ESM",
    # b"ubuntu 14.10",
    # b"ubuntu 15.04",
    # b"ubuntu 15.10",
    # b"ubuntu 16.04",
    # b"ubuntu 16.04-ESM",
    # b"ubuntu 16.10",
    # b"ubuntu 17.04",
    # b"ubuntu 17.10",
    b"ubuntu 18.04",
    # b"ubuntu 18.10",
    # b"ubuntu 19.04",
    # b"ubuntu 19.10",
    b"ubuntu 20.04",
    # b"ubuntu 20.10",
    # b"ubuntu 21.04",
    # b"ubuntu 21.10",
    b"ubuntu 22.04",
    # b"ubuntu 22.10",
    # b"ubuntu 23.04",
    b"ubuntu 24.04",
    # b"wolfi",
]

# https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/analyzer/os/const.go
# diff: "SUSE" -> "sles",
os_families = {
    "Oracle": "oracle",
    "Photon": "photon",
    "Red": "redhat",
    "SUSE": "sles",
    "alma": "alma",
    "alpine": "alpine",
    "amazon": "amazon",
    "archlinux": "archlinux",
    "debian": "debian",
    "openSUSE": "opensuse",
    "rocky": "rocky",
    "ubuntu": "ubuntu",
    "wolfi": "wolfi",
}


lang_families = {
    # lang_pkg_raw_data: package_info
    "pip": "pypi",
    "npm": "npm",
    "cargo": "cargo",
    "rubygems": "gem",
    "maven": "maven",
    "go": "golang",
    "composer": "composer",
}


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

    def get_vulns(self, offset, limit) -> dict:
        response = self._retry_call(
            requests.get, f"{self.api_url}/vulns?offset={offset}&limit={limit}", use_api_key=False
        )
        return response.json()

    def create_or_update_vuln(self, vuln_id: str, vuln: dict) -> None:
        api_endpoint = f"{self.api_url}/vulns/{vuln_id}"
        print(f"Put {api_endpoint}")
        response = self._retry_call(requests.put, api_endpoint, json=vuln, use_api_key=True)
        print(f"Http status: {response.status_code} {response.reason}")


def create_os_package_info(os_repos):
    key = os_repos.decode().split(" ", 1)[0]
    family_name = os_families[key]
    if family_name in ["redhat", "archlinux", "wolfi"]:
        os_name = family_name
        version = ""
    else:
        raw_os_text, raw_version_text = os_repos.decode().rsplit(" ", 1)
        if raw_os_text == "openSUSE Leap":
            os_name = "opensuse.leap"
        else:
            os_name = family_name

        version = raw_version_text.lower()
    return f"{os_name}-{version}" if version else f"{os_name}"


def get_package_info(repos):
    if b"::" in repos:  # lang-pkgs
        lang_pkg_raw_data = repos.decode().split("::", 1)[0]
        lang_ecosystem_info = lang_families[lang_pkg_raw_data]
        return f"{lang_ecosystem_info}"
    # os-pkgs
    os_package_info = create_os_package_info(repos)
    return f"{os_package_info}"


def vuln_info(repos, txs):
    repos_bucket = txs.bucket(repos)
    vulns = []
    for pkg, _ in repos_bucket:
        pkg_bucket = repos_bucket.bucket(pkg)
        for vuln, _ in pkg_bucket:
            vuln_dict = {"vuln_id": "", "pkg_name": "", "version_details": None}
            vuln_id = vuln.decode()
            for pattern in vuln_filter:
                if pattern in vuln_id:
                    vuln_dict["vuln_id"] = vuln_id
                    vuln_dict["pkg_name"] = pkg.decode().replace(":", "/")
                    vuln_content = pkg_bucket.get(vuln).decode()
                    if vuln_content:
                        vuln_dict["version_details"] = json.loads(vuln_content)
                        vulns.append(vuln_dict)
    return vulns


def get_versions_from_trivy_vuln(vuln) -> tuple[list[str] | None, list[str] | None]:
    fixed_versions = []
    vulnerable_versions = None

    if vuln["version_details"]:
        if "FixedVersion" in vuln["version_details"].keys():
            fixed_versions.append(vuln["version_details"]["FixedVersion"])
        if "PatchedVersions" in vuln["version_details"].keys():
            fixed_versions += vuln["version_details"]["PatchedVersions"]
        if "VulnerableVersions" in vuln["version_details"].keys():
            vulnerable_versions = vuln["version_details"]["VulnerableVersions"]

    return vulnerable_versions, fixed_versions


def get_vulns_data(tc_client: ThreatconnectomeClient, offset, limit):
    result = {}

    while True:
        vulns_response = tc_client.get_vulns(offset, limit)

        # Finish when response is empty
        if not vulns_response or not vulns_response.get("vulns"):
            break

        result.update(
            {
                vuln["vuln_id"]: convert_vuln_to_checkable_data(vuln)
                for vuln in vulns_response["vulns"]
            }
        )
        offset += limit

    return result


def convert_vuln_to_checkable_data(vuln: dict) -> dict:
    sorted_vulnerable_packages = sorted(
        vuln["vulnerable_packages"],
        key=lambda vulnerable_package: (
            vulnerable_package["affected_name"],
            vulnerable_package["ecosystem"],
        ),
    )
    return {
        "title": vuln["title"],
        "cve_id": vuln["cve_id"],
        "detail": vuln["detail"],
        "cvss_v3_score": vuln["cvss_v3_score"],
        "vulnerable_packages": [
            {
                "affected_name": vulnerable_package["affected_name"],
                "ecosystem": vulnerable_package["ecosystem"],
                "affected_versions": sorted(vulnerable_package["affected_versions"]),
                "fixed_versions": sorted(vulnerable_package["fixed_versions"]),
            }
            for vulnerable_package in sorted_vulnerable_packages
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", metavar="API_BASE_URL", type=str, help="API BASE URL of Threatconnectome"
    )
    parser.add_argument("-d", dest="trivy_db", type=str, help="load the Trivy DB from this path")
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
    parser.add_argument(
        "--force-update",
        dest="update",
        action="store_true",
        help="Option to force update existing topic",
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
        api_key = os.environ.get("VULN_API_KEY")

    if not api_key:
        sys.exit(
            "ERROR: Require the API Key for Threatconnectome.\n"
            "You can use '-k API_KEY' or 'export VULN_API_KEY=\"XXXXXX\"'."
        )

    trivy_db = Path(args.trivy_db).expanduser()
    bdb = BoltDB(trivy_db)

    vuln_dict: dict[str, dict[str, dict | set | str | None]] = {}
    with bdb.view() as txs:
        for repos, _ in txs.bucket():
            if repos in allow_list:
                category = get_package_info(repos)
                vulns = vuln_info(repos, txs)
                for trivy_vuln in vulns:
                    vuln_vers, fix_vers = get_versions_from_trivy_vuln(trivy_vuln)
                    if vuln_vers is None and fix_vers is None:
                        continue
                    trivy_vuln_id = trivy_vuln["vuln_id"]
                    vuln_obj = vuln_dict.get(trivy_vuln_id, {"affects": {}})
                    package = (trivy_vuln["pkg_name"], category)

                    # Ensure "affects" is dict
                    assert isinstance(vuln_obj["affects"], dict)
                    affect_obj = vuln_obj["affects"].get(
                        package,
                        {
                            "affected_versions": set(),
                            "fixed_versions": set(),
                        },
                    )

                    # Update "affected_versions"
                    affect_vers_obj = affect_obj["affected_versions"]
                    affect_vers_obj.update(vuln_vers or [])
                    affect_obj["affected_versions"] = affect_vers_obj

                    # Update "fixed_versions"
                    fixed_vers_obj = affect_obj["fixed_versions"]
                    fixed_vers_obj.update(fix_vers or [])
                    affect_obj["fixed_versions"] = fixed_vers_obj

                    # Update the "vuln_dict"
                    vuln_obj["affects"][package] = affect_obj
                    vuln_dict[trivy_vuln_id] = vuln_obj

        trivy_vulns: dict[str, dict] = {}
        vuln_bucket = txs.bucket(b"vulnerability")
        for trivy_vuln_id, trivy_vuln_content in vuln_dict.items():
            # Generate a tc vuln uuid from tirvy Vuln ID
            random.seed(trivy_vuln_id)
            tc_vuln_id = str(uuid.UUID(int=random.getrandbits(128), version=4))

            bucket_content = vuln_bucket.get(trivy_vuln_id.encode())
            if bucket_content:
                trivy_vuln_details = json.loads(bucket_content.decode())
                if "Title" in trivy_vuln_details:
                    title = trivy_vuln_details["Title"]
                else:
                    title = trivy_vuln_id
                if "Description" in trivy_vuln_details:
                    detail = trivy_vuln_details["Description"]
                elif "References" in trivy_vuln_details:
                    detail = "\n".join(trivy_vuln_details["References"])
                else:
                    detail = "There is no description."

                if (
                    "CVSS" in trivy_vuln_details
                    and "nvd" in trivy_vuln_details["CVSS"]
                    and "V3Score" in trivy_vuln_details["CVSS"]["nvd"]
                ):
                    cvss_v3_score = float(trivy_vuln_details["CVSS"]["nvd"]["V3Score"])
                else:
                    cvss_v3_score = None

            else:
                title = trivy_vuln_id
                detail = "This Vuln is not yet published."
                cvss_v3_score = None

            if trivy_vuln_content["affects"]:
                assert isinstance(trivy_vuln_content["affects"], dict)
                vulnerable_packages = []
                for key, value in trivy_vuln_content["affects"].items():
                    vulnerable_package = {
                        "affected_name": key[0],
                        "ecosystem": key[1],
                        "affected_versions": sorted(list(value["affected_versions"])),
                        "fixed_versions": sorted(list(value["fixed_versions"])),
                    }
                    vulnerable_packages.append(vulnerable_package)

                sorted_vulnerable_packages = sorted(
                    vulnerable_packages,
                    key=lambda vulnerable_package: (
                        vulnerable_package["affected_name"],
                        vulnerable_package["ecosystem"],
                    ),
                )

            CVE_PATTERN = r"^CVE-\d{4}-\d{4,}$"
            cve_id = trivy_vuln_id if re.match(CVE_PATTERN, trivy_vuln_id) else None
            trivy_vulns[tc_vuln_id] = {
                "title": title,
                "cve_id": cve_id,
                "detail": detail,
                "cvss_v3_score": cvss_v3_score,
                "vulnerable_packages": sorted_vulnerable_packages,
            }

    tc_client = ThreatconnectomeClient(
        args.url,
        refresh_token,
        api_key=api_key,
        retry_max=3,
        connect_timeout=60.0,
        read_timeout=60.0,
    )

    existing_vulns = get_vulns_data(tc_client, 0, 100)

    for tc_vuln_id, trivy_vuln in trivy_vulns.items():
        if tc_vuln_id not in existing_vulns:  # new tc vuln
            tc_client.create_or_update_vuln(tc_vuln_id, trivy_vuln)
            continue

        # existing vuln
        if args.update:  # force update mode
            tc_client.create_or_update_vuln(tc_vuln_id, trivy_vuln)
            continue

        if existing_vulns[tc_vuln_id] != trivy_vuln:  # vuln updated
            tc_client.create_or_update_vuln(tc_vuln_id, trivy_vuln)
            continue


if __name__ == "__main__":
    main()
