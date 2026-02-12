import logging

from univers.debian import Version as DebianVersion
from univers.rpm import RpmVersion
from univers.versions import (
    PypiVersion,
    SemverVersion,
)

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class MajorAndMinorVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        package_family = PackageFamily.from_registry(ecosystem)

        try:
            match package_family:
                case PackageFamily.DEBIAN:
                    version_parts = DebianVersion.from_string(version).upstream.split(".")
                case PackageFamily.RPM:
                    version_parts = RpmVersion.from_string(version).version.split(".")
                case PackageFamily.ALPINE:
                    semver_version = SemverVersion(version)
                    self.version = f"{semver_version.major}.{semver_version.minor}"
                    return
                case PackageFamily.PYPI:
                    version_parts = str(PypiVersion(version)).split(".")
                case _:
                    self.version = version
                    return

            self.version = ".".join(version_parts[:2])
        except Exception as exception:
            log = logging.getLogger(__name__)
            log.error(
                "Failed to parse version from" f" '{version}' (ecosystem: {ecosystem}): {exception}"
            )
            self.version = version
