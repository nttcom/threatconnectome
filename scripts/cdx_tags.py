import argparse
import json
import os
import re
import sys
from typing import Any, ClassVar, Dict, List, Pattern, Set, Tuple

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
from packageurl import PackageURL

REP_DELIMITER = "__>>__"
SUPPORTED_TOOLS = ["syft", "trivy"]


ARGUMENTS: List[Tuple[str, dict]] = []

OPTIONS: List[Tuple[str, str, dict]] = [
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
    (
        "-r",
        "--replace_rules",
        {
            "nargs": "*",
            "help": (
                "{TargetRegex}"
                + REP_DELIMITER
                + "{ReplacedString}"
                + '  ex) -r "home/[^/]*/'
                + REP_DELIMITER
                + 'ANONYMOUS:"'
            ),
        },
    ),
    (
        "-s",
        "--skip_rules",
        {
            "nargs": "*",
            "help": (
                "skip targets starting with one of rules. "
                + '-r options applied beforehand.  ex) -s "home/.*/secret/"'
            ),
        },
    ),
    (
        "-H",
        "--hostname",
        {
            "required": False,
            "help": "used as target of os-pkgs. (Default: auto-detect (only for trivy))",
        },
    ),
]


def _pick_prop(props_: List[Dict[str, Any]], name_: str) -> str:
    return (next(filter(lambda x: x.get("name") == name_, props_), None) or {}).get("value") or ""


class CDXComponents:
    replace_rules: List[Tuple[Pattern, str]] = []
    skip_rules: List[Pattern] = []
    components: Dict[str, Set[Tuple[str, str]]]  # {tag: {(version, target)}}

    def __init__(self, args: argparse.Namespace, jdata: dict):
        self.components = {}
        for rep_rule in args.replace_rules or []:
            try:
                rep_regex, replaced = rep_rule.rsplit(REP_DELIMITER, 1)
                self.replace_rules.append((re.compile(rep_regex), replaced))
            except re.error as rerror:
                print(f"Error: Invalid -r option: {rep_rule}: {rerror}", file=sys.stderr)
                sys.exit(1)
            except ValueError:
                print(f"Error: Invalid -r option: {rep_rule}", file=sys.stderr)
                sys.exit(1)
        for skip_rule in args.skip_rules or []:
            try:
                self.skip_rules.append(re.compile(skip_rule))
            except re.error as rerror:
                print(f"Error: Invalid -s option: {skip_rule}: {rerror}", file=sys.stderr)
                sys.exit(1)
            except ValueError:
                print(f"Error: Invalid -s option: {skip_rule}", file=sys.stderr)
                sys.exit(2)

    def list_tags(self) -> List[dict]:
        return sorted(
            [
                {
                    "tag_name": tag,
                    "references": sorted(
                        [
                            {
                                "version": version,
                                "target": target,
                            }
                            for (version, target) in refs
                        ],
                        key=lambda x: (x["version"], x["target"]),  # type: ignore[index]
                    ),
                }
                for (tag, refs) in self.components.items()
            ],
            key=lambda x: x["tag_name"],
        )


