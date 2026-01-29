from univers.versions import PypiVersion

from app.detector.package_family import PackageFamily

from .EoLBaseVersion import EoLBaseVersion


class MajorAndMinorVersion(EoLBaseVersion):
    def __init__(self, version: str, ecosystem: str):
        package_family = PackageFamily.from_registry(ecosystem)

        try:
            match package_family:
                case PackageFamily.PYPI:
                    version_parts = str(PypiVersion(version)).split(".")
                    self.version = (
                        version_parts[0]
                        if len(version_parts) == 1
                        else f"{version_parts[0]}.{version_parts[1]}"
                    )
                case _:
                    self.version = version
        except Exception:
            self.version = version
