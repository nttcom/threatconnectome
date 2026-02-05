from sqlalchemy.orm import Session

from app import models, persistence
from app.business.eol import ecosystem_eol_business, package_eol_business
from app.notification import alert
from app.notification.eol_notification_utils import is_within_eol_warning


def fix_eol_dependency_by_eol_product(db: Session, eol_product: models.EoLProduct) -> None:
    if eol_product.is_ecosystem:
        ecosystem_eol_business.fix_ecosystem_eol_dependency_by_eol_product(db, eol_product)
    else:
        package_eol_business.fix_package_eol_dependency_by_eol_product(db, eol_product)


def fix_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    _delete_eol_dependency_by_service(db, service)

    related_eol_version_id = set()

    eol_products = persistence.get_all_eol_products(db)
    for dependency in service.dependencies:
        package_version = dependency.package_version
        for eol_product in eol_products:
            if eol_product.is_ecosystem:
                for eol_version in eol_product.eol_versions:
                    if (
                        eol_version.matching_version
                        == package_version.package.vuln_matching_ecosystem
                    ):
                        related_eol_version_id.add(eol_version.eol_version_id)
            else:
                package_eol_business.fix_package_eol_dependency_by_package_version_and_eol_product(
                    db, dependency.dependency_id, package_version, eol_product
                )

    for eol_version_id in related_eol_version_id:
        # Create ecosystem EoL dependency and notify immediately if created
        ecosystem_eol_dependency = (
            ecosystem_eol_business.create_ecosystem_eol_dependency_if_not_exists(
                db, eol_version_id, service.service_id
            )
        )
        if ecosystem_eol_dependency:
            try:
                # eol_version_id refers to eol_version above; fetch date via object on dependency
                if is_within_eol_warning(ecosystem_eol_dependency.eol_version.eol_from):
                    notification_sent = alert.notify_eol_ecosystem(ecosystem_eol_dependency)
                    if notification_sent:
                        ecosystem_eol_dependency.eol_notification_sent = True
            except Exception:
                pass

    db.flush()


def _delete_eol_dependency_by_service(db: Session, service: models.Service) -> None:
    ecosystem_eol_business.delete_eol_dependency_by_service(db, service)

    for dependency in service.dependencies:
        package_eol_business.delete_eol_dependency_by_dependency(db, dependency)
