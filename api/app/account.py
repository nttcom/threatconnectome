from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import persistence
from app.auth.auth_module import AuthModule, get_auth_module, token_scheme

from .database import get_db
from .models import Account


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(token_scheme),
    auth_module: AuthModule = Depends(get_auth_module),
    db: Session = Depends(get_db),
) -> Account:
    uid, email = auth_module.check_and_get_user_info(token)
    user = persistence.get_account_by_uid(db, uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user",
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user
