from app.business.eol.version.MajorOnlyVersion import MajorOnlyVersion
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class AmazonCorrettoProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        try:
            major_version = MajorOnlyVersion(package_version, self.ecosystem).get_version()
        except Exception:
            major_version = None

        package_family = PackageFamily.from_registry(self.ecosystem)

        # Debian packages often use names like: java-25-amazon-corretto-jdk
        if package_family == PackageFamily.DEBIAN:
            if major_version:
                return package_name == f"java-{major_version}-amazon-corretto-jdk"
            return package_name == "java-amazon-corretto-jdk" or "amazon-corretto" in package_name

        # RPM packages may use names like: amazon-corretto-25 or corretto-25
        if package_family == PackageFamily.RPM:
            if major_version:
                return package_name.startswith(
                    f"amazon-corretto-{major_version}"
                ) or package_name.startswith(f"corretto-{major_version}")
            return "corretto" in package_name

        # Alpine or other ecosystems: try to match by name substring
        if package_family == PackageFamily.ALPINE:
            if major_version:
                return f"{major_version}" in package_name and "corretto" in package_name
            return "corretto" in package_name

        # Fallback: check substring
        return "amazon-corretto" in package_name or "corretto" in package_name
