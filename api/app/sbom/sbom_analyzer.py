from typing import (
    Type,
)

from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component

from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)
from app.sbom.parser.syft_cdx_parser import SyftCDXParser
from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser


def _inspect_cyclonedx(
    sbom: SBOM, deserialized_bom: Bom
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
        tool0 = _get_tool0(deserialized_bom)
        tool_name = tool0.name
        tool_version = tool0.version
        return (tool_name, tool_version)
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported CycloneDX format")


def _inspect_spdx(sbom: SBOM) -> tuple[str, str | None]:  # tool_name, tool_version
    raise ValueError("SPDX is not yet supported")


def _inspect_sbom(sbom: SBOM, deserialized_bom: Bom) -> SBOMInfo:
    try:
        if sbom.get("bomFormat") == "CycloneDX":
            spec_name = "CycloneDX"
            spec_version = sbom["specVersion"]
            tool_name, tool_version = _inspect_cyclonedx(sbom, deserialized_bom)
        elif sbom.get("SPDXID") == "SPDXRef-DOCUMENT":
            spec_name = "SPDX"
            spec_version = sbom["spdxVersion"]
            tool_name, tool_version = _inspect_spdx(sbom)
        else:
            raise ValueError("Not supported file format")
        return SBOMInfo(spec_name, spec_version, tool_name, tool_version)
    except (IndexError, KeyError, TypeError):
        raise ValueError("Not supported file format")


SBOM_PARSERS: dict[tuple[str, str], Type[SBOMParser]] = {
    # (spec_name, spec_version, tool_name) : SBOMParser
    ("CycloneDX", "trivy"): TrivyCDXParser,
    ("CycloneDX", "syft"): SyftCDXParser,
}


def sbom_json_to_artifact_json_lines(jdata: dict) -> list[dict]:
    sbom: SBOM = jdata
    deserialized_bom = Bom.from_json(sbom)  # type: ignore
    sbom_info = _inspect_sbom(sbom, deserialized_bom)
    sbom_parser = SBOM_PARSERS.get((sbom_info.spec_name, sbom_info.tool_name))
    if not sbom_parser:
        raise ValueError("Not supported file format")

    artifacts = sbom_parser.parse_sbom(deserialized_bom, sbom_info, sbom)
    return [
        artifact.to_json()
        for artifact in sorted(
            artifacts, key=lambda a: (a.package_name, a.ecosystem, a.package_manager)
        )
    ]
