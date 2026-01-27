import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth import api_key
from app.auth.account import get_current_user
from app.business.eol import eol_business
from app.database import get_db, open_db_session
from app.eol_constants import EOL_WARNING_THRESHOLD_DAYS
from app.notification.alert import notify_eol_ecosystem, notify_eol_package

router = APIRouter(prefix="/eols", tags=["eols"])

NO_SUCH_EOL = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such eol")
NO_SUCH_PTEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")


def _create_eol_response(eol_product: models.EoLProduct) -> schemas.EoLProductResponse:
    eol_versions = []
    for eol_version in eol_product.eol_versions:
        eol_versions.append(
            schemas.EoLVersionResponse(
                eol_version_id=UUID(eol_version.eol_version_id),
                version=eol_version.version,
                release_date=eol_version.release_date,
                eol_from=eol_version.eol_from,
                matching_version=eol_version.matching_version,
                created_at=eol_version.created_at,
                updated_at=eol_version.updated_at,
            )
        )

    return schemas.EoLProductResponse(
        eol_product_id=UUID(eol_product.eol_product_id),
        name=eol_product.name,
        product_category=eol_product.product_category,
        description=eol_product.description,
        is_ecosystem=eol_product.is_ecosystem,
        matching_name=eol_product.matching_name,
        eol_versions=eol_versions,
    )


@router.get("", response_model=schemas.EoLProductListResponse)
def get_eol_products(
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get EoL products and their versions.
    """
    eol_products = persistence.get_all_eol_products(db)

    return {
        "total": len(eol_products),
        "products": [schemas.EoLProductResponse.model_validate(p) for p in eol_products],
    }


@router.put(
    "/{eol_product_id}",
    response_model=schemas.EoLProductResponse,
    include_in_schema=False,
    dependencies=[Depends(api_key.verify_api_key)],
)
def update_eol(
    eol_product_id: UUID,
    request: schemas.EoLProductRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a eol if it exists,
    or create a new eol if the specified eol_id is not found in the database.
    """
    if not (eol_product := persistence.get_eol_product_by_id(db, eol_product_id)):
        eol_product = __handle_create_eol(eol_product_id, request, db)
    else:
        eol_product = __handle_update_eol(eol_product, request, db)

    db.refresh(eol_product)

    eol_business.fix_eol_dependency_by_eol_product(db, eol_product)

    eol_response = _create_eol_response(eol_product)

    db.commit()

    return eol_response


def __handle_create_eol(
    eol_product_id: UUID,
    request: schemas.EoLProductRequest,
    db: Session,
) -> models.EoLProduct:
    update_request = request.model_dump(exclude_unset=True)
    if (
        ("name" not in update_request.keys())
        or ("product_category" not in update_request.keys())
        or ("is_ecosystem" not in update_request.keys())
        or ("matching_name" not in update_request.keys())
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "'name' and 'product_category' and 'is_ecosystem' and "
                "'matching_name' are required when creating a eol."
            ),
        )

    _check_request_fields(request)

    # create eol product
    eol_product = models.EoLProduct(
        eol_product_id=str(eol_product_id),
        name=request.name,
        product_category=request.product_category,
        description=request.description,
        is_ecosystem=request.is_ecosystem,
        matching_name=request.matching_name,
    )

    persistence.create_eol_product(db, eol_product)

    # create eol versions
    now = datetime.now(timezone.utc)
    for eol_version in request.eol_versions:
        eol_version_model = models.EoLVersion(
            eol_product_id=str(eol_product_id),
            version=eol_version.version,
            release_date=eol_version.release_date,
            eol_from=eol_version.eol_from,
            matching_version=eol_version.matching_version,
            created_at=now,
            updated_at=now,
        )
        persistence.create_eol_version(db, eol_version_model)

    return eol_product


