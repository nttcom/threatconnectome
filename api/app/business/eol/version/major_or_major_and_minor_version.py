import logging

from .eol_base_version import EoLBaseVersion
from .major_and_minor_version import MajorAndMinorVersion
from .major_only_version import MajorOnlyVersion


class MajorOrMajorAndMinorVersion(EoLBaseVersion):
    """
    Return both major and major.minor patterns.
    Order: prefer `major` first, then `major.minor`.
    Useful when product records use major as primary key.
    """

    def __init__(self, version: str, ecosystem: str):
        try:
            self._major = MajorOnlyVersion(version, ecosystem).get_versions()[0]
            self._major_minor = MajorAndMinorVersion(version, ecosystem).get_versions()[0]
        except Exception as e:
            log = logging.getLogger(__name__)
            log.error(
                f"Failed to parse combined versions from '{version}' (ecosystem: {ecosystem}): {e}"
            )
            self._major = version
            self._major_minor = version

    def get_versions(self) -> list[str]:
        versions = [self._major]
        if self._major_minor and self._major_minor != self._major:
            versions.append(self._major_minor)
        return versions
