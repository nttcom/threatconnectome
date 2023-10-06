"""This is a script for tag generation from osv-scanner results."""

import argparse
import json
import os
import re
import sys
from typing import List, Tuple

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

REP_DELIMITER = "__>>__"


def make_reference(source_path, pkg_version):
    target = source_path
    version = pkg_version
    return {"target": target, "version": version}


def get_pkg_manager(ref_target):
    lockfile_name = os.path.basename(ref_target)
    pkg_manager = package_files[lockfile_name]
    return pkg_manager


def get_pkg(pkg_contents):
    if "package" in pkg_contents:
        pkg = pkg_contents.get("package")
        version = pkg.get("version")
        name = pkg.get("name")
        info = pkg.get("ecosystem").lower()
        # use purl（package URL） style
        # ecosystem: rubygems -> gem
        if info == "rubygems":
            info = "gem"
    return version, name, info


def make_tag_name(source_path, pkg_name, pkg_info):
    if source_path:
        pkg_manager = get_pkg_manager(source_path)

    if pkg_manager and pkg_name and pkg_info:
        return f"{pkg_name}:{pkg_info}:{pkg_manager}"

    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="osvresult", help="read osv result", type=argparse.FileType("r"))
    parser.add_argument("-o", dest="tags", help="output tags", type=argparse.FileType("w"))
    parser.add_argument(
        "-r",
        dest="replace_rules",
        nargs="*",
        help=(
            "{SourceRegex}"
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
    osv_result = args.osvresult.read()
    args.osvresult.close()
    json_contents = json.loads(osv_result)
    results_list = json_contents.get("results")

    replace_rules: List[Tuple] = []
    for rep_rule in args.replace_rules or []:
        try:
            rep_regex, replaced = rep_rule.rsplit(REP_DELIMITER, 1)
        except ValueError:
            print(f"Invalid -r option: {rep_rule}", file=sys.stderr)
            sys.exit(1)
        replace_rules.append((re.compile(rep_regex), replaced))
    skip_rules = [re.compile(skip_regex) for skip_regex in args.skip_rules or []]

    tags = {}
    for result_contents in results_list:
        # result_contents = {'source': ..., 'packages': ...}
        if "source" in result_contents:
            source_path = result_contents.get("source").get("path")
            for src, dst in replace_rules:
                source_path = re.sub(src, dst, source_path)
            if any(skip_rule.match(source_path) for skip_rule in skip_rules):
                continue

        if "packages" in result_contents:
            for pkg_contents in result_contents.get("packages"):
                version, name, info = get_pkg(pkg_contents)
                ref = make_reference(source_path, version)
                tag = make_tag_name(source_path, name, info)
                # Add tag name/reference pairs
                if tag and ref:
                    # Assign references in array format
                    if tag not in tags:
                        tags[tag] = [ref]
                    # append tag and assign tag to reference
                    else:
                        tags[tag].append(ref)
    # convert tags_dict
    for tag, refs in tags.items():
        tag_dict = {"tag_name": tag, "references": refs}
        tag_str = json.dumps(tag_dict)
        args.tags.write(tag_str + "\n")  # output tags in jsonlines format
    args.tags.close()


if __name__ == "__main__":
    main()
