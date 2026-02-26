import argparse
import enum
import os
import sys
import uuid
from functools import partial
from time import sleep
from typing import Callable, TypedDict

import requests


class ProductCategoryEnum(str, enum.Enum):
    OS = "os"
    RUNTIME = "runtime"
    MIDDLEWARE = "middleware"
    PACKAGE = "package"


class ProductEoLInfo(TypedDict):
    release: str
    releaseDate: str
    eolFrom: str


class ThreatConnectomeEoLData(TypedDict):
    product_category: ProductCategoryEnum
    description: str
    is_ecosystem: bool


class EOLProductItem(TypedDict):
    product: str
    threatconnectome: ThreatConnectomeEoLData


eol_product_list: list[EOLProductItem] = [
    {
        "product": "alpine-linux",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.OS,
            "description": "Alpine Linux is a security-oriented, lightweight Linux distribution "
            "based on musl libc and busybox.",
            "is_ecosystem": True,
        },
    },
    {
        "product": "rocky-linux",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.OS,
            "description": "Rocky Linux is a Linux distribution intended to be a downstream, "
            "complete binary-compatible release using the Red Hat Enterprise Linux (RHEL) "
            "operating system source code. The project is led by Gregory Kurtzer, "
            "founder of the CentOS project.",
            "is_ecosystem": True,
        },
    },
    {
        "product": "ubuntu",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.OS,
            "description": "Ubuntu is a free and open-source Linux distribution based on Debian. "
            "Ubuntu is officially released in three editions: Desktop, Server, "
            "and Core (for IoT devices and robots).",
            "is_ecosystem": True,
        },
    },
    {
        "product": "django",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.PACKAGE,
            "description": "Django is a high-level Python Web framework that encourages rapid "
            "development and clean, pragmatic design.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "firefox",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.PACKAGE,
            "description": "Firefox, is a free and open-source web browser developed by the "
            "Mozilla. Firefox is available for Windows, macOS, Android, iOS, Linux, and ChromeOS.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "react",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.PACKAGE,
            "description": "React is an open-source JavaScript library for "
            "building modern web applications.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "numpy",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.PACKAGE,
            "description": "NumPy offers comprehensive mathematical functions, "
            "random number generators, linear algebra routines, Fourier transforms, and more.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "nodejs",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.RUNTIME,
            "description": "Node.js is an open-source, cross-platform JavaScript run-time "
            "environment built on Chrome’s V8 JavaScript engine that executes JavaScript "
            "code outside a browser.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "php",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.RUNTIME,
            "description": "PHP: Hypertext Preprocessor (or simply PHP) is a general-purpose "
            "programming language originally designed for web development.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "ruby",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.RUNTIME,
            "description": "Ruby is a dynamic, open-source programming language with a focus "
            "on simplicity and productivity. It has an elegant syntax that is natural to read "
            "and easy to write.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "python",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.RUNTIME,
            "description": "Python is an interpreted, high-level, "
            "general-purpose programming language.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "postgresql",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.MIDDLEWARE,
            "description": "PostgreSQL, also known as Postgres, is a free and open-source "
            "relational database management system (RDBMS) emphasizing extensibility "
            "and technical standards compliance.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "redis",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.MIDDLEWARE,
            "description": "Redis is an in-memory data structure store, used as a database, "
            "cache and message broker. It supports data structures such as strings, hashes, lists, "
            "sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes "
            "with radius queries and streams. Redis has built-in replication, Lua scripting, "
            "LRU eviction, transactions and different levels of on-disk persistence, "
            "and provides high availability via Redis Sentinel and automatic partitioning "
            "with Redis Cluster.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "sqlite",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.MIDDLEWARE,
            "description": "SQLite is an in-process library that implements a self-contained, "
            "serverless, zero-configuration, transactional SQL database engine. "
            "The code for SQLite is in the public domain and is thus free for use for any purpose, "
            "commercial or private.",
            "is_ecosystem": False,
        },
    },
    {
        "product": "ansible",
        "threatconnectome": {
            "product_category": ProductCategoryEnum.PACKAGE,
            "description": (
                "Ansible is an open-source software provisioning, configuration management and "
                "application-deployment tool enabling infrastructure as code. ansible extends "
                "the basic ansible-core with additional modules by delivering several "
                "collections in an easy-to-consume PyPI package. The ansible community "
                "package typically gets 2 major releases every year. A new minor version is "
                "released every 4 weeks. Maintenance fixes are guaranteed for only the latest "
                "major release.\nSee the Ansible Roadmap for upcoming release details."
            ),
            "is_ecosystem": False,
        },
    },
]


