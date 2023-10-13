from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.common import (
    check_pteam_auth,
    create_secbadge_internal,
    validate_secbadge,
    validate_secbadge_metadata_internal,
)
from app.database import get_db
from app.models import Account, PTeamAuthIntFlag, SecBadge
from app.schemas import BadgeRequest, SecBadgeBody

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.post("/metadata", status_code=status.HTTP_204_NO_CONTENT)
def validate_secbadge_metadata(metadata: Dict[str, Any], db: Session = Depends(get_db)):
    return validate_secbadge_metadata_internal(metadata, db)


@router.get("/{user_id}", response_model=List[SecBadgeBody])
def get_secbadges(
    user_id: UUID, current_user: Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get only security badges based on the user ID.
    """
    account = db.query(Account).filter(Account.user_id == str(user_id)).one_or_none()
    if not account:
        return []
    return (
        db.query(SecBadge)
        .filter(SecBadge.user_id == account.user_id)
        .order_by(desc(SecBadge.created_at))
        .all()
    )


@router.post("", response_model=SecBadgeBody)
def create_secbadge(
    data: BadgeRequest,
    current_user: Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Issue a security badge for the given userID and badge's metadata.

    `priority` is optional, the default is `100`.

    `difficulty` is optional, the default is `low`.
    """
    return create_secbadge_internal(data, current_user, db)


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_secbadge(
    badge_id: UUID, current_user: Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete a specified security badge.
    """
    secbadge_data = validate_secbadge(db, badge_id, on_error=status.HTTP_404_NOT_FOUND)
    assert secbadge_data
    if current_user.user_id not in (secbadge_data.user_id, secbadge_data.created_by):
        check_pteam_auth(
            db,
            secbadge_data.pteam_id,
            current_user.user_id,
            PTeamAuthIntFlag.PTEAMBADGE_MANAGE,
            on_error=status.HTTP_403_FORBIDDEN,
        )
    db.delete(secbadge_data)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header
