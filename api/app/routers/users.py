from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.auth.auth_exception import AuthException
from app.auth.auth_module import AuthModule, get_auth_module
from app.database import get_db
from app.routers.utils.http_excption_creator import create_http_exception

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_my_user_info(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current user info.
    """
    return current_user


@router.post("", response_model=schemas.UserResponse)
def create_user(
    data: schemas.UserCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(scheme_name=None, description=None, auto_error=False)
    ),
    auth_module: AuthModule = Depends(get_auth_module),
    db: Session = Depends(get_db),
):
    """
    Create a user.
    """
    try:
        uid, email = auth_module.check_and_get_user_info(token)
    except AuthException as auth_exception:
        raise create_http_exception(auth_exception)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested Email information could not be retrieved.",
        )

    if persistence.get_account_by_uid(db, uid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uid already used")

    account = models.Account(**data.model_dump(), uid=uid, email=email)
    persistence.create_account(db, account)

    db.commit()

    return account


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: UUID,
    data: schemas.UserUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a user.
    """
    user = persistence.get_account_by_id(db, user_id)
    if not user or user.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Information can only be updated by user himself",
        )

    update_data = data.model_dump(exclude_unset=True)
    if "disabled" in update_data.keys() and data.disabled is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for disabled",
        )
    if "years" in update_data.keys() and data.years is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for years",
        )
    if data.disabled is not None:
        user.disabled = data.disabled
    if data.years is not None:
        user.years = data.years

    db.commit()

    return user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete current user and left admin-less pteams.
    """

    for log in current_user.action_logs:
        # actoin logs shoud not be deleted, but should be anonymized
        log.user_id = (
            None  # Current_user.user_id should be removed from the assignees of the ticket status.
        )

    def having_only_one_admin(pteam: models.PTeam):
        return len(list(filter(lambda x: x.is_admin is True, pteam.pteam_roles))) == 1

    for delete_target in [
        role.pteam
        for role in current_user.pteam_roles
        if role.is_admin and having_only_one_admin(role.pteam)
    ]:
        persistence.delete_pteam(db, delete_target)

    persistence.delete_account(db, current_user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
