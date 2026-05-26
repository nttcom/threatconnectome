import os
import re
from typing import Pattern

from packageurl import PackageURL

LOCATION_TO_PKG_MGR: list[tuple[str, Pattern[str]]] = [
    ("conan", re.compile(r"conanfile\.txt$")),
    ("conan", re.compile(r"conan\.lock$")),
    ("pub", re.compile(r"pubspec\.lock$")),
    ("dotnet", re.compile(r".+\.deps\.json$")),
    ("mix", re.compile(r"mix\.lock$")),
    ("rebar", re.compile(r"rebar\.lock$")),
    ("gomod", re.compile(r"go\.mod$")),
    ("hackage", re.compile(r"stack\.yaml$")),
    ("hackage", re.compile(r"stack\.yaml\.lock$")),
    ("hackage", re.compile(r"cabal\.project\.freeze$")),
    ("pom", re.compile(r"pom\.xml$")),
    ("npm", re.compile(r"package-lock\.json$")),
    ("yarn", re.compile(r"yarn\.lock$")),
    ("pnpm", re.compile(r"pnpm-lock\.yaml$")),
    ("composer", re.compile(r"installed\.json$")),
    ("composer", re.compile(r"composer\.lock$")),
    ("pip", re.compile(r".*requirements.*\.txt$")),
    ("pip", re.compile(r"setup\.py$")),
    ("poetry", re.compile(r"poetry\.lock$")),
    ("pipenv", re.compile(r"Pipfile\.lock$")),
    ("rpm", re.compile(r".+\.rpm$")),
    ("gem", re.compile(r"Gemfile\.lock$")),
    ("gemspec", re.compile(r".+\.gemspec$")),
    ("cargo", re.compile(r"Cargo\.lock$")),
    ("pod", re.compile(r"Podfile\.lock$")),
]


def get_package_manager_from_path(path: str) -> tuple[str, str]:
    filename = os.path.basename(path)
    for mgr_name, pattern in LOCATION_TO_PKG_MGR:
        if pattern.match(filename):
            return (mgr_name.casefold(), path)
    return ("", path)


def get_source_name_from_rpm_filename(filename: str) -> str:
    """Extracts the source package name from an RPM filename."""
    suffix_removed_filename = filename.removesuffix(".rpm")

    architecture_index = suffix_removed_filename.rfind(".")
    if architecture_index == -1:
        raise ValueError("Unexpected name format: missing '.'")

    release_index = suffix_removed_filename[:architecture_index].rfind("-")
    if release_index == -1:
        raise ValueError("Unexpected name format: missing release delimiter '-'")

    version_index = suffix_removed_filename[:release_index].rfind("-")
    if version_index == -1:
        raise ValueError("Unexpected name format: missing version delimiter '-'")

    return suffix_removed_filename[:version_index]


def get_ecosystem_from_purl(purl: PackageURL) -> str:
    distro = purl.qualifiers.get("distro") if isinstance(purl.qualifiers, dict) else None
    if distro:
        if str(distro).casefold().startswith("wolfi-"):
            return "wolfi"
        return str(distro).casefold()
    return str(purl.type).casefold()