class TrivyCDXComponents(CDXComponents):
    class TrivyCDXComponent:
        bom_ref: str
        raw_type: str  # library, application, or operating-system
        name: str  # pkgname, lockfile path (etc), or os family
        version: str
        purl: PackageURL | None
        mgr_class: str  # lang-pkgs or os-pkgs: only managers know
        mgr_type: str  # detailed mgr name, such as pipenv, poetry...

        @staticmethod
        def _gen_os_name(jdata: dict, hostname: str) -> str:
            # Note:
            #   this method is called for operating-system component, and return value is
            #   used as target name of os-pkgs. thus set the original name and version.
            name_ = jdata.get("name") or ""
            version_ = jdata.get("version") or ""
            distro_ = name_ if not version_ else f"{name_}-{version_}"
            return f"{hostname}({distro_})"

        def __init__(self, jdata, hostname):
            _class_key = "aquasecurity:trivy:Class"
            _mgr_type_key = "aquasecurity:trivy:Type"

            # CAUTION:
            #   Do NOT rely on aquasecurity:trivy:PkgType in component which type is "library".
            #   Each component has only one PkgType, even if referenced from multiple applications.

            self.bom_ref = jdata.get("bom-ref") or ""
            self.raw_type = jdata.get("type") or ""
            self.name = (
                (jdata.get("name") or "")
                if self.raw_type != "operating-system"
                else self._gen_os_name(jdata, hostname)
            )
            self.version = jdata.get("version") or ""
            self.purl = None if not (_purl := jdata.get("purl")) else PackageURL.from_string(_purl)

            props = jdata.get("properties") or []
            self.mgr_class = _pick_prop(props, _class_key)
            self.mgr_type = _pick_prop(props, _mgr_type_key)

    @staticmethod
    def _fix_distro(distro: str) -> str:
        # Note:
        #   syft sees /etc/os-release, but trivy sees /etc/redhat-release.
        #   if the contents differ, it causes distro mismatch.
        #   we fix the mismatch here as far as we found out.
        fix_rules: List[Tuple[Pattern[str], str]] = [
            (re.compile(r"^(centos-[0-9]+)\..+$"), r"\1"),
            (re.compile(r"^(debian-[0-9]+)\..+$"), r"\1"),
        ]
        for src, dst in fix_rules:
            distro = re.sub(src, dst, distro)
        return distro

    def __init__(self, args: argparse.Namespace, jdata: dict):
        super().__init__(args, jdata)
        if not args.hostname:
            try:
                args.hostname = jdata["metadata"]["component"]["name"]
                print(f"Auto detected hostname: {args.hostname}", file=sys.stderr)
            except KeyError:
                print(
                    "Error: Auto detect hostname failed. use -H option to specify.", file=sys.stderr
                )
                args.hostname = ""

        mgr2pkgs: Dict[str, Set[str]] = {}
        mgr_components: Dict[str, TrivyCDXComponents.TrivyCDXComponent] = {}
        pkg_components: Dict[str, TrivyCDXComponents.TrivyCDXComponent] = {}
        for dep in jdata.get("dependencies", []):
            if not dep.get("ref") or not dep.get("dependsOn"):
                continue
            mgr2pkgs[dep["ref"]] = set(dep["dependsOn"])
        for component_data in jdata.get("components") or []:
            assert component_data.get("name")
            if component_data.get("type") == "application":
                # apply -r & -s options only to referenced applications: name is lockfile path.
                for src, dst in self.replace_rules:
                    component_data["name"] = re.sub(src, dst, component_data["name"])
                if any(skip_rule.match(component_data["name"]) for skip_rule in self.skip_rules):
                    del mgr2pkgs[component_data["bom-ref"]]
                    continue
            component = TrivyCDXComponents.TrivyCDXComponent(component_data, args.hostname)
            if not component.purl and component.raw_type == "library":
                print(f"Warning: cannot get purl: {component.name}", file=sys.stderr)
            collection = (
                pkg_components
                if component.raw_type == "library"
                else (
                    mgr_components
                    if component.raw_type in {"application", "operating-system"}
                    else None
                )
            )
            if collection is None:
                print(
                    f"Warning: unknown type of component: {component.raw_type}({component.name})",
                    file=sys.stderr,
                )
                continue
            assert component.bom_ref not in collection
            collection[component.bom_ref] = component

        for mgr_ref in mgr2pkgs:
            if not (mgr := mgr_components.get(mgr_ref)):
                continue
            if not (target := mgr.name):
                continue
            pkg_mgr = "" if mgr.mgr_class == "os-pkgs" else mgr.mgr_type
            for pkg_ref in mgr2pkgs.get(mgr.bom_ref, []):
                if not (pkg := pkg_components.get(pkg_ref)):
                    continue
                assert pkg.purl
                pkg_info = (
                    pkg.purl.type
                    if mgr.mgr_class == "lang-pkgs"
                    else (
                        self._fix_distro(pkg.purl.qualifiers.get("distro") or "")
                        if mgr.mgr_class == "os-pkgs"
                        else ""
                    )
                )

                tag = f"{pkg.name}:{pkg_info}:{pkg_mgr}"

                self.components[tag] = self.components.get(tag, set()) | {(pkg.version, target)}


