from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.detector import vulnerability_detector


def fix_threat_for_create_vuln(db: Session, vuln: models.Vuln):
    matched_package_version_ids: list[str] = vulnerability_detector.detect_vulnerability_by_vuln(
        vuln
    )

    for package_version_id in matched_package_version_ids:
        dependencies = persistence.get_dependencies_from_package_version_id(db, package_version_id)
        for dependency in dependencies:
            _create_threat(db, dependency.dependency_id, package_version_id, vuln.vuln_id)


def fix_threat_for_create_dependency(db: Session, dependency: models.Dependency):
    matched_vuln_ids: list[str] = vulnerability_detector.detect_vulnerability_by_dependency(
        db, dependency
    )
    for vuln_id in matched_vuln_ids:
        _create_threat(
            db, dependency.dependency_id, dependency.package_version.package_version_id, vuln_id
        )


def _create_threat(db: Session, dependency_id: str, package_version_id: str, vuln_id: str):
    threat = models.Threat(package_version_id=package_version_id, vuln_id=vuln_id)
    persistence.create_threat(db, threat)
    ticket_business.fix_ticket_by_threat(db, threat, dependency_id)
