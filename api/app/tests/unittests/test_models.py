import pytest

from app import models


class TestVulnMatchingEcosystem:
    @pytest.mark.parametrize(
        "ecosystem, expected",
        [
            ("alpine-3.22.0", "alpine-3.22"),
            ("alpine-3", "alpine-3"),
            ("alpine-test-3.22.0", "alpine-test-3.22.0"),
            ("alpine", "alpine"),
            ("ubuntu-20.04", "ubuntu-20.04"),
        ],
    )
    def test_it_should_return_expected_value_for_os_package(self, ecosystem: str, expected: str):
        # Given
        os_package = models.OSPackage(
            name="test_package", ecosystem=ecosystem, source_name="test_source_name_package"
        )

        # Then
        assert os_package.vuln_matching_ecosystem == expected

    @pytest.mark.parametrize(
        "ecosystem, expected",
        [
            ("npm", "npm"),
            ("pypi", "pypi"),
        ],
    )
    def test_it_should_return_expected_value_for_lang_package(self, ecosystem: str, expected: str):
        # Given
        lang_package = models.LangPackage(name="test_package", ecosystem=ecosystem)

        # Then
        assert lang_package.vuln_matching_ecosystem == expected
