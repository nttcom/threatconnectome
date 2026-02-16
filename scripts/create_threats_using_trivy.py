import argparse
import http.client as http_client
import json
import os
import random
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from functools import partial
from pprint import pprint
from time import sleep
from typing import Callable, Generator
from uuid import UUID, uuid4

import requests
from packageurl import PackageURL
from sqlalchemy import ForeignKey, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, sessionmaker
from typing_extensions import Annotated

http_client.HTTPConnection.debuglevel = 0  # set 1 for detailed debug (http)
DB_DEBUG_ECHO = False  # set True for detailed debug (database)
TRIVY_DEBUG = False  # set True for detailed debug (trivy)

TRIVY_COMMAND = "trivy"  # require >= 0.50.0

ENV_KEY_REFRESH_TOKEN = "THREATCONNECTOME_REFRESH_TOKEN"
ENV_KEY_DATABASE_URL = "THREATCONNECTOME_DATABASE_URL"

ARGUMENTS: list[tuple[str, dict]] = []
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
        "-d",
        "--database",
        {
            "required": False,
            "default": os.environ.get(ENV_KEY_DATABASE_URL),
            "help": "URL to access database server."
            + f" default is environment variable: {ENV_KEY_DATABASE_URL}. "
            + "e.g) 'postgresql+psycopg2://USERNAME:PASSWORD@HOSTNAME:PORT/DBNAME'",
        },
    ),
]

StrUUID = Annotated[str, 36]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str: Text,
            StrUUID: String(36),
        }
    )


class Tag(Base):
    __tablename__ = "tag"
    tag_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_name: Mapped[str]
    parent_id: Mapped[StrUUID | None]
    parent_name: Mapped[str | None]


class Dependency(Base):
    __tablename__ = "dependency"
    service_id: Mapped[StrUUID] = mapped_column(primary_key=True)
    tag_id: Mapped[StrUUID] = mapped_column(ForeignKey("tag.tag_id"), primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    target: Mapped[str] = mapped_column(primary_key=True)


@contextmanager
def readonly_database(db_url: str) -> Generator:
    # generate read-only database session.
    # Note: `session.commit()` will cause Exception
    engine = create_engine(db_url, echo=DB_DEBUG_ECHO).execution_options(postgresql_readonly=True)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()


def create_fake_sbom(purls: list[PackageURL], purl_names: dict[PackageURL, str]) -> dict:
    sbom = {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.jaon",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": str(datetime.now()),
            "tools": [{"vendor": "aquasecurity", "name": "trivy", "version": "0.48.3"}],  # XXX
            "component": {
                "bom-ref": str(uuid4()),
                "type": "application",
                "name": "fake application to detect vulnerabilities",
                "properties": [{"name": "aquasecurity:trivy:SchemaVersion", "value": "2"}],
            },
        },
        "components": [
            {
                "bom-ref": str(purl),
                "type": "library",  # XXX
                "name": pkg_name,
                "purl": str(purl),
            }
            for purl in purls
            if (pkg_name := purl_names[purl])
        ],
        "dependencies": [],
    }
    return sbom


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

    def create_threat(
        self,
        topic_id: UUID | str,
        service_id: UUID | str,
        tag_id: UUID | str,
    ) -> dict:
        request = {
            "topic_id": str(topic_id),
            "service_id": str(service_id),
            "tag_id": str(tag_id),
        }
        url = f"{self.api_url}/threats"
        response = self.retry_call(requests.post, url, json=request)
        return response.json()


