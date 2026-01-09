from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth import api_key
from app.auth.account import get_current_user
from app.business.eol import eol_business
from app.database import get_db

router = APIRouter(prefix="/eols", tags=["eols"])

NO_SUCH_EOL = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such eol")


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
