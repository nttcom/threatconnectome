from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.auth.auth_exception import AuthException
from app.auth.auth_module import AuthModule, get_auth_module
from app.database import get_db
from app.routers.utils.http_excption_creator import create_http_exception
from app.routers.validators.account_validator import (
    check_pteam_membership,
)

router = APIRouter(prefix="/users", tags=["users"])

NOT_A_PTEAM_MEMBER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not a pteam member",
)


@router.get("/me", response_model=schemas.UserResponse)
def get_my_user_info(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current user info.
    """

    return schemas.UserResponse(
        user_id=UUID(current_user.user_id),
        uid=current_user.uid,
        email=current_user.email,
        disabled=current_user.disabled,
        years=current_user.years,
        pteam_roles=current_user.pteam_roles,
        default_pteam_id=(
            UUID(current_user.account_default_pteam.default_pteam_id)
            if current_user.account_default_pteam
            else None
        ),
    )


@router.post("", response_model=schemas.UserResponse)
def create_user(
    data: schemas.UserCreateRequest,
    request: Request,
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

        # store uid in request.state for logging in middleware
        request.state.uid = uid
    except AuthException as auth_exception:
        raise create_http_exception(auth_exception)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested Email information could not be retrieved.",
        )

    if persistence.get_account_by_uid(db, uid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uid already used")

    if len(persistence.get_accounts_by_email(db, email)) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This email address is already in use. "
                "You'll need to use a different email to sign up."
            ),
        )

    account = models.Account(**data.model_dump(), uid=uid, email=email)
    persistence.create_account(db, account)

    db.commit()
    db.refresh(account)

    return schemas.UserResponse(
        user_id=UUID(account.user_id),
        uid=account.uid,
        email=account.email,
        disabled=account.disabled,
        years=account.years,
        pteam_roles=account.pteam_roles,
        default_pteam_id=None,
    )


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
    if data.default_pteam_id is not None:
        if (pteam := persistence.get_pteam_by_id(db, data.default_pteam_id)) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pteam_id does not exist",
            )

        if not check_pteam_membership(pteam, current_user):
            raise NOT_A_PTEAM_MEMBER

        if (
            account_default_pteam := persistence.get_account_default_pteam_by_user_id(db, user_id)
        ) is not None:
            account_default_pteam.default_pteam_id = str(data.default_pteam_id)
        else:
            account_default_pteam = models.AccountDefaultPTeam(
                user_id=user.user_id,
                default_pteam_id=data.default_pteam_id,
            )
            persistence.create_account_default_pteam(db, account_default_pteam)

    elif "default_pteam_id" in update_data.keys() and data.default_pteam_id is None:
        if (
            account_default_pteam := persistence.get_account_default_pteam_by_user_id(db, user_id)
        ) is not None:
            persistence.delete_account_default_pteam(db, account_default_pteam)

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

    return schemas.UserResponse(
        user_id=UUID(user.user_id),
        uid=user.uid,
        email=user.email,
        disabled=user.disabled,
        years=user.years,
        pteam_roles=current_user.pteam_roles,
        default_pteam_id=(
            UUID(current_user.account_default_pteam.default_pteam_id)
            if current_user.account_default_pteam
            else None
        ),
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: models.Account = Depends(get_current_user),
    auth_module: AuthModule = Depends(get_auth_module),
    db: Session = Depends(get_db),
):
    """
    Delete current user and left admin-less pteams.
    """

    for log in current_user.action_logs:
        # action logs should not be deleted, but should be anonymized
        log.user_id = None
        log.email = ""

    db.flush()

    # Current_user.user_id should be removed from the assignees of the ticket status.

    def having_only_one_admin(pteam: models.PTeam):
        return len(list(filter(lambda x: x.is_admin is True, pteam.pteam_roles))) == 1

    for delete_target in [
        role.pteam
        for role in current_user.pteam_roles
        if role.is_admin and having_only_one_admin(role.pteam)
    ]:
        persistence.delete_pteam(db, delete_target)

    try:
        persistence.delete_account(db, current_user)
        auth_module.delete_user(current_user.uid)
    except AuthException as auth_exception:
        raise create_http_exception(auth_exception)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
