from sqlalchemy.orm import Session

from app import command, models
from app.business.eol import ecosystem_eol_business, package_eol_business


def fix_eol_dependency_by_eol_product(db: Session, eol_product: models.EoLProduct) -> None:
    if eol_product.is_ecosystem:
        ecosystem_eol_business.fix_ecosystem_eol_dependency_by_eol_version(db, eol_product)
    else:
        package_eol_business.fix_package_eol_dependency_by_eol_version(db, eol_product)


def fix_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    _delete_eol_dependency_by_service(db, service)

    related_services = set()
    for dependency in service.dependencies:
        package_version = dependency.package_version
        eol_versions = command.get_related_eol_versions_by_package_version(db, package_version)
        for eol_version in eol_versions:
            if eol_version.eol_product.is_ecosystem:
                related_services.add(dependency.service)
            else:
                package_eol_business.create_package_eol_dependency_if_not_exists(
                    db, eol_version.eol_version_id, dependency.dependency_id
                )

    for service in related_services:
        ecosystem_eol_business.create_ecosystem_eol_dependency_if_not_exists(
            db, eol_version.eol_version_id, service.service_id
        )


def _delete_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    ecosystem_eol_business.delete_eol_dependency_by_service(db, service)

    for dependency in service.dependencies:
        package_eol_business.delete_eol_dependency_by_dependency(db, dependency)
