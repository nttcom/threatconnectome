from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user, token_scheme, verify_id_token
from app.database import get_db

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
    token: HTTPAuthorizationCredentials = Depends(token_scheme),
    db: Session = Depends(get_db),
):
    """
    Create a user.
    """
    user_info = verify_id_token(token)
    uid = user_info.uid
    email = user_info.email
    # if user_info.email is empty, get email from auth provider data
    if email is None:
        if len(user_info.provider_data) > 0:
            email = user_info.provider_data[0].email

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested Email information could not be retrieved.",
        )

    if persistence.get_account_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used")

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
    Delete current user.
    """

    # delete all related objects  # FIXME: should deleted on cascade
    command.workaround_delete_team_authes_by_user_id(db, current_user.user_id)

    for log in current_user.action_logs:
        # actoin logs shoud not be deleted, but should be anonymized
        log.user_id = None

    persistence.delete_account(db, current_user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
