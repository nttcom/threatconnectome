from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, persistence
from app.auth import api_key
from app.auth.account import get_current_user
from app.database import get_db

router = APIRouter(prefix="/eols", tags=["eols"])

NO_SUCH_EOL = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such eol")


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
