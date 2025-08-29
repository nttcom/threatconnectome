from abc import ABC, abstractmethod
from typing import (
    TypeAlias,
)

from cyclonedx.model.bom import Bom

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.sbom_info import SBOMInfo

SBOM: TypeAlias = dict


class SBOMParser(ABC):
    @classmethod
    @abstractmethod
    def parse_sbom(cls, deserialized_bom: Bom, sbom_info: SBOMInfo, sbom: SBOM) -> list[Artifact]:
        raise NotImplementedError()
