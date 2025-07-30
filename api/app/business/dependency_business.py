from uuid import UUID

from sqlalchemy.orm import Session

from app import models, persistence


def get_dependencies_by_service(
    db: Session,
    service: models.Service,
    package_id: UUID | str | None,
) -> list[models.Dependency]:
    if package_id:
        return list(
            persistence.get_dependencies_from_service_id_and_package_id(
                db, service.service_id, package_id
            )
        )
    else:
        return service.dependencies
