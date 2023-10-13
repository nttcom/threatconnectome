"""This is a script for tag generation from syft results."""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

from packageurl import PackageURL

package_files = {
    # package file: package manager
    "packages.lock.json": "nuget",
    "packages.config": "nuget",
    "go.mod": "gomod",
    "go.sum": "gomod",
    "pom.xml": "pom",
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "pnpm-lock.yaml": "pnpm",
    "composer.lock": "composer",
    "requirements.txt": "pip",
    "Pipfile.lock": "pipenv",
    "poetry.lock": "poetry",
    "Gemfile.lock": "gemspec",
    "Cargo.lock": "cargo",
    "conan.lock": "conan",
    "Podfile.lock": "cocoapods",
    "pubspec.lock": "pub",
    "mix.lock": "mix",
}

# https://github.com/anchore/syft/blob/ac8f72fdd1b93e5ead343601bba1c06a9341d8ba/syft/pkg/type.go
os_package_mangers = [
    "deb",
    "alpm",
    "apk",
    "msrc-kb",
]

REP_DELIMITER = "__>>__"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="syftresult", help="read syft result", type=argparse.FileType("r")
    )
    parser.add_argument("-o", dest="tags", help="output tags", type=argparse.FileType("w"))
    parser.add_argument(
        "-r",
        dest="replace_rules",
        nargs="*",
        help=(
            "{TargetRegex}"
            + REP_DELIMITER
            + "{ReplacedString}"
            + '  ex) -r "home/[^/]*/'
            + REP_DELIMITER
            + 'ANONYMOUS:"'
        ),
    )
    parser.add_argument(
        "-s",
        dest="skip_rules",
        nargs="*",
        help=(
            "skip targets starting with one of rules. "
            '-r options applied beforehand.  ex) -s "home/.*/secret/"'
        ),
    )
    parser.add_argument("--hostname", dest="hostname", help="hostname for register os package info")
    args = parser.parse_args()
    syft_result = args.syftresult.read()
    args.syftresult.close()
    json_contents = json.loads(syft_result)

    replace_rules: List[Tuple] = []
    for rep_rule in args.replace_rules or []:
        try:
            rep_regex, replaced = rep_rule.rsplit(REP_DELIMITER, 1)
        except ValueError:
            print(f"Invalid -r option: {rep_rule}", file=sys.stderr)
            sys.exit(1)
        replace_rules.append((re.compile(rep_regex), replaced))
    skip_rules = [re.compile(skip_regex) for skip_regex in args.skip_rules or []]

    tags = []
    tags_info: Dict[str, Dict[str, Any]] = {}
    artifacts = json_contents.get("artifacts")
    for artifact in artifacts:
        locations = artifact.get("locations")
        target = locations[0].get("path")
        for src, dst in replace_rules:
            target = re.sub(src, dst, target)
        if any(skip_rule.match(target) for skip_rule in skip_rules):
            continue

        purlstr = artifact.get("purl")
        if not purlstr:
            continue
        purl = PackageURL.from_string(purlstr)
        package_location = purl.type or ""
        distro = purl.qualifiers.get("distro") or ""

        name = artifact.get("name")
        version = artifact.get("version")

        is_os_pkg = package_location in os_package_mangers

        if is_os_pkg:
            # os-pkgs format : {package name}:{OS name}-{OS version}:
            new_tag = f"{name}:{distro}:"
        else:
            filename = re.sub(r"\S*/", "", target)
            package_manager = package_files.get(filename) or ""
            # lang-pkgs format : {package name}:{default package location}:{package manager}
            new_tag = f"{name}:{package_location}:{package_manager}"

        tags.append(new_tag)
        if new_tag not in tags_info:
            tags_info[new_tag] = {"references": []}

        if is_os_pkg:
            hostname = args.hostname or ""
            os_target = f"{hostname}({distro})"
            tags_info[new_tag]["references"].append({"target": os_target, "version": version})
        else:
            tags_info[new_tag]["references"].append({"target": target, "version": version})

    tag_list = list(set(tags))  # remove duplicate tags
    for tag in tag_list:
        tag_dict = {"tag_name": tag, "references": tags_info[tag]["references"]}
        tag_str = json.dumps(tag_dict)
        args.tags.write(tag_str + "\n")  # output tags in jsonlines format
    args.tags.close()


if __name__ == "__main__":
    main()
