from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class NumpyProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "python3-numpy"
            case PackageFamily.RPM:
                return package_name == "python3-numpy"
            case PackageFamily.ALPINE:
                return package_name in ["py3-numpy", "py3-numpy-pyc"]
            case PackageFamily.PYPI:
                return package_name == "numpy"
            case _:
                return False
