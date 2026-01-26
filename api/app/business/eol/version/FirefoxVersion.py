from univers.debian import Version as DebianVersion
from univers.rpm import RpmVersion

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class FirefoxVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        self.version = version
        self.package_family = PackageFamily.from_registry(ecosystem)

        match self.package_family:
            case PackageFamily.DEBIAN:
                self.version = DebianVersion.from_string(self.version).upstream.split(".")[0]
            case PackageFamily.RPM:
                self.version = RpmVersion.from_string(self.version).version.split(".")[0]
            case _:
                self.version = version