def main(args: argparse.Namespace) -> None:

    # connect to database and fetch all Dependencies with Tags
    with readonly_database(args.database) as db:
        rows = db.execute(select(Dependency, Tag).join(Tag)).all()

    # create dict to map purl to dependencies
    purl_to_dependency: dict[PackageURL, set[tuple[str, str]]] = {}  # purl: (service_id, tag_id)
    # Tag.tag_name can be the name given by trivy -- maybe better hint than purl. keep them
    purl_to_name: dict[PackageURL, str] = {}  # purl: pkg_name
    for row in rows:
        [dependency, tag] = row
        if not tag.parent_name:  # not supported artifact
            continue
        [pkg_name, pkg_family, pkg_manager] = tag.tag_name.rsplit(":", 2)
        if pkg_name.startswith("alpine") and pkg_family.startswith("3."):  # HACK
            # drop wrong components which cause trivy fatal error
            continue
        purl = PackageURL.from_string(f"pkg:{pkg_family}/{pkg_name}@{dependency.version}")  # FIXME
        dependencies_set = purl_to_dependency.get(purl, set())
        dependencies_set.add((row.Dependency.service_id, row.Dependency.tag_id))
        purl_to_dependency[purl] = dependencies_set
        purl_to_name[purl] = pkg_name

    # create fake sbom file
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".sbom.json") as sbom_file:
        json.dump(create_fake_sbom(list(purl_to_dependency), purl_to_name), sbom_file)
        sbom_file.flush()

        # scan vulnerabilities using trivy
        with tempfile.TemporaryDirectory() as tmpdir:
            scan_result_filename = f"{tmpdir}/trivy_scanned_result.json"
            trivy_command = [
                TRIVY_COMMAND,
                "sbom",  # SBOM scan mode
                sbom_file.name,  # target sbom file name
                "--config",
                "-",  # do not load any config files
                "--format",
                "cyclonedx",  # output file format
                "--output",
                scan_result_filename,  # output file name
                "--scanners",
                "vuln",  # enable vulnerability scan
                "--debug" if TRIVY_DEBUG else "--quiet",
            ]

            # execute trivy!
            proc = subprocess.run(trivy_command)
            if proc.returncode != 0:
                raise ChildProcessError(f"subprocess failed: {trivy_command}")

            # load scan result
            with open(scan_result_filename, "r") as scan_result_file:
                scan_result = json.load(scan_result_file)

    # convert found vulnerabilities to threats
    threats: set[tuple[str, str, str]] = set()  # {(topic_id, service_id, tag_id)}
    for vulnerability in scan_result["vulnerabilities"]:
        cve_id = vulnerability["id"]
        # generate topic_id from cve_id -- see trivydb2tc.py
        random.seed(cve_id)
        topic_id = str(UUID(int=random.getrandbits(128), version=4))
        # CAUTION:
        #   we are not sure if the topic_ids above already exist or not!
        for affect in vulnerability.get("affects", []):
            purl = PackageURL.from_string(affect["ref"])
            if purl not in purl_to_dependency:  # something went wrong
                print(f"WARN: cannot detect dependency for purl: {purl}", file=sys.stderr)
                continue
            for [service_id, tag_id] in purl_to_dependency[purl]:
                threats.add((topic_id, service_id, tag_id))

    # connect to Threatconnectome and create threats
    tc_client = ThreatconnectomeClient(args.endpoint, args.refresh_token, retry_max=1)
    print("Start creating threats.")
    for [topic_id, service_id, tag_id] in threats:
        print("--")
        pprint({"topic_id": topic_id, "service_id": service_id, "tag_id": tag_id})
        try:
            created_threat = tc_client.create_threat(topic_id, service_id, tag_id)
            print("OK: created threat_id:", created_threat["threat_id"])
        except APIError as err:
            print(err)


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()
    for name, opts in ARGUMENTS:
        PARSER.add_argument(name, **opts)
    for sname, lname, opts in OPTIONS:
        PARSER.add_argument(sname, lname, **opts)
    ARGS = PARSER.parse_args()

    if not ARGS.database:
        raise ValueError(
            f"argument: -d/--database or environment variable: {ENV_KEY_DATABASE_URL}"
            + " is required"
        )
    if not ARGS.refresh_token:
        raise ValueError(
            f"argument: -r/--refresh-token or environment variable: {ENV_KEY_REFRESH_TOKEN}"
            + " is required"
        )

    main(ARGS)