class SyftCDXComponents(CDXComponents):
    # https://github.com/anchore/syft/blob/main/syft/pkg/type.go
    supported_pkg_types: ClassVar[List[str]] = [
        # 'UnknownPackage',
        "alpm",
        "apk",
        # 'binary',
        "pod",
        "conan",
        "dart-pub",
        "deb",
        "dotnet",
        "gem",
        "go-module",
        # 'graalvm-native-image',
        "hackage",
        "hex",
        "java-archive",
        # 'jenkins-plugin',
        "msrc-kb",
        "npm",
        "php-composer",
        "portage",
        "python",
        "rpm",
        "rust-crate",
    ]
    os_pkg_types: ClassVar[List[str]] = [
        "alpm",
        "apk",
        "deb",
        "msrc-kb",
        "portage",
    ]

    # https://github.com/anchore/syft/blob/main/syft/pkg/cataloger/ * /cataloger.go
    # Note:
    #   pkg_mgr is not defined in syft. use the same value in trivy (if exists).
    location_to_pkg_mgr: ClassVar[List[Tuple[str, Pattern[str]]]] = [
        ("conan", re.compile(r"conanfile\.txt$")),  # cpp
        ("conan", re.compile(r"conan\.lock$")),  # cpp
        ("pub", re.compile(r"pubspec\.lock$")),  # dart
        ("dotnet", re.compile(r".+\.deps\.json$")),  # dotnet
        ("mix", re.compile(r"mix\.lock$")),  # elixir: is this correct??
        ("rebar", re.compile(r"rebar\.lock$")),  # erlang: is this correct??
        ("gomod", re.compile(r"go\.mod$")),  # golang
        ("hackage", re.compile(r"stack\.yaml$")),  # haskell
        ("hackage", re.compile(r"stack\.yaml\.lock$")),  # haskell
        ("hackage", re.compile(r"cabal\.project\.freeze$")),  # haskell
        ("pom", re.compile(r"pom\.xml$")),  # java
        ("npm", re.compile(r"package-lock\.json$")),  # javascript
        ("yarn", re.compile(r"yarn\.lock$")),  # javascript
        ("pnpm", re.compile(r"pnpm-lock\.yaml$")),  # javascript
        ("composer", re.compile(r"installed\.json$")),  # php
        ("composer", re.compile(r"composer\.lock$")),  # php
        ("pip", re.compile(r".*requirements.*\.txt$")),  # python
        ("pip", re.compile(r"setup\.py$")),  # python
        ("poetry", re.compile(r"poetry\.lock$")),  # python
        ("pipenv", re.compile(r"Pipfile\.lock$")),  # python
        ("rpm", re.compile(r".+\.rpm$")),  # rpm
        ("gem", re.compile(r"Gemfile\.lock$")),  # ruby
        ("gemspec", re.compile(r".+\.gemspec$")),  # ruby
        ("cargo", re.compile(r"Cargo\.lock$")),  # rust
        ("pod", re.compile(r"Podfile\.lock$")),  # swift
    ]

    @classmethod
    def _resolve_pkg_mgr(cls, locations: List[str]) -> str:
        if not locations or not locations[0]:
            return ""
        tgt = os.path.basename(locations[0])
        for pkg_mgr, rule in cls.location_to_pkg_mgr:
            if rule.match(tgt):
                return pkg_mgr
        return ""

    @classmethod
    def _replace_all(cls, target: str) -> str:
        for src, dst in cls.replace_rules:
            target = re.sub(src, dst, target)
        return target

    @staticmethod
    def _pick_locations(props_: List[Dict[str, str]]) -> List[str]:
        loc_regex = re.compile("^syft:location:[0-9]+:path$")
        return [prop_["value"] for prop_ in props_ if loc_regex.match(prop_["name"])]

    def __init__(self, args: argparse.Namespace, jdata: dict):
        _pkg_type_key = "syft:package:type"
        super().__init__(args, jdata)
        if not args.hostname:
            print("Warning: no hostname specified.", file=sys.stderr)
            args.hostname = ""

        for component_data in jdata.get("components") or []:
            props = component_data.get("properties") or []
            pkg_type = _pick_prop(props, _pkg_type_key)
            if not (component_data.get("purl") and props and pkg_type in self.supported_pkg_types):
                continue
            purl = PackageURL.from_string(component_data["purl"])
            version = component_data.get("version") or ""
            if pkg_type in self.os_pkg_types:
                distro = purl.qualifiers.get("distro") or ""
                pkg_info = distro
                pkg_mgr = ""
                targets = [f"{args.hostname}({distro})"]
            else:
                pkg_info = purl.type or ""
                targets = list(
                    filter(
                        lambda x: len(x) > 0
                        and not any(skip_rule.match(x) for skip_rule in self.skip_rules),
                        {self._replace_all(target) for target in self._pick_locations(props)},
                    )
                )
                if len(targets) == 0:
                    continue  # skipped all targets
                if not (pkg_mgr := self._resolve_pkg_mgr(targets)):
                    # maybe not supported pkg_mgr by this script. skip this.
                    continue

            tag = f'{component_data["name"]}:{pkg_info}:{pkg_mgr}'

            self.components[tag] = (self.components.get(tag, set())) | {
                (version, target) for target in targets if targets
            }


