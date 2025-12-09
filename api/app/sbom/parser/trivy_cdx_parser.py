import re
from typing import (
    Pattern,
)

from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.os_purl_utils import is_os_purl
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
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

OS_PACKAGE_TYPES_USING_TYPE_ONLY_AS_ECOSYSTEM = ["wolfi"]


class TrivyCDXParser(SBOMParser):
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
    def _get_propety_value(component: Component, key: str) -> str | None:
        for property in component.properties:
            if property.name == key:
                return property.value
        return None

    @staticmethod
    def _find_pkg_mgr(target_components: list[Component]) -> Component | None:
        if len(target_components) == 0:
            return None
        if len(target_components) == 1:
            return target_components[0]
        for component in target_components:
            trivy_class = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:Class")
            if trivy_class is not None and trivy_class == "os-pkgs":
                return component

            trivy_type = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:Type")
            if trivy_type is not None:
                return component

        return target_components[0]

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

    @staticmethod
    def _to_package_info(component: Component, target_components: list[Component]) -> dict | None:
        if not component.purl:
            return None
        pkg_name = (
            component.group + "/" + component.name if component.group else component.name
        ).casefold()  # given by trivy. may include namespace in some case.

        source_name = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:SrcName")

        ecosystem = str(component.purl.type).casefold()
        pkg_mgr = None
        pkg_type = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:PkgType")

        if TrivyCDXParser._is_os_pkgtype(pkg_type) or is_os_purl(component.purl):
            if (
                pkg_type is not None
                and pkg_type in OS_PACKAGE_TYPES_USING_TYPE_AND_DISTRO_AS_ECOSYSTEM
            ):
                # For these OS types, we use pkg_type+distro as the ecosystem
                distro = (
                    component.purl.qualifiers.get("distro")
                    if isinstance(component.purl.qualifiers, dict)
                    else ""
                )
                ecosystem = str(
                    (pkg_type + "-" + TrivyCDXParser._fix_distro(distro))
                    if distro
                    else component.purl.type
                ).casefold()
            elif pkg_type is not None and pkg_type in OS_PACKAGE_TYPES_USING_TYPE_ONLY_AS_ECOSYSTEM:
                # For these OS types, we use pkg_type only as the ecosystem
                ecosystem = pkg_type.casefold()
            else:
                distro = (
                    component.purl.qualifiers.get("distro")
                    if isinstance(component.purl.qualifiers, dict)
                    else ""
                )
                ecosystem = str(
                    TrivyCDXParser._fix_distro(distro) if distro else component.purl.type
                ).casefold()

        elif mgr := TrivyCDXParser._find_pkg_mgr(target_components):
            pkg_mgr = TrivyCDXParser._get_propety_value(mgr, "aquasecurity:trivy:Type")

        return {
            "pkg_name": pkg_name,
            "source_name": source_name,
            "ecosystem": ecosystem,
            "pkg_mgr": pkg_mgr if pkg_mgr is not None else "",
        }

    @staticmethod
    def _get_direct_source_refs(
        target_ref: str,
        sbom_bom: Bom,
    ) -> list[str]:
        direct_source_refs: list[str] = []
        for dependency1 in sbom_bom.dependencies:
            for dependency2 in dependency1.dependencies:
                if dependency2.ref.value == target_ref:
                    direct_source_refs.append(dependency1.ref.value)
        return direct_source_refs

    @staticmethod
    def _recursive_get_all_source_ref_dict(
        target_ref: str,
        sbom_bom: Bom,
        all_source_ref_dict: dict[str, set[str]],
        current_ref: set[str],
    ) -> set[str]:
        refs: set[str] = set()
        if target_ref in current_ref:
            return refs

        for direct_source_ref in TrivyCDXParser._get_direct_source_refs(target_ref, sbom_bom):
            if direct_source_ref in current_ref:
                continue

            if direct_source_ref not in all_source_ref_dict.keys():
                all_source_ref_dict[direct_source_ref] = (
                    TrivyCDXParser._recursive_get_all_source_ref_dict(
                        direct_source_ref,
                        sbom_bom,
                        all_source_ref_dict,
                        current_ref | {target_ref},
                    )
                )
            refs.update(all_source_ref_dict[direct_source_ref])

            refs.add(direct_source_ref)

        return refs

    @staticmethod
    def _get_all_source_ref_dict(sbom_bom: Bom) -> dict[str, set[str]]:
        all_source_ref_dict: dict[str, set[str]] = {}
        for dependency1 in sbom_bom.dependencies:
            for dependency2 in dependency1.dependencies:
                if dependency2.ref.value in all_source_ref_dict.keys():
                    continue
                all_source_ref_dict[dependency2.ref.value] = (
                    TrivyCDXParser._recursive_get_all_source_ref_dict(
                        dependency2.ref.value,
                        sbom_bom,
                        all_source_ref_dict,
                        set(),
                    )
                )
        return all_source_ref_dict

    @staticmethod
    def _get_target_components(
        component: Component,
        all_components_dict: dict[str, Component],
        all_source_ref_dict: dict[str, set[str]],
    ) -> list[Component]:
        target_components: list[Component] = []
        if component.bom_ref.value is None:
            return target_components
        all_source_refs: set[str] = all_source_ref_dict[component.bom_ref.value]

        for ref in all_source_refs:
            source_component = all_components_dict.get(ref)
            if (
                source_component is not None
                and source_component.type is not None
                and source_component.type.value != "library"
            ):
                target_components.append(source_component)

        return target_components

    @classmethod
    def parse_sbom(cls, sbom_bom: Bom, sbom_info: SBOMInfo) -> list[Artifact]:
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
        return actual_parse_func(sbom_bom)

    @classmethod
    def parse_func_1_5(cls, sbom_bom: Bom) -> list[Artifact]:
        all_components_dict = {}
        if sbom_bom.metadata is not None and sbom_bom.metadata.component is not None:
            meta_component = sbom_bom.metadata.component
            if meta_component.bom_ref.value is not None:
                all_components_dict[meta_component.bom_ref.value] = meta_component
        if sbom_bom.components is not None:
            for raw_component in sbom_bom.components:
                if raw_component.bom_ref.value is not None:
                    all_components_dict[raw_component.bom_ref.value] = raw_component

        for dependency in sbom_bom.dependencies:
            if not any(
                dependency.ref.value == component_ref
                for component_ref in all_components_dict.keys()
            ):
                raise ValueError(f"Missing dependency: {dependency.ref.value}")

        all_source_ref_dict: dict[str, set[str]] = TrivyCDXParser._get_all_source_ref_dict(sbom_bom)

        # convert components to artifacts
        artifacts_map: dict[str, Artifact] = {}  # {artifacts_key: artifact}
        for component in all_components_dict.values():
            if (
                meta_component
                and meta_component.bom_ref
                and component.bom_ref == meta_component.bom_ref
            ):
                continue
            if not component.version:
                continue  # maybe directory or image
            target_components: list[Component] = cls._get_target_components(
                component, all_components_dict, all_source_ref_dict
            )
            if not (package_info := TrivyCDXParser._to_package_info(component, target_components)):
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
            for target_component in target_components:
                if (
                    meta_component
                    and meta_component.bom_ref
                    and target_component.bom_ref == meta_component.bom_ref
                ):
                    continue
                new_target = (target_component.name, component.version)
                if new_target in artifact.targets:
                    continue
                else:
                    artifact.targets.add(new_target)
            artifact.versions.add(component.version)

        return list(artifacts_map.values())
