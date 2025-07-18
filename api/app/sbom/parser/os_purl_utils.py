"""
Utility functions for handling and identifying OS-related Package URLs.

This module provides functions to determine if a package URL (purl) is associated with
an operating system package, and defines the recognized OS package types (apk, deb, rpm).
"""

from packageurl import PackageURL

"""
Common OS package PURL.type:
- apk: Alpine Linux, Chainguard, Minimos, Wolfi
- deb: Debian, Ubuntu, Echo
- rpm: Alma, Amazon, AzureLinux, CentOS, Fedora, Oracle, RedHat, Rocky, openSUSE,
      openSUSE-leap, openSUSE-tumbleweed, SLEM, SLES, Bottlerocket, CBL-Mariner, Photon
"""

OS_TYPE_PURL_TYPES = ["apk", "deb", "rpm"]


def is_os_purl(purl: PackageURL | None) -> bool:
    """
    Determines whether a package URL represents an OS package.

    Args:
        purl: PackageURL object to evaluate

    Returns:
        True if the package is an OS package, False otherwise

    Notes:
        - Returns True if purl.type is in OS_TYPE_PURL_TYPES (apk, deb, rpm)
        - Returns False if purl is None
    """
    if not purl:
        return False

    # Check if the package URL type matches any known OS package type
    if purl.type in OS_TYPE_PURL_TYPES:
        return True
    else:
        return False
