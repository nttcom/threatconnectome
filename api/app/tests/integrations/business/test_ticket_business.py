import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
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


class TestFixTicketByThreat:
    def test_it_should_create_ticket_when_has_fixed_versions(
        self,
        testdb: Session,
        service1: models.Service,
        package1: models.Package,
        vuln1: models.Vuln,
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        persistence.create_package_version(testdb, package_version)

        dependency1 = models.Dependency(
            dependency_id="test-dependency-id",
            target="test-target",
            package_manager="npm",
            package_version_id=package_version.package_version_id,
            service=service1,
        )
        testdb.add(dependency1)
        testdb.flush()

        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=["2.0.0"],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        persistence.create_affect(testdb, affect)

        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_threat(testdb, threat)

        # When
        ticket_business.fix_ticket_by_threat(testdb, threat)

        # Then
        ticket = testdb.scalars(
            select(models.Ticket).where(models.Ticket.threat_id == threat.threat_id)
        ).one_or_none()
        assert ticket

    def test_it_should_delete_ticket_when_not_need_ticket(
        self,
        testdb: Session,
        service1: models.Service,
        package1: models.Package,
        vuln1: models.Vuln,
    ):
        # Given
        package_version = models.PackageVersion(
            package_version_id="test-package-version-id",
            package_id=package1.package_id,
            version="1.0.0",
            package=package1,
        )
        persistence.create_package_version(testdb, package_version)

        dependency1 = models.Dependency(
            dependency_id="test-dependency-id",
            target="test-target",
            package_manager="npm",
            package_version_id=package_version.package_version_id,
            service=service1,
        )
        testdb.add(dependency1)
        testdb.flush()

        affect = models.Affect(
            vuln_id=vuln1.vuln_id,
            affected_versions=["<=1.0.0"],
            fixed_versions=[],
            affected_name=package1.name,
            ecosystem=package1.ecosystem,
        )
        persistence.create_affect(testdb, affect)

        threat = models.Threat(
            package_version_id=package_version.package_version_id, vuln_id=vuln1.vuln_id
        )
        persistence.create_threat(testdb, threat)

        ticket = models.Ticket(
            threat_id=threat.threat_id,
            dependency_id=dependency1.dependency_id,
            threat=threat,
            dependency=dependency1,
        )
        persistence.create_ticket(testdb, ticket)

        # When
        ticket_business.fix_ticket_by_threat(testdb, threat)

        # Then
        selected_ticket = testdb.scalars(
            select(models.Ticket).where(models.Ticket.threat_id == threat.threat_id)
        ).one_or_none()
        assert selected_ticket is None
