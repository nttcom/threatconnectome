from sqlalchemy.orm import Session

from app import models, persistence
from app.detector import vulnerability_detector


def fix_threat_by_vuln(db: Session, vuln: models.Vuln) -> list[models.Threat]:
    _delete_threat_by_vuln_when_all_affects_unmatch(db, vuln)

    threats: list[models.Threat] = []
    for affect in vuln.affects:
        threats.extend(_fix_threat_by_affect(db, affect))

    return threats


def _fix_threat_by_affect(db: Session, affect: models.Affect) -> list[models.Threat]:
    threats: list[models.Threat] = []
    for package_version in affect.package.package_versions:
        if threat := _fix_threat_for_package_version_and_affect(db, package_version, affect):
            threats.append(threat)

    return threats


def fix_threat_by_package_version_id(db: Session, package_version_id: str) -> list[models.Threat]:
    if not (package_version := persistence.get_package_version_by_id(db, package_version_id)):
        return []

    affects = persistence.get_affect_by_package_id(db, package_version.package_id)
    vulns: set[models.Vuln] = set()
    for affect in affects:
        vulns.add(affect.vuln)
    for vuln in vulns:
        _delete_threat_by_vuln_when_all_affects_unmatch(db, vuln)

    threats: list[models.Threat] = []
    for affect in affects:
        if threat := _fix_threat_for_package_version_and_affect(db, package_version, affect):
            threats.append(threat)

    return threats


def _fix_threat_for_package_version_and_affect(
    db: Session, package_version: models.PackageVersion, affect: models.Affect
) -> models.Threat | None:
    matched = vulnerability_detector.check_matched_package_version_and_affect(
        package_version, affect
    )

    if threat := persistence.get_threat_by_package_version_id_and_vuln_id(
        db, package_version.package_version_id, affect.vuln.vuln_id
    ):
        if matched:
            return threat
    else:
        if matched:
            threat = models.Threat(
                package_version_id=package_version.package_version_id,
                vuln_id=affect.vuln.vuln_id,
            )
            persistence.create_threat(db, threat)
            return threat

    return None


def _delete_threat_by_vuln_when_all_affects_unmatch(db: Session, vuln: models.Vuln):
    for threat in vuln.threats:
        if all(
            not vulnerability_detector.check_matched_package_version_and_affect(
                threat.package_version, affect
            )
            for affect in vuln.affects
        ):
            persistence.delete_threat(db, threat)
