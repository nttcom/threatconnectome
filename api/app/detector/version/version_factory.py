from typing import TypeAlias

from univers.versions import GolangVersion, SemverVersion

from app.detector.package_family import PackageFamily
from app.detector.version.ext_debian_version import ExtDebianVersion
from app.detector.version.ext_pypi_version import ExtPypiVersion

# supported version classes:
#   - should be hashable.
#   - required implemented __gt__, __ge__, __lt__, __le__.
#     Note: __eq__ cannot be used to compare versions. use >= and <= instead.
#   - may raise ValueError on errors.
ComparableVersion: TypeAlias = ExtDebianVersion | ExtPypiVersion | SemverVersion | GolangVersion


def gen_version_instance(
    package_family: PackageFamily,
    version_string: str,
) -> ComparableVersion:
    if package_family == PackageFamily.DEBIAN:
        return ExtDebianVersion.from_string(version_string)
    if package_family == PackageFamily.PYPI:
        return ExtPypiVersion(version_string)
    if package_family == PackageFamily.NPM:
        return SemverVersion(version_string)
    if package_family == PackageFamily.GO:
        return GolangVersion(version_string)

    return SemverVersion(version_string)
