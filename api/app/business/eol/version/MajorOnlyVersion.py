import logging

from univers.debian import Version as DebianVersion
from univers.rpm import RpmVersion
from univers.versions import PypiVersion, SemverVersion

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class MajorOnlyVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        package_family = PackageFamily.from_registry(ecosystem)

        try:
            match package_family:
                case PackageFamily.DEBIAN:
                    self.version = DebianVersion.from_string(version).upstream.split(".")[0]
                case PackageFamily.RPM:
                    self.version = RpmVersion.from_string(version).version.split(".")[0]
                case PackageFamily.ALPINE:
                    self.version = str(SemverVersion(version).major)
                case PackageFamily.PYPI:
                    self.version = str(PypiVersion(version)).split(".")[0]
                case PackageFamily.NPM:
                    self.version = str(SemverVersion(version).major)
                case _:
                    self.version = version
        except Exception as exception:
            log = logging.getLogger(__name__)
            log.error(
                "Failed to parse version from" f" '{version}' (ecosystem: {ecosystem}): {exception}"
            )
            self.version = version
