from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID


def check_pteam_auth(
    db: Session,
    pteam: models.PTeam,
    user: models.Account,
    required: models.PTeamAuthIntFlag,
) -> bool:
    if user.user_id == str(SYSTEM_UUID):
        return True

    user_auth = persistence.get_pteam_authority(db, pteam.pteam_id, user.user_id)
    int_auth = int(user_auth.authority) if user_auth else 0
    # append auth via pseudo-users
    if not_member_auth := persistence.get_pteam_authority(db, pteam.pteam_id, NOT_MEMBER_UUID):
        int_auth |= not_member_auth.authority
    if user in pteam.members and (
        member_auth := persistence.get_pteam_authority(db, pteam.pteam_id, MEMBER_UUID)
    ):
        int_auth |= member_auth.authority

    return int_auth & required == required


def check_ateam_auth(
    db: Session,
    ateam: models.ATeam,
    user: models.Account,
    required: models.ATeamAuthIntFlag,
) -> bool:
    if user.user_id == str(SYSTEM_UUID):
        return True

    user_auth = persistence.get_ateam_authority(db, ateam.ateam_id, user.user_id)
    int_auth = int(user_auth.authority) if user_auth else 0
    # append auth via pseudo-users
    if not_member_auth := persistence.get_ateam_authority(db, ateam.ateam_id, NOT_MEMBER_UUID):
        int_auth |= not_member_auth.authority
    if user in ateam.members and (
        member_auth := persistence.get_ateam_authority(db, ateam.ateam_id, MEMBER_UUID)
    ):
        int_auth |= member_auth.authority

    return int_auth & required == required


def check_and_get_account(
    db: Session,
    user_id: UUID | str,
) -> models.Account:
    if not (user := persistence.get_account_by_id(db, user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    return user
