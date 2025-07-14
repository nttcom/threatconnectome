import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import package_business
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
    USER2,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
)


@pytest.fixture(scope="function")
def service1(testdb: Session) -> models.Service:
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service = models.Service(
        service_id="test-service-id",
        service_name="TestService",
        pteam_id=pteam1.pteam_id,
    )
    testdb.add(service)
    testdb.flush()
    return service


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
    user2 = create_user(USER2)
    vuln = models.Vuln(
        vuln_id="test-vuln-id",
        title="Test Vulnerability",
        detail="This is a test vulnerability.",
        cvss_v3_score=7.5,
        created_by=user2.user_id,
        created_at="2023-10-01T00:00:00Z",
        updated_at="2023-10-01T00:00:00Z",
    )
    persistence.create_vuln(testdb, vuln)
    return vuln


class TestFixPackage:
    def test_it_should_delete_package_when_has_no_reference(
        self,
        testdb: Session,
        package1: models.Package,
    ) -> None:
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            version="1.0.0",
            package_id=package1.package_id,
        )
        testdb.add(package_version)
        testdb.flush()

        package_business.fix_package(db=testdb, package=package1)

        assert (
            testdb.execute(
                select(models.PackageVersion).where(
                    models.PackageVersion.package_version_id == package_version.package_version_id
                )
            ).first()
            is None
        )
        assert (
            testdb.execute(
                select(models.Package).where(models.Package.package_id == package1.package_id)
            ).first()
            is None
        )

    def test_it_should_not_delete_package_when_has_dependency(
        self,
        testdb: Session,
        service1: models.Service,
        package1: models.Package,
    ) -> None:
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            version="1.0.0",
            package_id=package1.package_id,
        )
        testdb.add(package_version)
        testdb.flush()

        dependency1 = models.Dependency(
            dependency_id="test-dependency-id",
            target="test-target",
            package_manager="npm",
            package_version_id=package_version.package_version_id,
            service=service1,
        )
        testdb.add(dependency1)
        testdb.flush()

        package_business.fix_package(db=testdb, package=package1)

        assert (
            testdb.execute(
                select(models.PackageVersion).where(
                    models.PackageVersion.package_version_id == package_version.package_version_id
                )
            ).first()
            is not None
        )
        assert (
            testdb.execute(
                select(models.Package).where(models.Package.package_id == package1.package_id)
            ).first()
            is not None
        )

    def test_it_should_delete_package_and_delete_package_version_when_related_affect(
        self,
        testdb: Session,
        package1: models.Package,
        vuln1: models.Vuln,
    ) -> None:
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            version="1.0.0",
            package_id=package1.package_id,
        )
        testdb.add(package_version)
        testdb.flush()

        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        testdb.add(affect)
        testdb.flush()

        package_business.fix_package(db=testdb, package=package1)

        assert (
            testdb.execute(
                select(models.PackageVersion).where(
                    models.PackageVersion.package_version_id == package_version.package_version_id
                )
            ).first()
            is None
        )
        assert (
            testdb.execute(
                select(models.Package).where(models.Package.package_id == package1.package_id)
            ).first()
            is None
        )
