from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class ContainerdProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "containerd"
            case PackageFamily.RPM:
                return package_name == "containerd.io"
            case PackageFamily.ALPINE:
                return package_name == "containerd"
            case PackageFamily.GO:
                return package_name in [
                    "github.com/containerd/containerd",
                    "github.com/containerd/containerd/v2",
                ]
            case _:
                return False
