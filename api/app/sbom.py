import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    NamedTuple,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    TypeAlias,
)

from packageurl import PackageURL

SBOM: TypeAlias = dict


def error_message(*args, **kwargs):
    # print(*args, **{k: v for (k, v) in kwargs if k != "file"}, file=sys.stderr)
    pass


class SBOMInfo(NamedTuple):
    spec_name: str
    spec_version: str
    tool_name: str
    tool_version: Optional[str]


@dataclass
class Artifact:
    tag: str
    targets: Set[Tuple[str, str]] = field(init=False, repr=False, default_factory=set)
    versions: Set[str] = field(init=False, repr=False, default_factory=set)  # for missing targets

    def to_json(self) -> dict:
        targets = self.targets if self.targets else {("", version) for version in self.versions}
        return {
            "tag_name": self.tag,
            "references": sorted(
                [
                    {
                        "version": version,
                        "target": target,
                    }
                    for (target, version) in targets
                ],
                key=lambda x: (x["version"], x["target"]),
            ),
        }


class SBOMParser(ABC):
    @classmethod
    @abstractmethod
    def parse_sbom(cls, sbom: SBOM, sbom_info: SBOMInfo) -> List[Artifact]:
        raise NotImplementedError()


class TrivyCDXParser(SBOMParser):
    @dataclass
    class CDXComponent:
        class Target(NamedTuple):
            ref: str
            name: str

        bom_ref: str
        type: str
        name: str
        version: str
        raw_purl: Optional[str]
        properties: Dict[str, Any]
        purl: Optional[PackageURL] = field(init=False, repr=False)
        trivy_class: Optional[str] = field(init=False, repr=False)
        targets: Set[Target] = field(init=False, repr=False, default_factory=set)

        def __post_init__(self):
            if not self.bom_ref:
                raise ValueError("Warning: Missing bom-ref")
            if not self.name:
                raise ValueError("Warning: Missing name")
            self.purl = PackageURL.from_string(self.raw_purl) if self.raw_purl else None
            self.trivy_class = self.properties.get("aquasecurity:trivy:Class")

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

        @staticmethod
        def _find_pkg_mgr(
            components_map: Dict[str, "TrivyCDXParser.CDXComponent"],
            refs: List[str],
        ) -> Optional["TrivyCDXParser.CDXComponent"]:
            if not refs:
                return None
            if len(refs) == 1:
                return components_map.get(refs[0])
            for ref in refs:
                if not (mgr_candidate := components_map.get(ref)):
                    continue
                if mgr_candidate.trivy_class == "os-pkgs":
                    return mgr_candidate
                if mgr_candidate.properties.get("aquasecurity:trivy:Type"):
                    return mgr_candidate
            return components_map.get(refs[0])

        def to_tag(self, components_map: Dict[str, Any]) -> Optional[str]:
            if not self.purl:
                return None
            pkg_name = self.purl.name
            pkg_info = self.purl.type
            pkg_mgr = ""
            if self.targets:
                mgr = self._find_pkg_mgr(components_map, [t.ref for t in self.targets])
                if not mgr:
                    pass
                elif mgr.trivy_class == "os-pkgs":
                    distro = (
                        self.purl.qualifiers.get("distro")
                        if isinstance(self.purl.qualifiers, dict)
                        else ""
                    )
                    pkg_info = self._fix_distro(distro) if distro else ""
                else:
                    pkg_mgr = mgr.properties.get("aquasecurity:trivy:Type", "")
            return f"{pkg_name}:{pkg_info}:{pkg_mgr}"

    @classmethod
    def parse_sbom(cls, sbom: SBOM, sbom_info: SBOMInfo) -> List[Artifact]:
        if (
            sbom_info.spec_name != "CycloneDX"
            or sbom_info.spec_version not in {"1.5"}
            or sbom_info.tool_name != "trivy"
        ):
            raise ValueError(f"Not supported: {sbom_info}")
        actual_parse_func = {
            "1.5": cls.parse_func_1_5,
        }.get(sbom_info.spec_version)
        if not actual_parse_func:
            raise ValueError("Internal error: actual_parse_func not found")
        return actual_parse_func(sbom)

    @classmethod
    def parse_func_1_5(cls, sbom: SBOM) -> List[Artifact]:
        meta_component = sbom.get("metadata", {}).get("component")
        raw_components = sbom.get("components", [])

        # parse components
        components_map: Dict[str, TrivyCDXParser.CDXComponent] = {}
        for data in [meta_component, *raw_components]:
            if not data:
                continue
            try:
                components_map[data["bom-ref"]] = TrivyCDXParser.CDXComponent(
                    bom_ref=data.get("bom-ref"),
                    type=data.get("type"),
                    name=data.get("name"),
                    version=data.get("version"),
                    raw_purl=data.get("purl"),
                    properties={x["name"]: x["value"] for x in data.get("properties", [])},
                )
            except ValueError as err:
                error_message(err)
                error_message("Dopped component:", data)

        # parse dependencies
        dependencies: Dict[str, Set[str]] = {}
        for dep in sbom.get("dependencies", []):
            if not (from_ := dep.get("ref")):
                continue
            if to_ := dep.get("dependsOn"):
                dependencies[from_] = set(to_)

        def _recursive_get(ref_: str, current_: Set[str]) -> Set[str]:  # returns new refs only
            if ref_ in current_:
                return set()  # nothing to add
            if not (children_ := dependencies.get(ref_)):
                return {ref_}  # ref_ is the leaf
            ret_ = {ref_}
            for child_ in children_:
                if child_ in current_ | ret_:
                    continue  # already fixed
                ret_ |= _recursive_get(child_, ret_ | current_)
            return ret_

        # fill component.targets using dependencies
        for dep_ref in dependencies:
            if not (target_component := components_map.get(dep_ref)):
                raise ValueError(f"Missing dependency: {dep_ref}")
            if target_component.type in {"library"}:
                # https://cyclonedx.org/docs/1.5/json/#components_items_type
                continue  # omit pkg to pkg dependencies
            # FIXME: should omit scan root? e.g. contaner, rootfs, etc
            # if dep_ref == meta_component["bom-ref"]:
            #     continue  # omit scan root
            target_name = target_component.name or ""
            for pkg_ref in _recursive_get(dep_ref, set()):
                if pkg_ref == dep_ref:  # cross-reference
                    continue
                if not (pkg_component := components_map.get(pkg_ref)):
                    raise ValueError(f"Missing component: {pkg_ref}")
                pkg_component.targets |= {TrivyCDXParser.CDXComponent.Target(dep_ref, target_name)}

        # convert components to artifacts
        artifacts_map: Dict[str, Artifact] = {}  # {tag: artifact}
        for component in components_map.values():
            if not component.version:
                continue  # maybe directory or image
            if not (tag := component.to_tag(components_map)):
                continue  # omit not packages
            artifact = artifacts_map.get(tag, Artifact(tag=tag))
            artifacts_map[tag] = artifact
            for _target_ref, target_name in component.targets:
                new_target = (target_name, component.version)
                if new_target in artifact.targets:
                    error_message("conflicted target:", tag, new_target)
                else:
                    artifact.targets.add(new_target)
            artifact.versions.add(component.version)

        return list(artifacts_map.values())


