import pytest
from sqlalchemy.orm import Session

from app import models


class TestPackageTable:
    class TestVulnMatchingEcosystem:
        @pytest.mark.parametrize(
            "ecosystem, expected",
            [
                ("alpine-3.22.0", "alpine-3.22"),
                ("alpine-3", "alpine-3"),
                ("alpine-test-3.22.0", "alpine-test-3.22.0"),
                ("alpine", "alpine"),
                ("ubuntu-20.04", "ubuntu-20.04"),
                ("rocky-9.3", "rocky-9"),
                ("rocky-8.7", "rocky-8"),
                ("rocky-9", "rocky-9"),
                ("rocky", "rocky"),
                ("rocky-test-9.3", "rocky-test-9.3"),
            ],
        )
        def test_it_should_return_expected_value_for_os_package(
            self, ecosystem: str, expected: str
        ):
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
        def test_it_should_return_expected_value_for_lang_package(
            self, ecosystem: str, expected: str
        ):
            # Given
            lang_package = models.LangPackage(name="test_package", ecosystem=ecosystem)

            # Then
            assert lang_package.vuln_matching_ecosystem == expected

    class TestUniqueConstraint:
        def test_unique_constraint_violation_when_name_ecosystem_same_and_source_name_is_null(
            self, testdb: Session
        ):
            # Given
            os_package_1 = models.OSPackage(
                name="test_package", ecosystem="alpine-3.22", source_name=None
            )
            os_package_2 = models.OSPackage(
                name="test_package", ecosystem="alpine-3.22", source_name=None
            )
            testdb.add(os_package_1)
            testdb.commit()

            # When
            with pytest.raises(Exception) as excinfo:
                testdb.add(os_package_2)
                testdb.commit()

            # Then
            assert (
                "duplicate key value violates unique "
                'constraint "package_name_ecosystem_source_name_key"' in str(excinfo.value)
            )
