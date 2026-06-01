from app.detector.package_family import PackageFamily

from .eol_base_product import EoLBaseProduct


class Log4jProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name in ["liblog4j2-java", "liblog4j1.2-java"]
            case PackageFamily.RPM:
                return package_name == "log4j"
            case _:
                return False
