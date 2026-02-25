from app.business.eol.version.MajorOnlyVersion import MajorOnlyVersion
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class AmazonCorrettoProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        major_version = MajorOnlyVersion(package_version, self.ecosystem).get_versions()[0]
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.RPM:
                return package_name == f"java-{major_version}-amazon-corretto-devel"
            case PackageFamily.DEBIAN:
                return package_name == f"java-{major_version}-amazon-corretto-jdk"
            case _:
                return False
