from app import models, persistence
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from sqlalchemy.orm import Session


def check_pteam_membership(
    db: Session,
    pteam: models.PTeam | None,
    user: models.Account | None,
    ignore_ateam: bool = False,
) -> bool:
    if not pteam or not user:
        return False
    if user.user_id == str(SYSTEM_UUID):
        return True
    if user in pteam.members:
        return True
    if ignore_ateam:
        return False
    # check if a member of ateam which watches the pteam
    if any(user in ateam.members for ateam in pteam.ateams):
        return True
    return False


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


def check_ateam_membership(
    ateam: models.ATeam | None,
    user: models.Account | None,
) -> bool:
    if not ateam or not user:
        return False
    if user.user_id == str(SYSTEM_UUID):
        return True
    if user in ateam.members:
        return True
    return False


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
