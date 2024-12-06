# !/usr/bin/env python3

import argparse
import json
import os
import random
import sys
import uuid
from functools import partial
from hashlib import md5
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
    # b"composer::PHP Security Advisories Database",
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
    # b"rocky 8",
    # b"rocky 9",
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
}


lang_families = {
    # lang_pkg_raw_data: package_info
    "pip": "pypi",
    "npm": "npm",
    "cargo": "cargo",
    "rubygems": "gem",
    "maven": "maven",
    "go": "golang",
}


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

    def get_topics(self) -> dict:
        response = self._retry_call(requests.get, f"{self.api_url}/topics")
        return response.json()

    def get_topic(self, topic_id) -> dict:
        response = self._retry_call(requests.get, f"{self.api_url}/topics/{topic_id}")
        return response.json()

    def create_tag(self, tag_name: str) -> None:
        api_endpoint = f"{self.api_url}/tags"
        print(f"Post {api_endpoint} to create tag: {tag_name}")
        response = self._retry_call(requests.post, api_endpoint, json={"tag_name": tag_name})
        print(f"Http status: {response.status_code} {response.reason}")

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
        response = self._retry_call(requests.post, api_endpoint, json=topic)
        print(f"Http status: {response.status_code} {response.reason}")

    def create_topic(self, topic_id: str, topic: dict) -> None:
        self.with_auto_create_tags(self._create_topic, topic_id, topic)

    def _update_topic_and_actions(self, topic_id: str, topic: dict) -> None:
        api_endpoint = f"{self.api_url}/topics/{topic_id}"
        print(f"Put {api_endpoint}")
        response = self._retry_call(requests.put, api_endpoint, json=topic)
        print(f"Http status: {response.status_code} {response.reason}")
        for action in topic.get("actions") or []:
            try:
                api_endpoint = f"{self.api_url}/actions"
                print(f"Post {api_endpoint}")
                response = self._retry_call(
                    requests.post, api_endpoint, json={**action, "topic_id": topic_id}
                )
                print(f"Http status: {response.status_code} {response.reason}")
            except APIError as error:
                if str(error) == "ERROR: 400: Bad Request: Action id already exists":
                    api_endpoint = f"{self.api_url}/actions/{action['action_id']}"
                    print(f"Put {api_endpoint}")
                    self._retry_call(requests.put, api_endpoint, json=action)
                    print(f"Http status: {response.status_code} {response.reason}")
                else:
                    raise error

    def update_topic_and_actions(self, topic_id: str, topic: dict) -> None:
        self.with_auto_create_tags(self._update_topic_and_actions, topic_id, topic)


def create_os_tag_info(os_repos):
    key = os_repos.decode().split(" ", 1)[0]
    family_name = os_families[key]
    if family_name in ["redhat", "archlinux"]:
        os_name = family_name
        version = ""
    else:
        raw_os_text, raw_version_text = os_repos.decode().rsplit(" ", 1)
        if raw_os_text == "openSUSE Leap":
            os_name = "opensuse.leap"
        else:
            os_name = family_name

        version = raw_version_text.lower()
    return f"{os_name}-{version}:" if version else f"{os_name}:"


def get_package_info(repos):
    if b"::" in repos:  # lang-pkgs
        lang_pkg_raw_data = repos.decode().split("::", 1)[0]
        lang_tag_info = lang_families[lang_pkg_raw_data]
        return f"{lang_tag_info}:"
    # os-pkgs
    os_tag_info = create_os_tag_info(repos)
    return f"{os_tag_info}"


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


def solution_from_vuln(vuln) -> tuple[str | None, str | None, str | None]:
    if vuln["version_details"]:
        solution, vuln_vers, fix_vers = make_update_action(
            vuln["pkg_name"], vuln["version_details"]
        )
        if solution:
            return solution, vuln_vers, fix_vers
    return None, None, None


def make_update_action(pkg_name, version_details: dict):
    fixed_versions = []
    vulnerable_versions = None

    if "FixedVersion" in version_details.keys():
        fixed_versions.append(version_details["FixedVersion"])
    if "PatchedVersions" in version_details.keys():
        fixed_versions += version_details["PatchedVersions"]
    if "VulnerableVersions" in version_details.keys():
        vulnerable_versions = version_details["VulnerableVersions"]

    if vulnerable_versions and fixed_versions:
        action = f"Update {pkg_name} from version {vulnerable_versions} to {fixed_versions}"
    elif fixed_versions:
        action = f"Update {pkg_name} to version {fixed_versions}"
        if len(fixed_versions) == 1 and "," not in fixed_versions[0]:
            # guess vulnerable version only if we can
            fixed_version = fixed_versions[0]
            if fixed_version.startswith(">="):
                vulnerable_version = fixed_version.replace(">=", "<", 1)
            elif fixed_version.startswith(">"):
                vulnerable_version = fixed_version.replace(">", "<=", 1)
            elif fixed_version.startswith("~>="):
                vulnerable_version = fixed_version.replace("~>=", "<", 1)
            elif fixed_version.startswith("~>"):
                vulnerable_version = fixed_version.replace("~>", "<=", 1)
            else:
                vulnerable_version = f"< {fixed_version}"
            vulnerable_versions = [vulnerable_version]
    else:
        action = None

    fixed_versions_str = ",".join(fixed_versions)

    return action, vulnerable_versions, fixed_versions_str


