from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
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
    decoded_token = verify_id_token(token)
    uid = decoded_token["uid"]
    email = decoded_token["email"]
    if db.query(models.Account).filter(models.Account.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used")
    user = models.Account(uid=uid, email=email, **data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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
    user = db.query(models.Account).filter(models.Account.user_id == str(user_id)).one_or_none()
    if not user or user.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Information can only be updated by user himself",
        )

    # update other user's properties
    if data.disabled is not None:
        user.disabled = data.disabled
    if data.years is not None:
        user.years = data.years

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete current user.
    """

    # Use selectinload to load all related objects
    user = (
        db.query(models.Account)
        .options(
            selectinload(models.Account.action_logs),
        )
        .filter(models.Account.user_id == current_user.user_id)
        .one_or_none()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {current_user.user_id} not found"
        )

    # delete all related objects
    db.query(models.PTeamAuthority).filter(models.PTeamAuthority.user_id == user.user_id).delete()
    db.query(models.ATeamAuthority).filter(models.ATeamAuthority.user_id == user.user_id).delete()

    for log in user.action_logs:
        # actoin logs shoud not be deleted, but should be anonymized
        log.user_id = None

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
