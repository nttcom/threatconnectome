import copy
import re
from dataclasses import dataclass, field
from typing import (
    Any,
    NamedTuple,
    Pattern,
)

from packageurl import PackageURL

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.debug_info_outputer import error_message
from app.sbom.parser.os_purl_utils import is_os_purl
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)

"""
We officially support only OS package types for Alpine Linux, Ubuntu, and Rocky Linux.
OS package types:
- Alpine Linux: alpine
- Chainguard: wolfi
- Minimos:
- Wolfi: wolfi
- Debian: debian
- Ubuntu: ubuntu
- Echo:
- Alma Linux: alma
- Amazon: amazon
- AzureLinux: azurelinux
- CentOS: centos
- Fedora: fedora
- Oracle: oracle
- RedHat: redhat
- Rocky: rocky
- openSUSE-leap: opensuse-leap
- openSUSE-tumbleweed: opensuse-tumbleweed
- SLEM: slem
- SLES: sles
- Bottlerocket: bottlerocket
- CBL-Mariner: cbl-mariner
- Photon: photon
"""
OS_PACKAGE_TYPES = [
    "alpine",
    "ubuntu",
    "rocky",
    "wolfi",
    "debian",
    "alma",
    "amazon",
    "azurelinux",
    "centos",
    "fedora",
    "oracle",
    "redhat",
    "opensuse-leap",
    "opensuse-tumbleweed",
    "slem",
    "sles",
    "bottlerocket",
    "cbl-mariner",
    "photon",
]

# OS types that combine pkg_type and distro when treated as ecosystem
# Example: "alpine" is formatted as "alpine+distro" instead of just "distro"
OS_PACKAGE_TYPES_USING_TYPE_AND_DISTRO_AS_ECOSYSTEM = ["alpine"]


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

        @staticmethod
        def _is_os_pkgtype(pkg_type: str | None) -> bool:
            """
            Determines whether a package type string represents an OS package.

            Args:
                pkg_type: Package type string to evaluate

            Returns:
                True if the package type is an OS package type, False otherwise

            Notes:
                - Returns True if pkg_type is in OS_PACKAGE_TYPES
                - Returns False if pkg_type is None
            """
            if not pkg_type:
                return False

            # Check if the package type matches any known OS package type
            return pkg_type in OS_PACKAGE_TYPES

        def to_package_info(
            self,
            merged_components_map: dict[str, Any],
        ) -> dict | None:
            if not self.purl:
                return None
            pkg_name = (
                self.group + "/" + self.name if self.group else self.name
            ).casefold()  # given by trivy. may include namespace in some case.

            source_name = None
            for key, value in self.properties.items():
                if "aquasecurity:trivy:SrcName" in key:
                    source_name = str(value).casefold()
                    break

            ecosystem = str(self.purl.type).casefold()
            pkg_mgr = ""
            pkg_type = self.properties.get("aquasecurity:trivy:PkgType", "")

            if self._is_os_pkgtype(pkg_type) or is_os_purl(self.purl):
                if pkg_type in OS_PACKAGE_TYPES_USING_TYPE_AND_DISTRO_AS_ECOSYSTEM:
                    # For these OS types, we use pkg_type+distro as the ecosystem
                    distro = (
                        self.purl.qualifiers.get("distro")
                        if isinstance(self.purl.qualifiers, dict)
                        else ""
                    )
                    ecosystem = str(
                        (pkg_type + "-" + self._fix_distro(distro)) if distro else self.purl.type
                    ).casefold()
                else:
                    distro = (
                        self.purl.qualifiers.get("distro")
                        if isinstance(self.purl.qualifiers, dict)
                        else ""
                    )
                    ecosystem = str(
                        self._fix_distro(distro) if distro else self.purl.type
                    ).casefold()

            elif self.targets and (
                mgr := self._find_pkg_mgr(merged_components_map, [t.ref for t in self.targets])
            ):
                pkg_mgr = str(mgr.properties.get("aquasecurity:trivy:Type", "")).casefold()

            return {
                "pkg_name": pkg_name,
                "source_name": source_name,
                "ecosystem": ecosystem,
                "pkg_mgr": pkg_mgr,
            }

        def _recursive_get_target_name(
            self,
            components_map: dict[str, Any],
            dependencies: dict[str, set[str]],
            current_refs: set[str] = set(),
            target_names: list[tuple[str, int]] = [],
        ) -> list[tuple[str, int]]:
            for ref, dependsOn in dependencies.items():
                if ref in current_refs:
                    continue
                if self.bom_ref not in dependsOn:
                    continue

                if not (target_component := components_map.get(ref)):
                    raise ValueError(f"Missing dependency: {ref}")
                if target_component.type not in {"library"}:
                    # https://cyclonedx.org/docs/1.5/json/#components_items_type
                    target_names.append((target_component.name or "", len(current_refs)))

                self._recursive_get_target_name(
                    components_map, dependencies, current_refs | {ref}, target_names
                )

            return target_names

        def _get_target_name(
            self,
            components_map: dict[str, Any],
            dependencies: dict[str, set[str]],
        ) -> str:
            """
            Determines the name of the target component that is closest (least depth)
            to the current component in the dependency graph.
            """
            target_names = self._recursive_get_target_name(components_map, dependencies)
            return min(target_names, key=lambda x: x[1])[0]

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
        for data in raw_components:
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

        merged_components_map = copy.deepcopy(components_map)
        merged_components_map[meta_component.get("bom-ref", "")] = TrivyCDXParser.CDXComponent(
            bom_ref=meta_component.get("bom-ref", ""),
            type=meta_component.get("type", ""),
            group=meta_component.get("group", ""),
            name=meta_component.get("name", ""),
            version=meta_component.get("version", ""),
            raw_purl=meta_component.get("purl", ""),
            properties={x["name"]: x["value"] for x in meta_component.get("properties", [])},
        )

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
            if not (target_component := merged_components_map.get(dep_ref)):
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
                if not (pkg_component := merged_components_map.get(pkg_ref)):
                    raise ValueError(f"Missing component: {pkg_ref}")
                pkg_component.targets |= {TrivyCDXParser.CDXComponent.Target(dep_ref, target_name)}

        # convert components to artifacts
        artifacts_map: dict[str, Artifact] = {}  # {artifacts_key: artifact}
        for component in components_map.values():
            if not component.version:
                continue  # maybe directory or image
            if not (package_info := component.to_package_info(merged_components_map)):
                continue  # omit not packages

            artifacts_key = (
                f"{package_info['pkg_name']}:{package_info['ecosystem']}:{package_info['pkg_mgr']}"
            )
            artifact = artifacts_map.get(
                artifacts_key,
                Artifact(
                    package_name=package_info["pkg_name"],
                    source_name=package_info["source_name"],
                    ecosystem=package_info["ecosystem"],
                    package_manager=package_info["pkg_mgr"],
                ),
            )
            artifacts_map[artifacts_key] = artifact
            target_name = component._get_target_name(components_map, dependencies)
            print("testes target_name:", target_name)
            new_target = (target_name, component.version)
            if new_target in artifact.targets:
                error_message("conflicted target:", artifacts_key, new_target)
            else:
                artifact.targets.add(new_target)
            artifact.versions.add(component.version)

        return list(artifacts_map.values())
