import logging

from univers.debian import Version as DebianVersion
from univers.rpm import RpmVersion

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class AmazonCorrettoVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        package_family = PackageFamily.from_registry(ecosystem)

        try:
            match package_family:
                case PackageFamily.DEBIAN:
                    deb = DebianVersion.from_string(version)
                    # str(deb) should include epoch and revision if present
                    self.version = str(deb)
                    return
                case PackageFamily.RPM:
                    rpm = RpmVersion.from_string(version)
                    self.version = str(rpm)
                    return
                case _:
                    self.version = version
                    return
        except Exception as exception:
            log = logging.getLogger(__name__)
            log.error(
                "Failed to parse version from" f" '{version}' (ecosystem: {ecosystem}): {exception}"
            )
            self.version = version
