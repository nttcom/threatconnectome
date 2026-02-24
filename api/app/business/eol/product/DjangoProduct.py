from app.business.eol.version.MajorOnlyVersion import MajorOnlyVersion
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class DjangoProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        major_version = MajorOnlyVersion(package_version, self.ecosystem).get_versions()[0]
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "python3-django"
            case PackageFamily.RPM:
                return package_name == f"python3-django{major_version}"
            case PackageFamily.ALPINE:
                return package_name == "py3-django"
            case PackageFamily.PYPI:
                return package_name == "django"
            case _:
                return False
