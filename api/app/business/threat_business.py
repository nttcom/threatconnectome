from sqlalchemy.orm import Session

from app import models, persistence
from app.business import ticket_business
from app.detector import vulnerability_detector


def fix_threat_by_vuln(db: Session, vuln: models.Vuln) -> list[models.Threat]:
    new_threats: list[models.Threat] = []
    for affect in vuln.affects:
        new_threats.extend(_fix_threat_by_affect(db, affect, vuln.vuln_id))

    return new_threats


def _fix_threat_by_affect(db: Session, affect: models.Affect, vuln_id: str) -> list[models.Threat]:
    new_threats: list[models.Threat] = []
    for package_version in affect.package.package_versions:
        if vulnerability_detector.check_matched_package_version_and_affect(package_version, affect):
            if not (
                threat := persistence.get_threat_by_package_version_id_and_vuln_id(
                    db, package_version.package_version_id, vuln_id
                )
            ):
                threat = models.Threat(
                    package_version_id=package_version.package_version_id, vuln_id=vuln_id
                )
                persistence.create_threat(db, threat)
            new_threats.append(threat)

    return new_threats


def fix_threat_for_dependency(db: Session, dependency: models.Dependency):
    matched_vuln_ids: list[str] = vulnerability_detector.detect_vulnerability_by_dependency(
        db, dependency
    )
    for vuln_id in matched_vuln_ids:
        threat = _get_or_create_threat(db, dependency.package_version.package_version_id, vuln_id)
        ticket_business.fix_ticket_by_threat(db, threat)


def _get_or_create_threat(db: Session, package_version_id: str, vuln_id: str) -> models.Threat:
    if not (
        threat := persistence.get_threat_by_package_version_id_and_vuln_id(
            db, package_version_id, vuln_id
        )
    ):
        threat = models.Threat(package_version_id=package_version_id, vuln_id=vuln_id)
    return threat