class EoLParamCreator:
    def __init__(
        self, product: str, eol_product_item: EOLProductItem, product_eol_info: list[ProductEoLInfo]
    ):
        self.product = product
        self.eol_product_item = eol_product_item
        self.product_eol_info = product_eol_info

    def get_eol_product_id(self) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, self.product))

    def create_eol_parameters(self) -> dict:
        eol_versions = []
        for eol_version_info in self.product_eol_info:
            eol_versions.append(
                {
                    "version": eol_version_info.get("release"),
                    "release_date": eol_version_info.get("releaseDate"),
                    "eol_from": eol_version_info.get("eolFrom"),
                }
            )

        return {
            "name": self.product,
            "product_category": self.eol_product_item["threatconnectome"]["product_category"],
            "description": self.eol_product_item["threatconnectome"]["description"],
            "is_ecosystem": self.eol_product_item["threatconnectome"]["is_ecosystem"],
            "eol_versions": eol_versions,
        }


class APIError(Exception):
    pass


def response_to_msg(resp: requests.Response) -> str:
    try:
        data = resp.json()
        return f"{resp.status_code}: {resp.reason}: {data.get('detail')}"
    except ValueError:
        return f"{resp.status_code}: {resp.reason}: {resp.text}"


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
                    raise APIError(f"ERROR: {response_to_msg(resp)}")
                _in_auth_retry = True
                self.headers = self._refresh_auth_token(self.headers)
                continue
            if resp.status_code < 500:
                # unrecoverable error: raise without retry
                raise APIError(f"ERROR: {response_to_msg(resp)}")
            # maybe recoverable error
            if _retry == 0:
                sys.exit(
                    "An unexpected error occurred\n"
                    + f"ERROR: Exceeded retry max: {response_to_msg(resp)}"
                )
            elif _retry > 0:
                _retry -= 1
            sleep(3)

    def get_eols(self) -> dict:
        response = self._retry_call(requests.get, f"{self.api_url}/eols")
        return response.json()

    def delete_eol(self, eol_product_id) -> None:
        self._retry_call(
            requests.delete,
            f"{self.api_url}/eols/{eol_product_id}",
            use_api_key=True,
        )

    def put_eol(self, eol_product_id, eol_parameters) -> None:
        self._retry_call(
            requests.put,
            f"{self.api_url}/eols/{eol_product_id}",
            json=eol_parameters,
            use_api_key=True,
        )


def get_product_eol_info_by_endoflife_date(product: str) -> list[ProductEoLInfo]:
    product_eol_info: list[ProductEoLInfo] = []

    response = requests.get(
        f"https://endoflife.date/api/v1/products/{product}",
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 404:
        sys.exit(f"Not support product. product: {product}")
    if response.status_code not in {200, 204}:
        sys.exit("An unexpected error occurred\n" + f"{response_to_msg(response)}")

    result = response.json().get("result")
    if result is None:
        return product_eol_info

    for release in result.get("releases", []):
        if release.get("eolFrom") is None:
            continue
        eol_data: ProductEoLInfo = {
            "release": release.get("name"),
            "releaseDate": release.get("releaseDate"),
            "eolFrom": release.get("eolFrom"),
        }
        product_eol_info.append(eol_data)

    return product_eol_info


def register_eol_info(tc_client: ThreatconnectomeClient) -> None:
    for eol_product_item in eol_product_list:
        product = eol_product_item.get("product", "")
        product_eol_info = get_product_eol_info_by_endoflife_date(product)
        if len(product_eol_info) == 0:
            continue

        eol_param_creator = EoLParamCreator(product, eol_product_item, product_eol_info)
        eol_product_id = eol_param_creator.get_eol_product_id()
        eol_parameters = eol_param_creator.create_eol_parameters()
        tc_client.put_eol(eol_product_id, eol_parameters)


def remove_unsupported_eol(tc_client: ThreatconnectomeClient) -> None:
    eols_in_db = tc_client.get_eols()
    for eol_product_in_db in eols_in_db.get("products", []):
        eol_product_name = eol_product_in_db.get("name")
        if not any(eol_product_name == item["product"] for item in eol_product_list):
            tc_client.delete_eol(eol_product_in_db.get("eol_product_id"))
            print(f"Deleted unsupported EoL. product: {eol_product_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", metavar="API_BASE_URL", type=str, help="API BASE URL of Threatconnectome"
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
        help="set the API key for patching EoL information in threatconnectome",
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
        connect_timeout=180.0,
        read_timeout=180.0,
    )

    remove_unsupported_eol(tc_client)
    register_eol_info(tc_client)


if __name__ == "__main__":
    main()