def _gen_action_id(topic_id: uuid.UUID | str, tags: list[str], action: str) -> str:
    random.seed(f"{topic_id}-{','.join(tags)}-{action}")
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def calculate_topic_content_fingerprint(topic: dict) -> str:
    tag_names = (
        [tag["tag_name"] for tag in topic["tags"]]
        if len(topic["tags"]) > 0 and isinstance(topic["tags"][0], dict)
        else topic["tags"]
    )
    data = {
        "title": topic["title"],
        "abstract": topic["abstract"],
        "cvss_v3_score": topic["cvss_v3_score"],
        "tag_names": sorted(set(tag_names)),
    }
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


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

    trivy_db = Path(args.trivy_db).expanduser()
    bdb = BoltDB(trivy_db)

    vuln_dict: dict[str, dict[str, dict | set | str | None]] = {}
    with bdb.view() as txs:
        for repos, _ in txs.bucket():
            if repos in allow_list:
                # create tag strings except packagename
                category = get_package_info(repos)
                vulns = vuln_info(repos, txs)
                for vuln in vulns:
                    solution, vuln_vers, fix_vers = solution_from_vuln(vuln)
                    if not solution:
                        continue
                    vuln_id = vuln["vuln_id"]
                    vuln_obj = vuln_dict.get(
                        vuln_id, {"tags": set(), "actions": {}, "fix_vers": {}}
                    )
                    tag = f"{vuln['pkg_name']}:{category}"
                    assert isinstance(vuln_obj["tags"], set)
                    vuln_obj["tags"].add(tag)
                    assert isinstance(vuln_obj["actions"], dict)
                    act_obj = vuln_obj["actions"].get(
                        solution,
                        {
                            "action": solution,
                            "action_type": "elimination",
                            "recommended": True,
                            "ext": {
                                "tags": set(),
                                "vulnerable_versions": {},  # {tag: versions}
                            },
                        },
                    )
                    act_obj["ext"]["tags"].add(tag)
                    vers_obj = act_obj["ext"]["vulnerable_versions"].get(tag, set())
                    vers_obj.update(vuln_vers or [])
                    act_obj["ext"]["vulnerable_versions"][tag] = vers_obj
                    vuln_obj["actions"][solution] = act_obj
                    vuln_obj["fix_vers"] = fix_vers
                    vuln_dict[vuln_id] = vuln_obj

        topics: dict[str, dict] = {}
        vuln_bucket = txs.bucket(b"vulnerability")
        for vuln_id, vuln_content in vuln_dict.items():
            # Generate a tooic uuid from Vuln ID
            random.seed(vuln_id)
            topic_id = str(uuid.UUID(int=random.getrandbits(128), version=4))

            bucket_content = vuln_bucket.get(vuln_id.encode())
            if bucket_content:
                vuln_details = json.loads(bucket_content.decode())
                if "Title" in vuln_details:
                    title = vuln_details["Title"]
                else:
                    title = vuln_id
                if "Description" in vuln_details:
                    abstract = vuln_details["Description"]
                elif "References" in vuln_details:
                    abstract = "\n".join(vuln_details["References"])
                else:
                    abstract = "There is no description."
                severity = vuln_details["Severity"]

                if (
                    "CVSS" in vuln_details
                    and "nvd" in vuln_details["CVSS"]
                    and "V3Score" in vuln_details["CVSS"]["nvd"]
                ):
                    cvss_v3_score = float(vuln_details["CVSS"]["nvd"]["V3Score"])
                else:
                    cvss_v3_score = None

            else:
                title = vuln_id
                abstract = "This Vuln is not yet published."
                severity = "UNKNOWN"
                cvss_v3_score = None
            if vuln_content["tags"]:
                tags = list(vuln_content["tags"])
            misp_tags = [vuln_id]
            assert isinstance(vuln_content["actions"], dict)
            actions = [
                {
                    **x,
                    "action": x["action"][:1024],
                    "ext": {
                        "tags": list(x["ext"]["tags"]),
                        "vulnerable_versions": {
                            k: list(v) for k, v in x["ext"]["vulnerable_versions"].items()
                        },
                    },
                    "action_id": _gen_action_id(topic_id, x["ext"]["tags"], x["action"]),
                }
                for x in vuln_content["actions"].values()
            ]

            convert_impact = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 3, "UNKNOWN": 4}
            topics[topic_id] = {
                "title": title,
                "abstract": abstract,
                "threat_impact": convert_impact.get(severity, 4),
                "tags": tags,
                "misp_tags": misp_tags,
                "actions": actions,
                "cvss_v3_score": cvss_v3_score,
            }

    tc_client = ThreatconnectomeClient(
        args.url,
        refresh_token,
        retry_max=3,
        connect_timeout=60.0,
        read_timeout=60.0,
    )
    data = tc_client.get_topics()
    if len(data) > 0 and not args.update:
        sample_topic = tc_client.get_topic(data[0]["topic_id"])
        if calculate_topic_content_fingerprint(sample_topic) != sample_topic["content_fingerprint"]:
            raise ValueError(
                "Calculated content_fingerprint does not matche. Check the calculation algorithm."
            )
    existing_topics = {result["topic_id"]: result for result in data}

    for topic_id, topic in topics.items():
        if topic_id not in existing_topics:  # new topic
            tc_client.create_topic(topic_id, topic)
            continue

        # existing topic
        if args.update:  # force update mode
            tc_client.update_topic_and_actions(topic_id, topic)
            continue

        content_fingerprint = calculate_topic_content_fingerprint(topic)
        if (
            content_fingerprint != existing_topics[topic_id]["content_fingerprint"]
        ):  # topic core updated
            tc_client.update_topic_and_actions(topic_id, topic)
            continue

        # TODO: care for the cases only actions are updated.


if __name__ == "__main__":
    main()
