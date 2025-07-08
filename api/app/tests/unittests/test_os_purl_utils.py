"""
Unit tests for os_purl_utils.py module.

This module tests the functionality for identifying OS-related Package URLs.
"""

import pytest
from packageurl import PackageURL

from app.sbom.parser.os_purl_utils import is_os_purl


class TestOsPurlUtils:

    def test_it_should_return_false_when_input_is_none(self):

        # Given
        input_value = None

        # When
        result = is_os_purl(input_value)

        # Then
        assert result is False

    def test_it_should_return_true_for_apk_package_type(self):

        # Given
        purl = PackageURL.from_string("pkg:apk/alpine/alpine-keys@2.5-r0?arch=x86_64&distro=3.22.0")

        # When
        result = is_os_purl(purl)

        # Then
        assert result is True

    def test_it_should_return_true_for_deb_package_type(self):
        # Given
        purl = PackageURL.from_string("pkg:deb/ubuntu/apt@2.8.3?arch=amd64&distro=ubuntu-24.04")

        # When
        result = is_os_purl(purl)

        # Then
        assert result is True

    def test_it_should_return_true_for_rpm_package_type(self):
        # Given
        purl = PackageURL.from_string(
            "pkg:rpm/rocky/alternatives@1.24-1.el9?arch=x86_64&distro=rocky-9.3"
        )

        # When
        result = is_os_purl(purl)

        # Then
        assert result is True

    @pytest.mark.parametrize(
        "purl_str",
        [
            "pkg:npm/web@0.1.0",
            "pkg:pypi/markupsafe@2.0.1",
            "pkg:golang/github.com/chai2010/gettext-go@v1.0.2",
        ],
    )
    def test_it_should_return_false_for_non_os_package_types(self, purl_str: str):
        # Given
        purl = PackageURL.from_string(purl_str)

        # When
        result = is_os_purl(purl)

        # Then
        assert result is False
        assert result is False
