from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import api_key
from app.auth.account import get_current_user
from app.database import get_db

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


@router.get("/", response_model=schemas.EoLProductListResponse)
def get_eol_products(
    pteam_id: UUID | None = Query(None, description="PTeam ID (optional)"),
    eol_product_id: UUID | None = Query(None, description="EoL Product ID (optional)"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get EoL products and their versions.
    Can be filtered by pteam_id and/or eol_product_id (both optional).
    """
    # Check if pteam exists when pteam_id is specified
    if pteam_id is not None:
        if not persistence.get_pteam_by_id(db, pteam_id):
            raise NO_SUCH_PTEAM

    # Check if eol_product exists when eol_product_id is specified
    if eol_product_id is not None:
        if not persistence.get_eol_product_by_id(db, eol_product_id):
            raise NO_SUCH_EOL

    result = command.get_eol_products(db, pteam_id, eol_product_id)

    # Format response with eol_versions
    products_response = []
    for product in result["products"]:
        products_response.append(_create_eol_response(product))

    return schemas.EoLProductListResponse(total=result["num_products"], products=products_response)


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
