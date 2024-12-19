from sqlalchemy.orm import Session

from app import models, persistence


def check_pteam_membership(pteam: models.PTeam | None, user: models.Account | None) -> bool:
    if not pteam or not user:
        return False
    if user in pteam.members:
        return True
    return False


def check_pteam_auth(
    db: Session,
    pteam: models.PTeam,
    user: models.Account,
) -> bool:
    account_role = persistence.get_pteam_account_role(db, pteam.pteam_id, user.user_id)
    if account_role is not None and account_role.is_admin is True:
        return True
    else:
        return False
