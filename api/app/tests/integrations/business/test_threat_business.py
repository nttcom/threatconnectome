import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import threat_business
from app.tests.medium.constants import (
    USER1,
)
from app.tests.medium.utils import (
    create_user,
)


@pytest.fixture(scope="function")
def package1(testdb: Session) -> models.Package:
    package = models.Package(
        package_id="test-package-id",
        name="TestPackage",
        ecosystem="npm",
    )
    persistence.create_package(testdb, package)
    return package


@pytest.fixture(scope="function")
def vuln1(testdb: Session) -> models.Vuln:
    user1 = create_user(USER1)
    vuln = models.Vuln(
        vuln_id="test-vuln-id",
        title="Test Vulnerability",
        detail="This is a test vulnerability.",
        cvss_v3_score=7.5,
        created_by=user1.user_id,
        created_at="2023-10-01T00:00:00Z",
        updated_at="2023-10-01T00:00:00Z",
    )
    persistence.create_vuln(testdb, vuln)
    return vuln


class TestFixThreatByVuln:
    def test_it_should_create_threat_when_version_matched(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)

        # When
        threats = threat_business.fix_threat_by_vuln(testdb, vuln1)

        # Then
        assert len(threats) == 1
        assert testdb.scalars(
            select(models.Threat).where(models.Threat.threat_id == threats[0].threat_id)
        ).one_or_none()

    def test_it_should_delete_threat_when_version_unmatched(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="2.0.0",
            package=package1,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)
        persistence.create_threat(testdb, threat)

        # When
        threats = threat_business.fix_threat_by_vuln(testdb, vuln1)

        # Then
        assert len(threats) == 0
        threat_in_db = testdb.scalars(
            select(models.Threat).where(
                models.Threat.package_version_id == package_version.package_version_id,
                models.Threat.vuln_id == vuln1.vuln_id,
            )
        ).all()
        assert len(threat_in_db) == 0


class TestFixThreatByPackageVersionId:
    def test_it_should_create_threat_when_version_matched(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)

        # When
        threats = threat_business.fix_threat_by_package_version_id(
            testdb, package_version.package_version_id
        )

        # Then
        assert len(threats) == 1
        assert testdb.scalars(
            select(models.Threat).where(models.Threat.threat_id == threats[0].threat_id)
        ).one_or_none()

    def test_it_should_create_threat_when_version_matched_with_source_name(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package2 = models.OSPackage(
            package_id="test-package-id2",
            name="TestPackage2",
            source_name="TestPackageSourceName2",
            ecosystem="alpine-3.22.1",
        )
        persistence.create_package(testdb, package2)

        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package2.package_id,
            version="1.0.0",
            package=package2,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package2.source_name,
            ecosystem="alpine-3.22",
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)

        # When
        threats = threat_business.fix_threat_by_package_version_id(
            testdb, package_version.package_version_id
        )

        # Then
        assert len(threats) == 1
        assert testdb.scalars(
            select(models.Threat).where(models.Threat.threat_id == threats[0].threat_id)
        ).one_or_none()

    def test_it_should_create_threat_when_version_matched_with_alpine(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package2 = models.OSPackage(
            package_id="test-package-id2",
            name="TestPackage2",
            source_name="TestPackageSourceName2",
            ecosystem="ubuntu",
        )
        persistence.create_package(testdb, package2)

        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package2.package_id,
            version="1.0.0",
            package=package2,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package2.source_name,
            ecosystem=package2.ecosystem,
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)

        # When
        threats = threat_business.fix_threat_by_package_version_id(
            testdb, package_version.package_version_id
        )

        # Then
        assert len(threats) == 1
        assert testdb.scalars(
            select(models.Threat).where(models.Threat.threat_id == threats[0].threat_id)
        ).one_or_none()

    def test_it_should_delete_threat_when_version_unmatched(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="2.0.0",
            package=package1,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)
        persistence.create_threat(testdb, threat)
        # When
        threats = threat_business.fix_threat_by_package_version_id(
            testdb, package_version.package_version_id
        )
        # Then
        assert len(threats) == 0
        threat_in_db = testdb.scalars(
            select(models.Threat).where(
                models.Threat.package_version_id == package_version.package_version_id,
                models.Threat.vuln_id == vuln1.vuln_id,
            )
        ).all()
        assert len(threat_in_db) == 0


class TestDeleteThreatByVulnWhemAllAffectsUnmatch:
    def test_it_should_delete_threat_when_affect_removed(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_threat(testdb, threat)

        # When
        threat_business._delete_threat_by_vuln_when_all_affects_unmatch(testdb, vuln1)

        # Then
        threat_in_db = testdb.scalars(
            select(models.Threat).where(models.Threat.vuln_id == vuln1.vuln_id)
        ).all()
        assert len(threat_in_db) == 0

    def test_it_should_not_delete_threat_when_affect_exists(
        self, testdb: Session, package1: models.Package, vuln1: models.Vuln
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_package_version(testdb, package_version)
        persistence.create_affect(testdb, affect)
        persistence.create_threat(testdb, threat)

        # When
        threat_business._delete_threat_by_vuln_when_all_affects_unmatch(testdb, vuln1)
        # Then
        threat_in_db = testdb.scalars(
            select(models.Threat).where(models.Threat.vuln_id == vuln1.vuln_id)
        ).all()
        assert len(threat_in_db) == 1
