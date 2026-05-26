from collections import defaultdict
from typing import Any

from packageurl import PackageURL

from app.sbom.parser import syft_common
from app.sbom.parser.artifact import Artifact
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import SBOM, SBOMParser
from app.utility.progress_logger import TimeBasedProgressLogger


class SyftSPDXParser(SBOMParser):
    @staticmethod
    def _parse_purl(package: dict[str, Any]) -> PackageURL | None:
        external_refs = package.get("externalRefs")
        if not isinstance(external_refs, list):
            return None

        for external_ref in external_refs:
            if not isinstance(external_ref, dict):
                continue
            if str(external_ref.get("referenceType", "")).casefold() != "purl":
                continue
            locator = external_ref.get("referenceLocator")
            if not isinstance(locator, str):
                continue
            try:
                return PackageURL.from_string(locator)
            except ValueError:
                continue

        return None

    @staticmethod
    def _get_source_name(purl: PackageURL) -> str | None:
        # sourceInfo in SPDX is a free-form description, not a source package name.
        # Use the upstream purl qualifier instead, consistent with syft CycloneDX behavior.
        if isinstance(purl.qualifiers, dict) and (upstream := purl.qualifiers.get("upstream")):
            if str(upstream).endswith(".rpm"):
                try:
                    return syft_common.get_source_name_from_rpm_filename(str(upstream)).casefold()
                except ValueError:
                    pass
            return str(upstream).casefold()
        return None

    @staticmethod
    def _get_package_manager_from_path(path: str) -> tuple[str, str]:
        return syft_common.get_package_manager_from_path(path)

    @staticmethod
    def _get_package_manager(package: dict[str, Any]) -> tuple[str, str | None]:
        package_filename = package.get("packageFileName")
        if not isinstance(package_filename, str) or not package_filename:
            return ("", None)

        return SyftSPDXParser._get_package_manager_from_path(package_filename)

    @staticmethod
    def _get_ecosystem(purl: PackageURL) -> str:
        return syft_common.get_ecosystem_from_purl(purl)

    @staticmethod
    def _extract_package_info(package: dict[str, Any]) -> dict[str, Any] | None:
        purl = SyftSPDXParser._parse_purl(package)
        if not purl:
            return None

        name = package.get("name")
        if not isinstance(name, str) or not name:
            return None

        pkg_name = name.casefold()
        source_name = SyftSPDXParser._get_source_name(purl)
        ecosystem = SyftSPDXParser._get_ecosystem(purl)
        package_manager, package_filename = SyftSPDXParser._get_package_manager(package)

        return {
            "pkg_name": pkg_name,
            "source_name": source_name,
            "ecosystem": ecosystem,
            "package_manager": package_manager,
            "target_path": package_filename,
        }

    @staticmethod
    def _build_target_map(sbom: dict[str, Any]) -> dict[str, set[str]]:
        target_map: dict[str, set[str]] = defaultdict(set)

        package_name_map = {
            package.get("SPDXID"): str(package.get("name", "")).casefold()
            for package in sbom.get("packages", [])
            if isinstance(package, dict) and isinstance(package.get("SPDXID"), str)
        }
        file_name_map = {
            file.get("SPDXID"): str(file.get("fileName", ""))
            for file in sbom.get("files", [])
            if isinstance(file, dict) and isinstance(file.get("SPDXID"), str)
        }
        element_name_map = package_name_map | file_name_map

        for relationship in sbom.get("relationships", []):
            if not isinstance(relationship, dict):
                continue
            source = relationship.get("spdxElementId")
            target = relationship.get("relatedSpdxElement")
            rel_type = str(relationship.get("relationshipType", "")).upper()
            if not isinstance(source, str) or not isinstance(target, str):
                continue

            if rel_type in {"DEPENDS_ON", "CONTAINS", "DESCRIBES"}:
                if source_name := element_name_map.get(source):
                    target_map[target].add(source_name)
            elif rel_type in {"DEPENDENCY_OF", "CONTAINED_BY", "DESCRIBED_BY"}:
                if target_name := element_name_map.get(target):
                    target_map[source].add(target_name)
            elif rel_type == "OTHER" and str(relationship.get("comment", "")).startswith(
                "evident-by:"
            ):
                if target_name := file_name_map.get(target):
                    target_map[source].add(target_name)
                elif source_name := file_name_map.get(source):
                    target_map[target].add(source_name)

        return target_map

    @classmethod
    def parse_sbom(
        cls,
        sbom_bom: SBOM,
        sbom_info: SBOMInfo,
        progress: TimeBasedProgressLogger,
    ) -> list[Artifact]:
        if (
            sbom_info.spec_name != "SPDX"
            or sbom_info.spec_version != "2.3"
            or sbom_info.tool_name != "syft"
        ):
            raise ValueError(f"Not supported: {sbom_info}")
        if not isinstance(sbom_bom, dict):
            raise ValueError("Not supported file format")
        return cls.parse_func_2_3(sbom_bom, progress)

    @classmethod
    def parse_func_2_3(
        cls,
        sbom: dict[str, Any],
        progress: TimeBasedProgressLogger,
    ) -> list[Artifact]:
        artifacts_map: dict[str, Artifact] = {}
        packages = [package for package in sbom.get("packages", []) if isinstance(package, dict)]
        target_map = cls._build_target_map(sbom)

        PROGRESS_ALLOCATION = 20
        if len(packages) > 0:
            step_progress = PROGRESS_ALLOCATION / len(packages)
        else:
            step_progress = PROGRESS_ALLOCATION
            progress.add_progress(step_progress)

        for package in packages:
            progress.add_progress(step_progress)

            version = package.get("versionInfo")
            spdx_id = package.get("SPDXID")
            primary_package_purpose = str(package.get("primaryPackagePurpose", "")).upper()
            if not isinstance(version, str) or not version:
                continue
            if not isinstance(spdx_id, str) or not spdx_id:
                continue
            if primary_package_purpose in {"CONTAINER", "FILE"}:
                continue

            package_info = cls._extract_package_info(package)
            if not package_info:
                continue

            targets = target_map.get(spdx_id, set())
            package_manager = package_info["package_manager"]
            if not package_manager:
                for target in sorted(targets):
                    package_manager = cls._get_package_manager_from_path(target)[0]
                    if package_manager:
                        break

            artifacts_key = (
                f"{package_info['pkg_name']}:{package_info['ecosystem']}" f":{package_manager}"
            )
            artifact = artifacts_map.get(
                artifacts_key,
                Artifact(
                    package_name=package_info["pkg_name"],
                    source_name=package_info["source_name"],
                    ecosystem=package_info["ecosystem"],
                    package_manager=package_manager,
                ),
            )
            artifacts_map[artifacts_key] = artifact

            if targets:
                for target in targets:
                    artifact.targets.add((target, version))
            elif package_info["target_path"]:
                artifact.targets.add((str(package_info["target_path"]), version))

            artifact.versions.add(version)

        return list(artifacts_map.values())
