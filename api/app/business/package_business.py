from sqlalchemy.orm import Session

from app import persistence


def fix_package_by_package_version_id(db: Session, package_version_id: str) -> None:
    if not (package_version := persistence.get_package_version_by_id(db, package_version_id)):
        return
    if not (package := persistence.get_package_by_id(db, package_version.package_id)):
        return
    affects = persistence.get_affect_by_package_id(db, package.package_id)
    if len(affects) > 0:
        return
    persistence.delete_package(db, package)
