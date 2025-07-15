import pytest
from sqlalchemy import (
    select,
)

from app import models, persistence


class TestVulnMatchingEcosystemForSqlQuery:
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
    def test_it_should_return_expected_value_for_os_package(
        self, testdb, ecosystem: str, expected: str
    ):
        # Given
        os_package = models.OSPackage(
            name="test_package", ecosystem=ecosystem, source_name="test_source_name_package"
        )
        persistence.create_package(testdb, os_package)

        # When
        query = select(models.Package.vuln_matching_ecosystem_for_sql_query)
        vuln_matching_ecosystem = testdb.scalars(query).one_or_none()

        # Given
        assert vuln_matching_ecosystem == expected

    @pytest.mark.parametrize(
        "ecosystem, expected",
        [
            ("npm", "npm"),
            ("pypi", "pypi"),
        ],
    )
    def test_it_should_return_expected_value_for_lang_package(
        self, testdb, ecosystem: str, expected: str
    ):
        # Given
        lang_package = models.LangPackage(name="test_package", ecosystem=ecosystem)
        persistence.create_package(testdb, lang_package)

        # When
        query = select(models.Package.vuln_matching_ecosystem_for_sql_query)
        vuln_matching_ecosystem = testdb.scalars(query).one_or_none()

        # Given
        assert vuln_matching_ecosystem == expected
