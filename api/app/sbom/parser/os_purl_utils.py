"""
Utility functions for handling and identifying OS-related Package URLs.

This module provides functions to determine if a package URL (purl) is associated with
an operating system package, and includes mappings between OS types and their
corresponding purl types.
"""

from packageurl import PackageURL

# Mapping of OS names to their corresponding PURL types
OS_TYPE_PURL_TYPES = {
    "alpine": "apk",
    "debian": "deb",
    "ubuntu": "deb",
    "alma": "rpm",
    "amazon": "rpm",
    "azurelinux": "rpm",
    "centos": "rpm",
    "fedora": "rpm",
    "oracle": "rpm",
    "redhat": "rpm",
    "rocky": "rpm",
    "opensuse": "rpm",
    "opensuse-leap": "rpm",
    "opensuse-tumbleweed": "rpm",
    "slem": "rpm",
    "sles": "rpm",
    "bottlerocket": "rpm",
    "cbl-mariner": "rpm",
    "chainguard": "apk",
    "echo": "deb",
    "minimos": "apk",
    "photon": "rpm",
    "wolfi": "apk",
}


def is_os_purl(purl: PackageURL | None) -> bool:
    """
    Determines whether a package URL represents an OS package.

    Args:
        purl: PackageURL object to evaluate

    Returns:
        True if the package is an OS package, False otherwise

    Notes:
        The function returns True if any of the following conditions are met:
        - The purl.type matches any value in OS_TYPE_PURL_TYPES
        - Returns False if purl is None
    """
    if not purl:
        return False

    # Check if the package URL type matches any known OS package type
    if purl.type in OS_TYPE_PURL_TYPES.values():
        return True
    else:
        return False
