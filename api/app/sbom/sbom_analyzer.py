import json
import re
from typing import (
    Type,
)

from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator

from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)
from app.sbom.parser.syft_cdx_parser import SyftCDXParser
from app.sbom.parser.syft_spdx_parser import SyftSPDXParser
from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser
from app.utility.progress_logger import TimeBasedProgressLogger


def _inspect_cyclonedx(
    sbom_bom: Bom,
) -> tuple[str, str | None]:  # tool_name, tool_version
    def _get_tool0(jdata_: Bom) -> Component:
        # https://cyclonedx.org/docs/1.5/json/#metadata_tools
        tools_ = jdata_.metadata.tools
        if tools_.components:  # CDX1.5
            return tools_.components[0]
        if tools_.services:  # CDX1.5
            return tools_.services[0]
        if tools_.tools:  # CDX1.5 (legacy)
            return tools_.tools[0]

        raise ValueError("Not supported CycloneDX format")

    try:
        tool0 = _get_tool0(sbom_bom)
        tool_name = tool0.name
        tool_version = tool0.version
        return (tool_name, tool_version)
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported CycloneDX format")


def _inspect_spdx(sbom_json: dict) -> tuple[str, str | None]:  # tool_name, tool_version
    creators = (
        sbom_json.get("creationInfo", {}).get("creators", [])
        if isinstance(sbom_json.get("creationInfo", {}), dict)
        else []
    )
    for creator in creators:
        if not isinstance(creator, str) or not creator.startswith("Tool:"):
            continue
        tool = creator.split(":", 1)[1].strip()
        if not tool:
            continue

        if match := re.match(r"([A-Za-z0-9_.-]+?)-v?([0-9].+)$", tool):
            return (match.group(1).casefold(), match.group(2))
        return (tool.casefold(), None)

    raise ValueError("Not supported SPDX format")


def _validate_and_get_cyclonedx_version(sbom_json: dict, sbom_str: str) -> str:
    spec_versions = {
        "1.6": SchemaVersion.V1_6,
        "1.5": SchemaVersion.V1_5,
        "1.4": SchemaVersion.V1_4,
    }
    for ver, schema_ver in spec_versions.items():
        if sbom_json.get("specVersion") == ver:
            validator = JsonStrictValidator(schema_ver)
            if validation_errors := validator.validate_str(sbom_str):
                raise ValueError(
                    "Not supported file format. ValidationError: " + repr(validation_errors)
                )
            return ver
    raise ValueError("Not supported CycloneDX specVersion")


def _validate_and_get_version(sbom_json: dict, sbom_str: str) -> str:
    try:
        if sbom_json.get("bomFormat") == "CycloneDX":
            return _validate_and_get_cyclonedx_version(sbom_json, sbom_str)
        elif sbom_json.get("SPDXID") == "SPDXRef-DOCUMENT":
            if sbom_json.get("spdxVersion") == "SPDX-2.3":
                return "2.3"
            raise ValueError("Not supported SPDX specVersion")
        else:
            raise ValueError("Not supported file format")
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported file format")


SBOM_PARSERS: dict[tuple[str, str], Type[SBOMParser]] = {
    # (spec_name, tool_name) : SBOMParser
    ("CycloneDX", "trivy"): TrivyCDXParser,
    ("CycloneDX", "syft"): SyftCDXParser,
    ("SPDX", "syft"): SyftSPDXParser,
}


def sbom_json_to_artifact_json_lines(
    sbom_str: str,
    progress: TimeBasedProgressLogger,
) -> list[dict]:
    sbom_json = json.loads(sbom_str)
    progress.add_progress(0.1)
    spec_version = _validate_and_get_version(sbom_json, sbom_str)
    progress.add_progress(8.9)

    sbom_data: SBOM
    if sbom_json.get("bomFormat") == "CycloneDX":
        cdx_bom = Bom.from_json(sbom_json)  # type: ignore[attr-defined]
        sbom_data = cdx_bom
        progress.add_progress(1.0)
        tool_name, tool_version = _inspect_cyclonedx(cdx_bom)
        sbom_info = SBOMInfo("CycloneDX", spec_version, tool_name, tool_version)
    else:
        sbom_data = sbom_json
        progress.add_progress(1.0)
        tool_name, tool_version = _inspect_spdx(sbom_json)
        sbom_info = SBOMInfo("SPDX", spec_version, tool_name, tool_version)

    sbom_parser = SBOM_PARSERS.get((sbom_info.spec_name, sbom_info.tool_name))
    if not sbom_parser:
        raise ValueError("Not supported file format")

    artifacts = sbom_parser.parse_sbom(sbom_data, sbom_info, progress)
    return [
        artifact.to_json()
        for artifact in sorted(
            artifacts, key=lambda a: (a.package_name, a.ecosystem, a.package_manager)
        )
    ]
