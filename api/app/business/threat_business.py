from sqlalchemy.orm import Session

from app import models, persistence
from app.detector import vulnerability_detector


def fix_threat_by_vuln(db: Session, vuln: models.Vuln) -> list[models.Threat]:
    new_threats: list[models.Threat] = []
    for affect in vuln.affects:
        new_threats.extend(_fix_threat_by_affect(db, affect, vuln.vuln_id))

    return new_threats


def _fix_threat_by_affect(db: Session, affect: models.Affect, vuln_id: str) -> list[models.Threat]:
    new_threats: list[models.Threat] = []
    for package_version in affect.package.package_versions:
        if _check_need_threat(db, package_version, affect):
            threat = models.Threat(
                package_version_id=package_version.package_version_id, vuln_id=affect.vuln.vuln_id
            )
            persistence.create_threat(db, threat)
            new_threats.append(threat)

    return new_threats


def fix_threat_for_package_version_id(db: Session, package_version_id: str) -> list[models.Threat]:
    if not (package_version := persistence.get_package_version_by_id(db, package_version_id)):
        return []

    affects = persistence.get_affect_by_package_id(db, package_version.package_id)

    new_threats: list[models.Threat] = []
    for affect in affects:
        if _check_need_threat(db, package_version, affect):
            threat = models.Threat(
                package_version_id=package_version.package_version_id, vuln_id=affect.vuln.vuln_id
            )
            persistence.create_threat(db, threat)
            new_threats.append(threat)

    return new_threats


def _check_need_threat(
    db: Session, package_version: models.PackageVersion, affect: models.Affect
) -> bool:
    if not vulnerability_detector.check_matched_package_version_and_affect(package_version, affect):
        return False

    threat = persistence.get_threat_by_package_version_id_and_vuln_id(
        db, package_version.package_version_id, affect.vuln.vuln_id
    )
    return threat is None
