import argparse
import json
import sys
from typing import Set

REP_DELIMITER = "__>>__"
SUPPORTED_TOOLS = {"GitHub.com-Dependency-Graph"}
ARGUMENTS: list[tuple[str, dict]] = []  # arg_name, options
OPTIONS: list[tuple[str, str, dict]] = [  # short_name, long_name, options
    (
        "-i",
        "--infile",
        {
            "required": False,
            "type": argparse.FileType("r"),
            "default": sys.stdin,
            "help": "(Default: stdin)",
        },
    ),
    (
        "-o",
        "--outfile",
        {
            "required": False,
            "type": argparse.FileType("w"),
            "default": sys.stdout,
            "help": "(Default: stdout)",
        },
    ),
    (
        "-t",
        "--tool",
        {
            "required": False,
            "help": f"one of {SUPPORTED_TOOLS}. (Default: auto-detect)",
        },
    ),
]


def system_message(*args, **kwargs):
    print(*args, **{k: v for k, v in kwargs if k != "file"}, file=sys.stderr)


class GitHubSPDXParser:
    json_data: dict

    def __init__(self, json_data: dict):
        self.json_data = json_data
        try:
            if (spdxVer := self.json_data["spdxVersion"]) == "SPDX-2.3":
                system_message(f"Detected SPDX Version: {spdxVer} (ok)")
            else:
                system_message(f"Warn: Detected not supported SPDX Version: {spdxVer}")
        except (KeyError, TypeError, IndexError):
            system_message("Warn: Cannot detect SPDX Version")

    def list_tags(self) -> list[dict]:
        tag_versions: dict[str, Set[str]] = {}  # [tag: {versions,...}]
        for pkg in self.json_data.get("packages", []):
            try:
                if not (external_refs := pkg.get("externalRefs")):
                    continue  # ignore not having externalRefs
                pkg_managers = [
                    ex_ref
                    for ex_ref in external_refs
                    if ex_ref.get("referenceCategory") == "PACKAGE-MANAGER"
                ]
                if not pkg_managers:
                    continue  # do not trust if missing package-manager

                pkg_name = pkg["name"].split(":", 1)[1]
                pkg_version = pkg["versionInfo"]
                if len(pkg_managers) > 1:
                    system_message(f"Warn: Ambiguous package managers for {pkg_name}")
                pkg_info = pkg_managers[0]["referenceLocator"].split(":", 1)[1].split("/", 1)[0]
                tag: str = f"{pkg_name}:{pkg_info}:"
                versions_set: Set[str] = tag_versions.get(tag, set())
                versions_set.add(pkg_version)
                tag_versions[tag] = versions_set
            except (KeyError, TypeError, IndexError):
                pass  # just ignore not expected contents

        return sorted(
            [
                {
                    "tag_name": tag,
                    "references": [
                        {
                            "version": version,
                            "target": "-",
                        }
                        for version in sorted(versions)
                    ],
                }
                for tag, versions in tag_versions.items()
            ],
            key=lambda x: x["tag_name"],
        )


def main(args: argparse.Namespace) -> None:
    if args.infile == sys.stdin:
        system_message("reading data from STDIN...")
    json_data = json.load(args.infile)
    if not args.tool:
        try:
            for creator_entry in json_data["creationInfo"]["creators"]:
                key, value = [x.strip() for x in creator_entry.split(":", 1)]
                if key.lower() == "tool" and value in SUPPORTED_TOOLS:
                    args.tool = value
                    system_message(f"Auto detected tool: {args.tool}")
                    break
        except (KeyError, TypeError, IndexError):
            system_message("Error: Auto detecting tool failed. Specify tool by -t option.")
            sys.exit(255)
    elif args.tool not in SUPPORTED_TOOLS:
        system_message(f"Error: Not a supported tool: {args.tool}")
        sys.exit(255)

    spdx_parser = GitHubSPDXParser(json_data)
    for tag_line in spdx_parser.list_tags():
        args.outfile.write(json.dumps(tag_line) + "\n")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    for short_name, long_name, options in OPTIONS:
        PARSER.add_argument(short_name, long_name, **options)
    for arg_name, options in ARGUMENTS:
        PARSER.add_argument(arg_name, **options)
    ARGS = PARSER.parse_args()
    main(ARGS)
