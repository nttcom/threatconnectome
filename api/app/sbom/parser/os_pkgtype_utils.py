"""
Utility functions for handling and identifying OS-related package types.

This module provides functions to determine if a package type is associated with
an operating system package, and defines the recognized OS package types (apk, deb, rpm).
"""

"""
We officially support only OS package types for Alpine Linux, Ubuntu, and Rocky Linux.
OS package types:
- Alpine Linux: alpine
- Chainguard: wolfi
- Minimos:
- Wolfi: wolfi
- Debian: debian
- Ubuntu: ubuntu
- Echo:
- Alma Linux: alma
- Amazon: amazon
- AzureLinux: azurelinux
- CentOS: centos
- Fedora: fedora
- Oracle: oracle
- RedHat: redhat
- Rocky: rocky
- openSUSE-leap: opensuse-leap
- openSUSE-tumbleweed: opensuse-tumbleweed
- SLEM: slem
- SLES: sles
- Bottlerocket: bottlerocket
- CBL-Mariner: cbl-mariner
- Photon: photon
"""

OS_PACKAGE_TYPES = [
    "alpine",
    "ubuntu",
    "rocky",
    "wolfi",
    "debian",
    "alma",
    "amazon",
    "azurelinux",
    "centos",
    "fedora",
    "oracle",
    "redhat",
    "opensuse-leap",
    "opensuse-tumbleweed",
    "slem",
    "sles",
    "bottlerocket",
    "cbl-mariner",
    "photon",
]

# OS types that combine pkg_type and distro when treated as ecosystem
# Example: "alpine" is formatted as "alpine+distro" instead of just "distro"
OS_PACKAGE_TYPES_USING_TYPE_AND_DISTRO_AS_ECOSYSTEM = ["alpine"]


def is_os_pkgtype(pkg_type: str | None) -> bool:
    """
    Determines whether a package type string represents an OS package.

    Args:
        pkg_type: Package type string to evaluate

    Returns:
        True if the package type is an OS package type, False otherwise

    Notes:
        - Returns True if pkg_type is in OS_PACKAGE_TYPES
        - Returns False if pkg_type is None
    """
    if not pkg_type:
        return False

    # Check if the package type matches any known OS package type
    return pkg_type in OS_PACKAGE_TYPES
