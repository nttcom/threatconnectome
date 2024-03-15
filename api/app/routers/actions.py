from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    auto_close_by_topic,
    check_tags_exist,
    check_topic_action_tags_integrity,
    create_action_internal,
    validate_action,
)
from app.database import get_db

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("", response_model=schemas.ActionResponse)
def create_action(
    data: schemas.ActionCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a topic action.
    """
    if not data.topic_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing topic_id",
        )
    if data.action_id and validate_action(db, data.action_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action id already exists",
        )
    check_tags_exist(db, data.ext.get("tags", []))
    action = create_action_internal(db, current_user, data)

    auto_close_by_topic(db, action.topic)

    return action


@router.get("/{action_id}", response_model=schemas.ActionResponse)
def get_action(
    action_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a topic action.
    """
    action = validate_action(db, action_id, on_error=status.HTTP_404_NOT_FOUND)
    assert action
    return action


@router.put("/{action_id}", response_model=schemas.ActionResponse)
def update_action(
    action_id: UUID,
    data: schemas.ActionUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a topic action.
    """
    action = validate_action(db, action_id, on_error=status.HTTP_404_NOT_FOUND)
    assert action
    if data.ext:
        check_topic_action_tags_integrity(
            action.topic.tags,
            data.ext.get("tags"),
            on_error=status.HTTP_400_BAD_REQUEST,
        )

    for key, value in data:
        if value is None:
            continue
        elif key == "ext":
            check_tags_exist(db, value.get("tags", []))
            setattr(action, key, value)
        else:
            setattr(action, key, value)

    # Note:
    #   do not try auto close topic because core of action should be immutable

    db.add(action)
    db.commit()
    db.refresh(action)

    return action


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action(
    action_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a topic action.
    """
    action = validate_action(db, action_id, on_error=status.HTTP_404_NOT_FOUND)
    assert action
    topic = action.topic

    db.delete(action)
    db.commit()

    # try auto close because deleted action could block closing
    auto_close_by_topic(db, topic)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
