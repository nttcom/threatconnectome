from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class RedisProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "redis-server"
            case PackageFamily.RPM:
                return package_name == "redis"
            case PackageFamily.ALPINE:
                return package_name == "redis"
            case _:
                return False