class SyftCDXParser(SBOMParser):
    @dataclass
    class CDXComponent:
        class PkgMgrInfo(NamedTuple):
            name: str
            location_path: str

        bom_ref: str
        type: str
        name: str
        version: str
        raw_purl: Optional[str]
        properties: Dict[str, Any]
        purl: Optional[PackageURL] = field(init=False, repr=False)
        mgr_info: Optional[PkgMgrInfo] = field(init=False, repr=False)

        # https://github.com/anchore/syft/blob/main/syft/pkg/cataloger/ * /cataloger.go
        # Note: pkg_mgr is not defined in syft. use the same value in trivy (if exists).
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

        def __post_init__(self):
            if not self.bom_ref:
                raise ValueError("Warning: Missing bom-ref")
            if not self.name:
                raise ValueError("Warning: Missing name")
            self.purl = PackageURL.from_string(self.raw_purl) if self.raw_purl else None
            self.mgr_info = self._guess_mgr()

        def _guess_mgr(self) -> Optional[PkgMgrInfo]:
            # https://github.com/anchore/syft/blob/main/syft/pkg/package.go#L24
            # we do not know which is the best to guess pkg_mgr...
            if not (location_0_path := self.properties.get("syft:location:0:path")):
                return None
            idx = 0
            while True:
                key = f"syft:location:{idx}:path"
                if not (location_path := self.properties.get(key)):
                    # could not guess type, but no more locations.
                    # return the top of locations as a (hint of) target.
                    return self.PkgMgrInfo("", location_0_path)
                filename = os.path.basename(location_path)
                for mgr_name, pattern in self.location_to_pkg_mgr:
                    if pattern.match(filename):
                        return self.PkgMgrInfo(mgr_name, location_path)  # Eureka!
                idx += 1

        def to_tag(self) -> Optional[str]:
            if not self.purl:
                return None
            pkg_name = self.purl.name
            distro = (
                self.purl.qualifiers.get("distro")
                if self.purl and isinstance(self.purl.qualifiers, dict)
                else None
            )
            pkg_info = distro if distro else self.purl.type
            pkg_mgr = self.mgr_info.name if self.mgr_info else ""

            return f"{pkg_name}:{pkg_info}:{pkg_mgr}"

    @classmethod
    def parse_sbom(cls, sbom: SBOM, sbom_info: SBOMInfo) -> List[Artifact]:
        if (
            sbom_info.spec_name != "CycloneDX"
            or sbom_info.spec_version not in {"1.4", "1.5"}
            or sbom_info.tool_name != "syft"
        ):
            raise ValueError(f"Not supported: {sbom_info}")
        actual_parse_func = {
            "1.4": cls.parse_func_1_4,
            "1.5": cls.parse_func_1_4,
        }.get(sbom_info.spec_version)
        if not actual_parse_func:
            raise ValueError("Internal error: actual_parse_func not found")
        return actual_parse_func(sbom)

    @classmethod
    def parse_func_1_4(cls, sbom: SBOM) -> List[Artifact]:
        meta_component = sbom.get("metadata", {}).get("component")
        raw_components = sbom.get("components", [])

        # parse components
        components_map: Dict[str, SyftCDXParser.CDXComponent] = {}
        for data in [meta_component, *raw_components]:
            if not data:
                continue
            try:
                components_map[data["bom-ref"]] = SyftCDXParser.CDXComponent(
                    bom_ref=data.get("bom-ref"),
                    type=data.get("type"),
                    name=data.get("name"),
                    version=data.get("version"),
                    raw_purl=data.get("purl"),
                    properties={x["name"]: x["value"] for x in data.get("properties", [])},
                )
            except ValueError as err:
                error_message(err)
                error_message("Dropped component:", data)

        # convert components to artifacts
        artifacts_map: Dict[str, Artifact] = {}  # {tag: artifact}
        for component in components_map.values():
            if not component.version:
                continue  # maybe directory or image
            if not (tag := component.to_tag()):
                continue  # omit not packages
            artifact = artifacts_map.get(tag, Artifact(tag=tag))
            artifacts_map[tag] = artifact
            if component.mgr_info:
                new_target = (component.mgr_info.location_path, component.version)
                if new_target in artifact.targets:
                    error_message("conflicted target:", tag, new_target)
                artifact.targets |= {(component.mgr_info.location_path, component.version)}
            artifact.versions |= {component.version}

        return list(artifacts_map.values())


