import re
from typing import (
    Pattern,
)

from cyclonedx.model.bom import Bom
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component
from cyclonedx.model.dependency import Dependency

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.debug_info_outputer import error_message
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
    def _find_pkg_mgr(target_components: set[Component]) -> Component | None:
        if len(target_components) == 0:
            return None
        if len(target_components) == 1:
            return target_components.pop()
        for component in target_components:
            trivy_class = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:Class")
            if trivy_class is not None and trivy_class == "os-pkgs":
                return component

            trivy_type = TrivyCDXParser._get_propety_value(component, "aquasecurity:trivy:Type")
            if trivy_type is not None:
                return component

        return target_components.pop()

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
    def _to_package_info(component: Component, target_components: set[Component]) -> dict | None:
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
    def _get_component_by_dependency(
        dependency: Dependency, all_components: list[Component]
    ) -> Component | None:
        return next(
            (component for component in all_components if component.bom_ref == dependency.ref),
            None,
        )

    @staticmethod
    def _get_source_dependencies(
        ref: BomRef,
        sbom_bom: Bom,
    ) -> list[Dependency]:
        source_dependencies: list[Dependency] = []
        for dependency1 in sbom_bom.dependencies:
            for dependency2 in dependency1.dependencies:
                if dependency2.ref == ref:
                    source_dependencies.append(dependency1)
        return source_dependencies

    @staticmethod
    def _recursive_get_target_components(
        dependency: Dependency,
        sbom_bom: Bom,
        all_components: list[Component],
        current_ref: set[BomRef],
    ) -> set[Component]:
        components: set[Component] = set()
        if dependency.ref in current_ref:
            return components
        source_dependencies: list[Dependency] = TrivyCDXParser._get_source_dependencies(
            dependency.ref, sbom_bom
        )
        for dep in source_dependencies:
            if dep.ref in current_ref:
                continue
            component = TrivyCDXParser._get_component_by_dependency(dep, all_components)
            if (
                component is not None
                and component.type is not None
                and component.type.value != "library"
            ):
                components.add(component)
            components |= TrivyCDXParser._recursive_get_target_components(
                dep, sbom_bom, all_components, current_ref | {dep.ref}
            )
        return components

    @staticmethod
    def _get_target_components(
        component: Component,
        sbom_bom: Bom,
        all_components: list[Component],
    ) -> set[Component]:
        target_components: set[Component] = set()
        source_dependencies: list[Dependency] = TrivyCDXParser._get_source_dependencies(
            component.bom_ref, sbom_bom
        )

        for dep in source_dependencies:
            source_component = TrivyCDXParser._get_component_by_dependency(dep, all_components)
            if (
                source_component is not None
                and source_component.type is not None
                and source_component.type.value != "library"
            ):
                target_components.add(source_component)
            target_components |= TrivyCDXParser._recursive_get_target_components(
                dep, sbom_bom, all_components, set()
            )

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
        meta_component = sbom_bom.metadata.component if sbom_bom.metadata else None
        raw_components = sbom_bom.components if sbom_bom.components else None

        all_components = []
        if meta_component:
            all_components.append(meta_component)
        if raw_components:
            all_components.extend(raw_components)

        for dependency in sbom_bom.dependencies:
            if not any(dependency.ref == component.bom_ref for component in all_components):
                raise ValueError(f"Missing dependency: {dependency.ref.value}")

        # convert components to artifacts
        artifacts_map: dict[str, Artifact] = {}  # {artifacts_key: artifact}
        for component in all_components:
            if (
                meta_component
                and meta_component.bom_ref
                and component.bom_ref == meta_component.bom_ref
            ):
                continue
            if not component.version:
                continue  # maybe directory or image
            target_components: set[Component] = cls._get_target_components(
                component, sbom_bom, all_components
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
                    error_message("conflicted target:", artifacts_key, new_target)
                else:
                    artifact.targets.add(new_target)
            artifact.versions.add(component.version)

        return list(artifacts_map.values())
