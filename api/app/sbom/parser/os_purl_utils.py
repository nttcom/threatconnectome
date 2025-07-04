"""
Utility functions for handling and identifying OS-related Package URLs.

This module provides functions to determine if a package URL (purl) is associated with
an operating system package, and includes mappings between OS types and their
corresponding purl types.
"""

from packageurl import PackageURL

# Mapping of OS names to their corresponding PURL types
# Each OS is mapped to its appropriate Package URL type
OS_TYPE_PURL_TYPES = {
    # Alpine Linux
    # trivy image --format cyclonedx --output alpine.json alpine:latest
    # pkg:apk/alpine/alpine-keys@2.5-r0?arch=x86_64&distro=3.22.0
    "alpine": "apk",
    # Debian-based distributions
    # trivy image --format cyclonedx --output debian.json debian:latest
    # pkg:deb/debian/adduser@3.134?arch=all&distro=debian-12.11
    "debian": "deb",
    # trivy image --format cyclonedx --output ubuntu.json ubuntu:latest
    # pkg:deb/ubuntu/apt@2.8.3?arch=amd64&distro=ubuntu-24.04
    "ubuntu": "deb",
    # Red Hat-based distributions
    # trivy image --format cyclonedx --output almalinux.json almalinux:latest
    # pkg:rpm/alma/acl@2.3.1-4.el9?arch=x86_64&distro=alma-9.6
    "alma": "rpm",
    # trivy image --format cyclonedx --output amazonlinux.json amazonlinux:latest
    # pkg:rpm/amazon/alternatives@1.15-2.amzn2023.0.2?arch=x86_64&distro=amazon-2023.7.20250609+%28Amazon+Linux%29
    "amazon": "rpm",
    # trivy image --format cyclonedx --output azurelinux.json mcr.microsoft.com/azurelinux/base/core:3.0
    # pkg:rpm/azurelinux/SymCrypt-OpenSSL@1.8.1-1.azl3?arch=x86_64&distro=azurelinux-3.0
    "azurelinux": "rpm",
    # trivy image --format cyclonedx  --output centos.json centos:7
    # pkg:rpm/centos/acl@2.2.51-15.el7?arch=x86_64&distro=centos-7.9.2009
    "centos": "rpm",
    # trivy image --format cyclonedx --output fedora.json fedora:latest
    # pkg:rpm/fedora/alternatives@1.33-1.fc42?arch=x86_64&distro=fedora-42
    "fedora": "rpm",
    # trivy image --format cyclonedx --output oracle.json oraclelinux:9
    # pkg:rpm/oracle/acl@2.3.1-4.el9?arch=x86_64&distro=oracle-9.6
    "oracle": "rpm",
    # trivy image --format cyclonedx --output redhat.json registry.access.redhat.com/ubi9/ubi:latest
    # pkg:rpm/redhat/acl@2.3.1-4.el9?arch=x86_64&distro=redhat-9.6
    "redhat": "rpm",
    # trivy image --format cyclonedx --output rocky.json rockylinux:9
    # pkg:rpm/rocky/alternatives@1.24-1.el9?arch=x86_64&distro=rocky-9.3
    "rocky": "rpm",
    # SUSE-based distributions
    # trivy image --format cyclonedx --pkg-types os --output opensuse.json opensuse/archive:latest
    # pkg:rpm/opensuse/aaa_base@13.2%2Bgit20140911.61c1681-28.9.1?arch=x86_64&distro=opensuse-leap-42.3
    "opensuse": "rpm",
    # trivy image --format cyclonedx --output opensuse-leap.json opensuse/leap:latest
    # pkg:rpm/opensuse/aaa_base@84.87%2Bgit20180409.04c9dae-150300.10.28.2?arch=x86_64&distro=opensuse-leap-15.6
    "opensuse-leap": "rpm",
    # trivy image --format cyclonedx --output opensuse-tumbleweed.json opensuse/tumbleweed:latest
    # pkg:rpm/opensuse/aaa_base@84.87%2Bgit20250429.1cad3bc-1.1?arch=x86_64&distro=opensuse-tumbleweed-20250630
    "opensuse-tumbleweed": "rpm",
    # trivy image --format cyclonedx  --output slem.json registry.suse.com/suse/sle-micro/5.5:latest
    # pkg:rpm/suse/ModemManager@1.18.10-150500.1.2?arch=aarch64&distro=slem-5.5
    "slem": "rpm",
    # trivy image --format cyclonedx --output sles.json registry.suse.com/suse/sle15:latest
    # pkg:rpm/suse/bash-sh@4.4-150400.27.3.2?arch=x86_64&distro=sles-15.7
    "sles": "rpm",
    # Other distributions
    # Official GitHub documentation mentions the use of RPM
    "bottlerocket": "rpm",
    # trivy image --format cyclonedx --output cbl-mariner.json mcr.microsoft.com/cbl-mariner/base/core:2.0
    # pkg:rpm/cbl-mariner/bzip2-libs@1.0.8-1.cm2?arch=x86_64&distro=cbl-mariner-2.0
    "cbl-mariner": "rpm",
    # trivy image --format cyclonedx  --output chainguard.json chainguard/static
    # pkg:apk/wolfi/tzdata@2025b-r1?arch=x86_64&distro=20230201
    "chainguard": "apk",
    # Echo is a Debian-based container image
    "echo": "deb",
    # Minimos SBOM is the same as Alpine
    "minimos": "apk",
    # trivy image --format cyclonedx --output photon.json photon:latest
    # pkg:rpm/photon/ca-certificates-pki@20230315-6.ph5?arch=x86_64&distro=photon-5.0
    "photon": "rpm",
    # trivy image --format cyclonedx  --output wolfi.json chainguard/wolfi-base
    # pkg:apk/wolfi/ca-certificates-bundle@20241121-r42?arch=x86_64&distro=20230201
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