def inspect_cyclonedx(sbom: SBOM) -> Tuple[str, Optional[str]]:  # tool_name, tool_version
    def _get_tool0(jdata_: dict) -> dict:
        # https://cyclonedx.org/docs/1.5/json/#metadata_tools
        tools_ = jdata_["metadata"]["tools"]
        if isinstance(tools_, dict):
            if components_ := tools_.get("components"):  # CDX1.5
                return components_[0]
            if services_ := tools_.get("services"):  # CDX1.5
                return services_[0]
            raise ValueError("Not supported CycloneDX format")
        if isinstance(tools_, list):
            return tools_[0]  # CDX1.5 (legacy)
        raise ValueError("Not supported CycloneDX format")

    try:
        tool0 = _get_tool0(sbom)
        tool_name = tool0["name"]
        tool_version = tool0.get("version")
        return (tool_name, tool_version)
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported CycloneDX format")


def inspect_spdx(sbom: SBOM) -> Tuple[str, Optional[str]]:  # tool_name, tool_version
    raise ValueError("SPDX is not yet supported")


def inspect_sbom(sbom: SBOM) -> SBOMInfo:
    try:
        if sbom.get("bomFormat") == "CycloneDX":
            spec_name = "CycloneDX"
            spec_version = sbom["specVersion"]
            tool_name, tool_version = inspect_cyclonedx(sbom)
        elif sbom.get("SPDXID") == "SPDXRef-DOCUMENT":
            spec_name = "SPDX"
            spec_version = sbom["spdxVersion"]
            tool_name, tool_version = inspect_spdx(sbom)
        else:
            raise ValueError("Not supported file format")
        return SBOMInfo(spec_name, spec_version, tool_name, tool_version)
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported file format")


SBOM_PARSERS: Dict[Tuple[str, str], Type[SBOMParser]] = {
    # (spec_name, spec_version, tool_name) : SBOMParser
    ("CycloneDX", "trivy"): TrivyCDXParser,
    ("CycloneDX", "syft"): SyftCDXParser,
}


def sbom_json_to_artifact_json_lines(jdata: dict) -> List[dict]:
    sbom: SBOM = jdata
    sbom_info = inspect_sbom(sbom)
    sbom_parser = SBOM_PARSERS.get((sbom_info.spec_name, sbom_info.tool_name))
    if not sbom_parser:
        raise ValueError("Not supported file format")

    artifacts = sbom_parser.parse_sbom(sbom, sbom_info)
    return [artifact.to_json() for artifact in sorted(artifacts, key=lambda a: a.tag)]
