from sqlalchemy.orm import Session

from app import command, models, persistence
from app.notification import alert


def fix_ecosystem_eol_dependency_by_eol_product(
    db: Session, eol_product: models.EoLProduct
) -> None:
    for eol_version in eol_product.eol_versions:
        _delete_not_match_ecosystem_eol_dependency(db, eol_version)

        package_versions = command.get_related_package_versions_by_eol_version(
            db, eol_product, eol_version
        )
        related_services = set()
        for package_version in package_versions:
            for dependency in package_version.dependencies:
                related_services.add(dependency.service)

        for service in related_services:
            # Create ecosystem EoL dependency and notify immediately if created
            ecosystem_eol_dependency = create_ecosystem_eol_dependency_if_not_exists(
                db, eol_version.eol_version_id, service.service_id
            )
            if ecosystem_eol_dependency:
                notification_sent = alert.notify_eol_ecosystem(ecosystem_eol_dependency)
                if notification_sent:
                    ecosystem_eol_dependency.eol_notification_sent = True


def create_ecosystem_eol_dependency_if_not_exists(
    db: Session, eol_version_id: str, service_id: str
) -> models.EcosystemEoLDependency | None:
    ecosystem_eol_dependency = (
        persistence.get_ecosystem_eol_dependency_by_eol_version_id_and_service_id(
            db,
            eol_version_id,
            service_id,
        )
    )
    if not ecosystem_eol_dependency:
        ecosystem_eol_dependency = models.EcosystemEoLDependency(
            eol_version_id=eol_version_id,
            service_id=service_id,
            eol_notification_sent=False,
        )
        persistence.create_ecosystem_eol_dependency(db, ecosystem_eol_dependency)
        return ecosystem_eol_dependency
    return None


def _delete_not_match_ecosystem_eol_dependency(db: Session, eol_version: models.EoLVersion) -> None:
    _delete_not_match_ecosystem_eol_dependency_by_ecosystem_eol_dependencies(
        db, eol_version.ecosystem_eol_dependencies
    )


def delete_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    _delete_not_match_ecosystem_eol_dependency_by_ecosystem_eol_dependencies(
        db, service.ecosystem_eol_dependencies
    )


def _delete_not_match_ecosystem_eol_dependency_by_ecosystem_eol_dependencies(
    db: Session,
    ecosystem_eol_dependencies: list[models.EcosystemEoLDependency],
) -> None:
    delete_ecosystem_eol_dependencies = []
    for ecosystem_eol_dependency in ecosystem_eol_dependencies:
        if not _check_match_any_dependencies(
            ecosystem_eol_dependency, ecosystem_eol_dependency.eol_version
        ):
            delete_ecosystem_eol_dependencies.append(ecosystem_eol_dependency)

    for ecosystem_eol_dependency in delete_ecosystem_eol_dependencies:
        persistence.delete_ecosystem_eol_dependency(db, ecosystem_eol_dependency)


def _check_match_any_dependencies(ecosystem_eol_dependency, eol_version):
    for dependency in ecosystem_eol_dependency.service.dependencies:
        if (
            dependency.package_version.package.vuln_matching_ecosystem
            == eol_version.matching_version
        ):
            return True

    return False
