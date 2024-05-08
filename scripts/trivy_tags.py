"""This is a script for tag generation from trivy results."""

import argparse
import json
import re
import sys
from typing import Any

lang_package_managers = {
    # packager manager: package location
    "jar": "maven",
    "pom": "maven",
    "gradle": "maven",
    "bundler": "gem",
    "gemspec": "gem",
    "nuget": "nuget",
    "dotnet-core": "nuget",
    "conda-pkg": "conda",
    "python-pkg": "pypi",
    "pip": "pypi",
    "pipenv": "pypi",
    "poetry": "pypi",
    "gobinary": "golang",
    "gomod": "golang",
    "npm": "npm",
    "node-pkg": "npm",
    "yarn": "npm",
    "pnpm": "npm",
    "cocoapods": "swift",
    "hex": "hex",
    "pub": "dart",
    "cargo": "cargo",
}

os_package_mangers = [
    "alpine",
    "debian",
    "ubuntu",
    "redhat",
    "centos",
    "rocky",
    "alma",
    "amazon",
    "fedora",
    "oracle",
    "opensuse",
    "opensuse.leap",
    "opensuse.tumbleweed",
    "suse linux enterprise server",
    "photon",
]

REP_DELIMITER = "__>>__"


def create_tag(metadata, tag_class, tag_type, tag_package_name):
    if tag_class == "os-pkgs":
        os_meta = metadata.get("OS")
        os_family = os_meta.get("Family")  # OS name
        os_name = os_meta.get("Name")  # OS version
        if os_name:
            if os_family == "centos":
                new_os_name = os_name.split(".")[0]
                return f"{tag_package_name}:{os_family}-{new_os_name}:"
            else:
                return f"{tag_package_name}:{os_family}-{os_name}:"
        # when there is no info on OS version
        return f"{tag_package_name}:{os_family}:"
    package_info = lang_package_managers[tag_type]
    # lang-pkgs format : {package name}:{default package location}:{package manager}
    return f"{tag_package_name}:{package_info}:{tag_type}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="trivyresult", help="read trivy result", type=argparse.FileType("r")
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
    args = parser.parse_args()
    trivy_result = args.trivyresult.read()
    args.trivyresult.close()
    json_contents = json.loads(trivy_result)
    metadata = json_contents.get("Metadata")
    results = json_contents.get("Results")

    replace_rules: list[tuple] = []
    for rep_rule in args.replace_rules or []:
        try:
            rep_regex, replaced = rep_rule.rsplit(REP_DELIMITER, 1)
        except ValueError:
            print(f"Invalid -r option: {rep_rule}", file=sys.stderr)
            sys.exit(1)
        replace_rules.append((re.compile(rep_regex), replaced))
    skip_rules = [re.compile(skip_regex) for skip_regex in args.skip_rules or []]

    tags = []
    tags_info: dict[str, dict[str, Any]] = {}
    for result in results:
        tag_target = result.get("Target")  # reference location
        for src, dst in replace_rules:
            tag_target = re.sub(src, dst, tag_target)
        if any(skip_rule.match(tag_target) for skip_rule in skip_rules):
            continue

        tag_type = result.get("Type")  # package manager
        if tag_type not in os_package_mangers and tag_type not in lang_package_managers:
            continue

        tag_class = result.get("Class")  # package category
        tag_packages = result.get("Packages")
        for package in tag_packages:
            tag_package_name = package.get("Name")
            tag_package_version = package.get("Version")
            new_tag = create_tag(metadata, tag_class, tag_type, tag_package_name)
            tags.append(new_tag)
            if new_tag not in tags_info:
                tags_info[new_tag] = {"references": []}
            tags_info[new_tag]["references"].append(
                {"target": tag_target, "version": tag_package_version}
            )

    tag_list = list(set(tags))  # remove duplicate tags
    for tag in tag_list:
        tag_dict = {"tag_name": tag, "references": tags_info[tag]["references"]}
        tag_str = json.dumps(tag_dict)
        args.tags.write(tag_str + "\n")  # output tags in jsonlines format
    args.tags.close()


if __name__ == "__main__":
    main()
