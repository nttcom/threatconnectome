import pytest

from app import models


class TestVulnMatchingEcosystem:
    @pytest.mark.parametrize(
        "ecosystem, package_type, expected",
        [
            ("alpine-3.22.0", "OS", "alpine-3.22"),
            ("alpine-3", "OS", "alpine-3"),
            ("alpine-test-3.22.0", "OS", "alpine-test-3.22.0"),
            ("alpine", "OS", "alpine"),
            ("ubuntu-20.04", "OS", "ubuntu-20.04"),
        ],
    )
    def test_it_should_return_expected_value_for_os_package(
        self, ecosystem: str, package_type: str, expected: str
    ):
        # Given
        os_package = models.OSPackage(
            name="test_package", ecosystem=ecosystem, source_name="test_source_name_package"
        )

        # Then
        assert os_package.vuln_matching_ecosystem == expected

    @pytest.mark.parametrize(
        "ecosystem, package_type, expected",
        [
            ("npm", "LANG", "npm"),
            ("pypi", "LANG", "pypi"),
        ],
    )
    def test_it_should_return_expected_value_for_lang_package(
        self, ecosystem: str, package_type: str, expected: str
    ):
        # Given
        lang_package = models.LangPackage(name="test_package", ecosystem=ecosystem)

        # Then
        assert lang_package.vuln_matching_ecosystem == expected
