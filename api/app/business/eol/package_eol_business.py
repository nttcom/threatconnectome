from sqlalchemy.orm import Session

from app import command, models, persistence
from app.business.eol import eol_detector
from app.notification import alert
from app.notification.eol_notification_utils import is_within_eol_warning


def fix_package_eol_dependency_by_eol_product(db: Session, eol_product: models.EoLProduct) -> None:
    for eol_version in eol_product.eol_versions:
        _delete_not_match_package_eol_dependency(db, eol_version)

        package_versions = command.get_related_package_versions_by_eol_version(
            db, eol_product, eol_version
        )
        for package_version in package_versions:
            if not eol_detector.check_matched_package_version_and_eol_version(
                package_version, eol_version
            ):
                continue
            for dependency in package_version.dependencies:
                # Create package EoL dependency and notify immediately if created
                package_eol_dependency = create_package_eol_dependency_if_not_exists(
                    db, eol_version.eol_version_id, dependency.dependency_id
                )
                if package_eol_dependency:
                    try:
                        if is_within_eol_warning(package_eol_dependency.eol_version.eol_from):
                            notification_sent = alert.notify_eol_package(package_eol_dependency)
                            if notification_sent:
                                package_eol_dependency.eol_notification_sent = True
                    except Exception:
                        pass

    db.flush()


def create_package_eol_dependency_if_not_exists(
    db: Session, eol_version_id: str, dependency_id: str
) -> models.PackageEoLDependency | None:
    package_eol_dependency = (
        persistence.get_package_eol_dependency_by_eol_version_id_and_dependency_id(
            db,
            eol_version_id,
            dependency_id,
        )
    )
    if not package_eol_dependency:
        package_eol_dependency = models.PackageEoLDependency(
            eol_version_id=eol_version_id,
            dependency_id=dependency_id,
            eol_notification_sent=False,
        )
        persistence.create_package_eol_dependency(db, package_eol_dependency)
        return package_eol_dependency
    return None


def _delete_not_match_package_eol_dependency(db: Session, eol_version: models.EoLVersion) -> None:
    _delete_not_match_package_eol_dependency_by_package_eol_dependencies(
        db, eol_version.package_eol_dependencies
    )


def delete_eol_dependency_by_dependency(db: Session, dependency: models.Dependency) -> None:
    _delete_not_match_package_eol_dependency_by_package_eol_dependencies(
        db, dependency.package_eol_dependencies
    )


def _delete_not_match_package_eol_dependency_by_package_eol_dependencies(
    db: Session, package_eol_dependencies: list[models.PackageEoLDependency]
) -> None:
    delete_package_eol_dependencies = []
    for package_eol_dependency in package_eol_dependencies:
        eol_version = package_eol_dependency.eol_version
        eol_product = eol_version.eol_product
        package_version = package_eol_dependency.dependency.package_version
        if (
            package_version.package.name == eol_product.matching_name
            and eol_detector.check_matched_package_version_and_eol_version(
                package_version, eol_version
            )
        ):
            continue
        delete_package_eol_dependencies.append(package_eol_dependency)

    for package_eol_dependency in delete_package_eol_dependencies:
        persistence.delete_package_eol_dependency(db, package_eol_dependency)
