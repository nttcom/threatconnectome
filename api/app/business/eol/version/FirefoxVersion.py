from univers.debian import Version as DebianVersion
from univers.rpm import RpmVersion

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class FirefoxVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        self.package_family = PackageFamily.from_registry(ecosystem)

        try:
            match self.package_family:
                case PackageFamily.DEBIAN:
                    self.version = DebianVersion.from_string(version).upstream.split(".")[0]
                case PackageFamily.RPM:
                    self.version = RpmVersion.from_string(version).version.split(".")[0]
                case _:
                    self.version = version
        except Exception:
            self.version = version
