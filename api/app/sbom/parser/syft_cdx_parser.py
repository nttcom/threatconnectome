import os
import re
from dataclasses import dataclass, field
from typing import (
    Any,
    ClassVar,
    NamedTuple,
    Pattern,
)

from packageurl import PackageURL

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.debug_info_outputer import error_message
from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.sbom_parser import (
    SBOM,
    SBOMParser,
)


class SyftCDXParser(SBOMParser):
    @dataclass
    class CDXComponent:
        class PkgMgrInfo(NamedTuple):
            name: str
            location_path: str

        bom_ref: str
        type: str
        group: str
        name: str
        version: str
        raw_purl: str | None
        properties: dict[str, Any]
        purl: PackageURL | None = field(init=False, repr=False)
        mgr_info: PkgMgrInfo | None = field(init=False, repr=False)

        # https://github.com/anchore/syft/blob/main/syft/pkg/cataloger/ * /cataloger.go
        # Note: pkg_mgr is not defined in syft. use the same value in trivy (if exists).
        location_to_pkg_mgr: ClassVar[list[tuple[str, Pattern[str]]]] = [
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

        def _guess_mgr(self) -> PkgMgrInfo | None:
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

        def to_package_info(self) -> dict | None:
            if not self.purl:
                return None
            pkg_name = (
                self.group + "/" + self.name if self.group else self.name
            ).casefold()  # given by syft. may include namespace in some case.

            source_name = None
            for key, value in self.properties.items():
                if "syft:metadata:source" in key:
                    source_name = str(value).casefold()
                    break

            if not source_name and self.purl and isinstance(self.purl.qualifiers, dict):
                source_name = self.purl.qualifiers.get("upstream")

            distro = (
                self.purl.qualifiers.get("distro")
                if self.purl and isinstance(self.purl.qualifiers, dict)
                else None
            )
            pkg_info = str(distro).casefold() if distro else str(self.purl.type).casefold()
            pkg_mgr = (self.mgr_info.name).casefold() if self.mgr_info else ""

            return {
                "pkg_name": pkg_name,
                "source_name": source_name,
                "ecosystem": pkg_info,
                "pkg_mgr": pkg_mgr,
            }

    @classmethod
    def parse_sbom(cls, sbom: SBOM, sbom_info: SBOMInfo) -> list[Artifact]:
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
        return actual_parse_func(sbom)

    @classmethod
    def parse_func_1_4(cls, sbom: SBOM) -> list[Artifact]:
        meta_component = sbom.get("metadata", {}).get("component")
        raw_components = sbom.get("components", [])

        # parse components
        components_map: dict[str, SyftCDXParser.CDXComponent] = {}
        for data in [meta_component, *raw_components]:
            if not data:
                continue
            try:
                components_map[data["bom-ref"]] = SyftCDXParser.CDXComponent(
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
                error_message("Dropped component:", data)

        # convert components to artifacts
        artifacts_map: dict[str, Artifact] = {}  # {artifacts_key: artifact}
        for component in components_map.values():
            if not component.version:
                continue  # maybe directory or image
            if not (package_info := component.to_package_info()):
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
            if component.mgr_info:
                new_target = (component.mgr_info.location_path, component.version)
                if new_target in artifact.targets:
                    error_message("conflicted target:", artifacts_key, new_target)
                artifact.targets |= {(component.mgr_info.location_path, component.version)}
            artifact.versions |= {component.version}

        return list(artifacts_map.values())
