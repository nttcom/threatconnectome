"""
Unit tests for os_pkgtype_utils.py module.

This module tests the functionality for identifying OS-related package types.
"""

import pytest

from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser


class TestOsPkgtypeUtils:

    def test_it_should_return_false_when_input_is_none(self):
        # Given
        input_value = None

        # When
        result = TrivyCDXParser.CDXComponent._is_os_pkgtype(input_value)

        # Then
        assert result is False

    @pytest.mark.parametrize(
        "pkg_type",
        [
            "alpine",
            "ubuntu",
            "rocky",
        ],
    )
    def test_it_should_return_true_for_os_package_types(self, pkg_type: str):
        # Given - pkg_type from parametrize

        # When
        result = TrivyCDXParser.CDXComponent._is_os_pkgtype(pkg_type)

        # Then
        assert result is True

    @pytest.mark.parametrize(
        "pkg_type",
        [
            "npm",
            "pypi",
            "golang",
            "maven",
            "nuget",
            "composer",
            "cargo",
            "gem",
        ],
    )
    def test_it_should_return_false_for_non_os_package_types(self, pkg_type: str):
        # Given - pkg_type from parametrize

        # When
        result = TrivyCDXParser.CDXComponent._is_os_pkgtype(pkg_type)

        # Then
        assert result is False
