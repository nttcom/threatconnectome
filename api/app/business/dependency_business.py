from uuid import UUID

from sqlalchemy.orm import Session

from app import models, persistence


def get_dependencies_by_service(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    package_version_id: UUID | str | None = None,
) -> list[models.Dependency]:
    if package_version_id is not None:
        return list(
            persistence.get_dependencies_from_service_id_and_package_version_id(
                db, service.service_id, package_version_id
            )
        )
    if package_id is not None:
        return list(
            persistence.get_dependencies_from_service_id_and_package_id(
                db, service.service_id, package_id
            )
        )
    return service.dependencies


def has_dependency_by_service(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
    package_version_id: UUID | str | None = None,
) -> bool:
    if package_version_id is not None:
        return persistence.exists_dependency_from_service_id_and_package_version_id(
            db, service.service_id, package_version_id
        )
    if package_id is not None:
        return persistence.exists_dependency_from_service_id_and_package_id(
            db, service.service_id, package_id
        )
    return bool(service.dependencies)
