import pytest
from sqlalchemy import (
    select,
)

from app import models, persistence


class TestVulnMatchingEcosystemForSqlQuery:
    @pytest.mark.parametrize(
        "ecosystem, package_type, expected",
        [
            ("alpine-3.22.0", "OS", "alpine-3.22"),
            ("alpine-3", "OS", "alpine-3"),
            ("alpine-test-3.22.0", "OS", "alpine-test-3.22.0"),
            ("alpine", "OS", "alpine"),
            ("ubuntu-20.04", "OS", "ubuntu-20.04"),
            ("npm", "LANG", "npm"),
            ("pypi", "LANG", "pypi"),
        ],
    )
    def test_it_should_return_expected_value_for_vuln_matching_ecosystem_for_sql_query(
        self, testdb, ecosystem: str, package_type: str, expected: str
    ):
        # Given
        if package_type == "OS":
            _os_package = models.OSPackage(
                name="test_package", ecosystem=ecosystem, source_name="test_source_name_package"
            )
            persistence.create_package(testdb, _os_package)
        else:
            _lang_package = models.LangPackage(name="test_package", ecosystem=ecosystem)
            persistence.create_package(testdb, _lang_package)

        # When
        query = select(models.Package.vuln_matching_ecosystem_for_sql_query)
        vuln_matching_ecosystem = testdb.scalars(query).one_or_none()

        # Given
        assert vuln_matching_ecosystem == expected
