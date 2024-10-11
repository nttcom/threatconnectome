import re
from dataclasses import dataclass, field
from typing import (
    Any,
    NamedTuple,
    Pattern,
    TypeAlias,
)

from packageurl import PackageURL

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.debug_info_outputer import error_message
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import SBOMParser

SBOM: TypeAlias = dict


class TrivyCDXParser(SBOMParser):
    @dataclass
    class CDXComponent:
        class Target(NamedTuple):
            ref: str
            name: str

        bom_ref: str
        type: str
        group: str
        name: str
        version: str
        raw_purl: str | None
        properties: dict[str, Any]
        purl: PackageURL | None = field(init=False, repr=False)
        trivy_class: str | None = field(init=False, repr=False)
        targets: set[Target] = field(init=False, repr=False, default_factory=set)

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
            fix_rules: list[tuple[Pattern[str], str]] = [
                (re.compile(r"^(centos-[0-9]+)\..+$"), r"\1"),
                (re.compile(r"^(debian-[0-9]+)\..+$"), r"\1"),
            ]
            for src, dst in fix_rules:
                distro = re.sub(src, dst, distro)
            return distro

        @staticmethod
        def _find_pkg_mgr(
            components_map: dict[str, "TrivyCDXParser.CDXComponent"],
            refs: list[str],
        ) -> "TrivyCDXParser.CDXComponent | None":
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

        def to_tag(self, components_map: dict[str, Any]) -> str | None:
            if not self.purl:
                return None
            pkg_name = (
                self.group + "/" + self.name if self.group else self.name
            )  # given by trivy. may include namespace in some case.
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
    def parse_sbom(cls, sbom: SBOM, sbom_info: SBOMInfo) -> list[Artifact]:
        if (
            sbom_info.spec_name != "CycloneDX"
            or sbom_info.spec_version not in {"1.5", "1.6"}
            or sbom_info.tool_name != "trivy"
        ):
            raise ValueError(f"Not supported: {sbom_info}")
        actual_parse_func = {
            "1.5": cls.parse_func_1_5,
            "1.6": cls.parse_func_1_5,
        }.get(sbom_info.spec_version)
        if not actual_parse_func:
            raise ValueError("Internal error: actual_parse_func not found")
        return actual_parse_func(sbom)

    @classmethod
    def parse_func_1_5(cls, sbom: SBOM) -> list[Artifact]:
        meta_component = sbom.get("metadata", {}).get("component")
        raw_components = sbom.get("components", [])

        # parse components
        components_map: dict[str, TrivyCDXParser.CDXComponent] = {}
        for data in [meta_component, *raw_components]:
            if not data:
                continue
            try:
                components_map[data["bom-ref"]] = TrivyCDXParser.CDXComponent(
                    bom_ref=data.get("bom-ref"),
                    type=data.get("type"),
                    group=data.get("group"),
                    name=data.get("name"),
                    version=data.get("version"),
                    raw_purl=data.get("purl"),
                    properties={x["name"]: x["value"] for x in data.get("properties", [])},
                )
            except ValueError as err:
                error_message(err)
                error_message("Dopped component:", data)

        # parse dependencies
        dependencies: dict[str, set[str]] = {}
        for dep in sbom.get("dependencies", []):
            if not (from_ := dep.get("ref")):
                continue
            if to_ := dep.get("dependsOn"):
                dependencies[from_] = set(to_)

        def _recursive_get(ref_: str, current_: set[str]) -> set[str]:  # returns new refs only
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
        artifacts_map: dict[str, Artifact] = {}  # {tag: artifact}
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