def main(args: argparse.Namespace) -> None:
    if args.infile == sys.stdin:
        print("reading data from STDIN...", file=sys.stderr)

    jtext = args.infile.read()
    my_json_validator = JsonStrictValidator(SchemaVersion.V1_5)
    try:
        # Check CycloneDX v1.5 format
        validation_errors = my_json_validator.validate_str(jtext)
        if validation_errors:
            print(
                "Error: CycloneDX v1.5 JSON invalid: ",
                repr(validation_errors),
                file=sys.stderr,
            )
            sys.exit(1)
    # 'json-validation' is not installed
    except MissingOptionalDependencyException:
        print(
            "Error: Missing 'json-validation' extras.",
            'Run `pip install "cyclonedx-python-lib[json-validation]"`',
            file=sys.stderr,
        )
        sys.exit(2)

    jdata = json.loads(jtext)

    if args.tool is None:
        try:
            args.tool = jdata["metadata"]["tools"][0]["name"]
            print(f"Auto detected tool: {args.tool}", file=sys.stderr)
        except (KeyError, TypeError, IndexError):
            print(
                "Error: Auto detecting tool failed. Specify tool by -t option",
                file=sys.stderr,
            )
            sys.exit(255)
    if args.tool not in SUPPORTED_TOOLS:
        print(f"Error: Not a supported tool: {args.tool}", file=sys.stderr)
        sys.exit(255)

    components: CDXComponents = (
        TrivyCDXComponents(args, jdata) if args.tool == "trivy" else SyftCDXComponents(args, jdata)
    )

    for item in components.list_tags():
        args.outfile.write(json.dumps(item) + "\n")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    for sname, lname, opts in OPTIONS:
        PARSER.add_argument(sname, lname, **opts)
    for name, opts in ARGUMENTS:
        PARSER.add_argument(name, **opts)
    ARGS = PARSER.parse_args()
    main(ARGS)
