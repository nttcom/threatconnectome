from sqlalchemy.orm import Session

from app import models, persistence


def fix_package(db: Session, package: models.Package) -> None:
    for package_version in package.package_versions:
        if len(package_version.dependencies) > 0:
            return
    if len(package.affects) > 0:
        return
    persistence.delete_package(db, package)
