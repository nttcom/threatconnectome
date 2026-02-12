from app.business.eol.version.MajorAndMinorVersion import MajorAndMinorVersion
from app.business.eol.version.MajorOnlyVersion import MajorOnlyVersion
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class PythonProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        major_version = MajorOnlyVersion(package_version, self.ecosystem).get_version()
        major_and_minor_version = MajorAndMinorVersion(
            package_version, self.ecosystem
        ).get_version()
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name in [
                    f"python{major_version}",
                    f"python{major_and_minor_version}",
                ]
            case PackageFamily.RPM:
                return package_name == f"python{major_version}"
            case PackageFamily.ALPINE:
                return package_name in [
                    f"python{major_version}",
                    f"python{major_version}-pyc",
                    f"python{major_version}-pycache-pyc0",
                ]
            case _:
                return False