def __handle_update_eol(
    eol_product: models.EoLProduct, request: schemas.EoLProductRequest, db: Session
) -> models.EoLProduct:
    _check_request_fields(request)

    update_request = request.model_dump(exclude_unset=True)
    if "name" in update_request.keys() and request.name is not None:
        eol_product.name = request.name
    if "product_category" in update_request.keys() and request.product_category is not None:
        eol_product.product_category = request.product_category
    if "description" in update_request.keys():
        eol_product.description = request.description
    if "is_ecosystem" in update_request.keys() and request.is_ecosystem is not None:
        eol_product.is_ecosystem = request.is_ecosystem
    if "matching_name" in update_request.keys() and request.matching_name is not None:
        eol_product.matching_name = request.matching_name
    if "eol_versions" in update_request.keys():
        eol_versions_request = [eol_version.version for eol_version in request.eol_versions]
        for eol_version in eol_product.eol_versions:
            if eol_version.version not in eol_versions_request:
                persistence.delete_eol_version(db, eol_version)

        for eol_version in request.eol_versions:
            update_eol_version = eol_version.model_dump(exclude_unset=True)
            now = datetime.now(timezone.utc)
            if (
                persisted_eol_version := _get_eol_version_by_version(
                    eol_product.eol_versions, eol_version.version
                )
            ) is not None:
                if (
                    "release_date" in update_eol_version.keys()
                    and eol_version.release_date is not None
                ):
                    persisted_eol_version.release_date = eol_version.release_date

                if "eol_from" in update_eol_version.keys() and eol_version.eol_from is not None:
                    persisted_eol_version.eol_from = eol_version.eol_from

                if (
                    "matching_version" in update_eol_version.keys()
                    and eol_version.matching_version is not None
                ):
                    persisted_eol_version.matching_version = eol_version.matching_version

                persisted_eol_version.updated_at = now
            else:
                new_eol_version = models.EoLVersion(
                    eol_product_id=eol_product.eol_product_id,
                    version=eol_version.version,
                    release_date=eol_version.release_date,
                    eol_from=eol_version.eol_from,
                    matching_version=eol_version.matching_version,
                    created_at=now,
                    updated_at=now,
                )
                persistence.create_eol_version(db, new_eol_version)
    db.flush()

    return eol_product


def _check_request_fields(request):
    # check eol_product fields
    eol_product_fields_to_check = [
        "name",
        "product_category",
        "is_ecosystem",
        "matching_name",
    ]
    update_request = request.model_dump(exclude_unset=True)
    for field in eol_product_fields_to_check:
        if field in update_request.keys() and getattr(request, field) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot specify None for {field}",
            )


def _get_eol_version_by_version(
    eol_versions: list[models.EoLVersion], version: str
) -> models.EoLVersion | None:
    for eol_version in eol_versions:
        if eol_version.version == version:
            return eol_version
    return None


@router.delete(
    "/{eol_product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
    dependencies=[Depends(api_key.verify_api_key)],
)
def delete_eol(
    eol_product_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a eol.
    """
    if not (eol_product := persistence.get_eol_product_by_id(db, eol_product_id)):
        raise NO_SUCH_EOL

    persistence.delete_eol_product(db, eol_product)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _bg_check_eol_notification() -> None:
    log = logging.getLogger(__name__)
    log.info("Start EOL notification check")

    with open_db_session() as db:
        ecosystem_eol_dependencies = persistence.get_all_ecosystem_eol_dependencies(db)
        for ecosystem_eol_dependency in ecosystem_eol_dependencies:
            if ecosystem_eol_dependency.eol_notification_sent is True:
                continue

            time_until_eol = (
                ecosystem_eol_dependency.eol_version.eol_from - datetime.now(timezone.utc).date()
            )

            if time_until_eol > timedelta(days=EOL_WARNING_THRESHOLD_DAYS):
                continue

            try:
                sent = notify_eol_ecosystem(ecosystem_eol_dependency)
            except Exception as e:
                log.exception(
                    "Failed to send EOL notification for EcosystemEoLDependency (ID: %s): %s",
                    getattr(ecosystem_eol_dependency, "ecosystem_eol_dependency_id", "<unknown>"),
                    e,
                )
                continue

            if sent:
                ecosystem_eol_dependency.eol_notification_sent = True

        package_eol_dependencies = persistence.get_all_package_eol_dependencies(db)
        for package_eol_dependency in package_eol_dependencies:
            if package_eol_dependency.eol_notification_sent is True:
                continue

            time_until_eol = (
                package_eol_dependency.eol_version.eol_from - datetime.now(timezone.utc).date()
            )
            if time_until_eol > timedelta(days=EOL_WARNING_THRESHOLD_DAYS):
                continue

            try:
                sent = notify_eol_package(package_eol_dependency)
            except Exception as e:
                log.exception(
                    "Failed to send EOL notification for PackageEoLDependency (ID: %s): %s",
                    getattr(package_eol_dependency, "package_eol_dependency_id", "<unknown>"),
                    e,
                )
                continue

            if sent:
                package_eol_dependency.eol_notification_sent = True

        db.commit()
        log.info("End EOL notification check")


@router.post(
    "/check_notifications",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
    dependencies=[Depends(api_key.verify_api_key)],
)
async def check_eol_notification(
    background_tasks: BackgroundTasks,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Identify and notify records in EcosystemEoLDependency and PackageEoLDependency
    where EOL is approaching within six months and eol_notification_sent is false.
    """

    background_tasks.add_task(_bg_check_eol_notification)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
