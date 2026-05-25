from dataclasses import field
from typing import NamedTuple

from cyclonedx.model import Property
from cyclonedx.model.bom import Bom
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component
from packageurl import PackageURL
from sortedcontainers import SortedSet

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.debug_info_outputer import error_message
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)
from app.sbom.parser.syft_common import (
    get_ecosystem_from_purl,
    get_package_manager_from_path,
    get_source_name_from_rpm_filename,
)
from app.utility.progress_logger import TimeBasedProgressLogger


class SyftCDXParser(SBOMParser):
    class PkgMgrInfo(NamedTuple):
        name: str
        location_path: str

    bom_ref: BomRef
    group: str | None
    name: str
    version: str | None
    purl: PackageURL | None
    properties: SortedSet[Property]
    mgr_info: PkgMgrInfo | None = field(init=False, repr=False)

    @staticmethod
    def _find_location_path(properties: SortedSet[Property], idx: int) -> str | None:
        for prop in properties:
            if prop.name == f"syft:location:{idx}:path":
                return prop.value
        return None

    @staticmethod
    def _guess_mgr(properties: SortedSet[Property]) -> PkgMgrInfo | None:
        # https://github.com/anchore/syft/blob/main/syft/pkg/package.go#L24
        # we do not know which is the best to guess pkg_mgr...

        location_0_path = SyftCDXParser._find_location_path(properties, 0)
        if location_0_path is None:
            return None
        idx = 0
        while True:
            if not (location_path := SyftCDXParser._find_location_path(properties, idx)):
                # could not guess type, but no more locations.
                # return the top of locations as a (hint of) target.
                return SyftCDXParser.PkgMgrInfo("", location_0_path)
            package_manager, _ = get_package_manager_from_path(location_path)
            if package_manager:
                return SyftCDXParser.PkgMgrInfo(package_manager, location_path)  # Eureka!

            idx += 1

    @staticmethod
    def _to_package_info(component: Component) -> dict | None:
        if not component.purl:
            return None
        pkg_name = (
            (component.group + "/" + component.name if component.group else component.name)
            if component.name is not None
            else ""
        ).casefold()  # given by syft. may include namespace in some case.

        source_name = None
        for property in component.properties:
            if property.name == "syft:metadata:source":
                source_name = str(property.value).casefold()
                break
            if property.name == "syft:metadata:sourceRpm":
                try:
                    source_name = get_source_name_from_rpm_filename(property.value).casefold()
                    break
                except ValueError:
                    continue

        if (
            not source_name
            and component.purl
            and isinstance(component.purl.qualifiers, dict)
            and (upstream := component.purl.qualifiers.get("upstream"))
        ):
            source_name = str(upstream).casefold()

        pkg_info = get_ecosystem_from_purl(component.purl)

        mgr_info = SyftCDXParser._guess_mgr(component.properties)

        return {
            "pkg_name": pkg_name,
            "source_name": source_name,
            "ecosystem": pkg_info,
            "mgr_info": mgr_info,
        }

    @classmethod
    def parse_sbom(
        cls,
        sbom_bom: SBOM,
        sbom_info: SBOMInfo,
        progress: TimeBasedProgressLogger,
    ) -> list[Artifact]:
        if not isinstance(sbom_bom, Bom):
            raise ValueError("Not supported file format")
        if (
            sbom_info.spec_name != "CycloneDX"
            or sbom_info.spec_version not in {"1.4", "1.5", "1.6"}
            or sbom_info.tool_name != "syft"
        ):
            raise ValueError(f"Not supported: {sbom_info}")
        actual_parse_func = {
            "1.4": cls.parse_func_1_4,
            "1.5": cls.parse_func_1_4,
            "1.6": cls.parse_func_1_4,
        }.get(sbom_info.spec_version)
        if not actual_parse_func:
            raise ValueError("Internal error: actual_parse_func not found")
        return actual_parse_func(sbom_bom, progress)

    @classmethod
    def parse_func_1_4(
        cls,
        sbom: Bom,
        progress: TimeBasedProgressLogger,
    ) -> list[Artifact]:
        # convert components to artifacts
        artifacts_map: dict[str, Artifact] = {}  # {artifacts_key: artifact}

        meta_component = sbom.metadata.component if sbom.metadata else None
        raw_components = sbom.components if sbom.components else None

        all_components = []
        if meta_component:
            all_components.append(meta_component)
        if raw_components:
            all_components.extend(raw_components)

        PROGRESS_ALLOCATION = 20
        if len(all_components) > 0:
            step_progress = PROGRESS_ALLOCATION / len(all_components)
        else:
            step_progress = PROGRESS_ALLOCATION
            progress.add_progress(step_progress)

        for component in all_components:
            progress.add_progress(step_progress)

            if not component.version:
                continue  # maybe directory or image
            if not (package_info := SyftCDXParser._to_package_info(component)):
                continue  # omit not packages

            mgr_info = package_info["mgr_info"]
            pkg_mgr = mgr_info.name.casefold() if mgr_info and mgr_info.name else ""

            artifacts_key = f"{package_info['pkg_name']}:{package_info['ecosystem']}:{pkg_mgr}"
            artifact = artifacts_map.get(
                artifacts_key,
                Artifact(
                    package_name=package_info["pkg_name"],
                    source_name=package_info["source_name"],
                    ecosystem=package_info["ecosystem"],
                    package_manager=pkg_mgr,
                ),
            )
            artifacts_map[artifacts_key] = artifact
            if mgr_info:
                new_target = (mgr_info.location_path, component.version)
                if new_target in artifact.targets:
                    error_message("conflicted target:", artifacts_key, new_target)
                artifact.targets |= {(mgr_info.location_path, component.version)}
            artifact.versions |= {component.version}

        return list(artifacts_map.values())
