from app.business.eol.version.MajorOnlyVersion import MajorOnlyVersion
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class PostgresqlProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def mutch_package(self, package_name: str, package_version: str) -> bool:
        major_version = MajorOnlyVersion(package_version, self.ecosystem).get_version()
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == f"postgresql-{major_version}"
            case PackageFamily.RPM:
                return package_name in ["postgresql", "postgresql-server"]
            case PackageFamily.ALPINE:
                return package_name in [
                    f"postgresql{major_version}",
                    f"postgresql{major_version}-client",
                ]
            case _:
                return False
