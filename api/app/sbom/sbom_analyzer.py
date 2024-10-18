from typing import (
    Type,
)

from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)
from app.sbom.parser.syft_cdx_parser import SyftCDXParser
from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser


def _inspect_cyclonedx(sbom: SBOM) -> tuple[str, str | None]:  # tool_name, tool_version
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


def _inspect_spdx(sbom: SBOM) -> tuple[str, str | None]:  # tool_name, tool_version
    raise ValueError("SPDX is not yet supported")


def _inspect_sbom(sbom: SBOM) -> SBOMInfo:
    try:
        if sbom.get("bomFormat") == "CycloneDX":
            spec_name = "CycloneDX"
            spec_version = sbom["specVersion"]
            tool_name, tool_version = _inspect_cyclonedx(sbom)
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
    sbom_info = _inspect_sbom(sbom)
    sbom_parser = SBOM_PARSERS.get((sbom_info.spec_name, sbom_info.tool_name))
    if not sbom_parser:
        raise ValueError("Not supported file format")

    artifacts = sbom_parser.parse_sbom(sbom, sbom_info)
    return [artifact.to_json() for artifact in sorted(artifacts, key=lambda a: a.tag)]
