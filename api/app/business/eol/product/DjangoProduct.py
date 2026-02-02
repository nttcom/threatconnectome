from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class DjangoProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def mutch_package(self, package_name: str, package_version: str) -> bool:
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "python3-django"
            case PackageFamily.ALPINE:
                return package_name == "py3-django"
            case PackageFamily.PYPI:
                return package_name == "django"
            case _:
                return False
