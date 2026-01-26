from sqlalchemy.orm import Session

from app import command, models
from app.business.eol import ecosystem_eol_business, package_eol_business
from app.notification import alert


def fix_eol_dependency_by_eol_product(db: Session, eol_product: models.EoLProduct) -> None:
    if eol_product.is_ecosystem:
        ecosystem_eol_business.fix_ecosystem_eol_dependency_by_eol_product(db, eol_product)
    else:
        package_eol_business.fix_package_eol_dependency_by_eol_product(db, eol_product)


def fix_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    _delete_eol_dependency_by_service(db, service)

    related_eol_version_id = set()

    for dependency in service.dependencies:
        package_version = dependency.package_version
        eol_versions = command.get_related_eol_versions_by_package_version(db, package_version)
        for eol_version in eol_versions:
            if eol_version.eol_product.is_ecosystem:
                related_eol_version_id.add(eol_version.eol_version_id)
            else:
                # Create package EoL dependency and notify immediately if created
                package_eol_dependency = (
                    package_eol_business.create_package_eol_dependency_if_not_exists(
                        db, eol_version.eol_version_id, dependency.dependency_id
                    )
                )
                if package_eol_dependency:
                    try:
                        notification_sent = alert.notify_eol_package(package_eol_dependency)
                        if notification_sent:
                            package_eol_dependency.eol_notification_sent = True
                    except Exception:
                        pass
                        db.flush()  # Ensure the change is persisted

    for eol_version_id in related_eol_version_id:
        # Create ecosystem EoL dependency and notify immediately if created
        ecosystem_eol_dependency = (
            ecosystem_eol_business.create_ecosystem_eol_dependency_if_not_exists(
                db, eol_version_id, service.service_id
            )
        )
        if ecosystem_eol_dependency:
            try:
                notification_sent = alert.notify_eol_ecosystem(ecosystem_eol_dependency)
                if notification_sent:
                    ecosystem_eol_dependency.eol_notification_sent = True
            except Exception:
                pass  # Keep eol_notification_sent as False
                db.flush()  # Ensure the change is persisted


def _delete_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    ecosystem_eol_business.delete_eol_dependency_by_service(db, service)

    for dependency in service.dependencies:
        package_eol_business.delete_eol_dependency_by_dependency(db, dependency)
