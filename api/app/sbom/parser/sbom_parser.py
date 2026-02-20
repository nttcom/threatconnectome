from abc import ABC, abstractmethod
from typing import (
    TypeAlias,
)

from cyclonedx.model.bom import Bom

from app.sbom.parser.artifact import Artifact
from app.sbom.parser.sbom_info import SBOMInfo
from app.utility.progress_logger import TimeBasedProgressLogger

SBOM: TypeAlias = dict


class SBOMParser(ABC):
    @classmethod
    @abstractmethod
    def parse_sbom(
        cls,
        sbom_bom: Bom,
        sbom_info: SBOMInfo,
        progress: TimeBasedProgressLogger,
    ) -> list[Artifact]:
        raise NotImplementedError()
