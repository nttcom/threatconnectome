from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth import get_current_user
from app.common import (
    auto_close_by_topic,
    check_topic_action_tags_integrity,
)
from app.database import get_db

router = APIRouter(prefix="/actions", tags=["actions"])


NO_SUCH_ACTION = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic action")


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing topic_id")
    if not (topic := persistence.get_topic_by_id(db, data.topic_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such topic")
    if data.action_id and persistence.get_action(db, data.action_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action id already exists",
        )
    if not_exist_tags := {
        tag_name
        for tag_name in data.ext.get("tags", [])
        if not persistence.get_tag_by_name(db, tag_name)
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No such tags: {', '.join(sorted(not_exist_tags))}",
        )
    if not check_topic_action_tags_integrity(topic.tags, data.ext.get("tags")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action Tag mismatch with Topic Tag",
        )

    now = datetime.now()
    action = models.TopicAction(
        action_id=str(data.action_id) if data.action_id else None,
        # topic_id will be filled at appending to topic.actions
        action=data.action,
        action_type=data.action_type,
        recommended=data.recommended,
        ext=data.ext,
        created_by=current_user.user_id,
        created_at=now,
    )
    topic.actions.append(action)
    db.flush()

    auto_close_by_topic(db, action.topic)

    db.commit()
    db.refresh(action)

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
    if not (action := persistence.get_action(db, action_id)):
        raise NO_SUCH_ACTION

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
    if not (action := persistence.get_action(db, action_id)):
        raise NO_SUCH_ACTION
    if data.ext:
        if not_exist_tags := {
            tag_name
            for tag_name in data.ext.get("tags", [])
            if not persistence.get_tag_by_name(db, tag_name)
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No such tags: {', '.join(sorted(not_exist_tags))}",
            )
        if not check_topic_action_tags_integrity(action.topic.tags, data.ext.get("tags")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action Tag mismatch with Topic Tag",
            )

    for key, value in data:
        if value is None:
            continue
        else:
            setattr(action, key, value)

    # Note:
    #   do not try auto close topic because core of action should be immutable

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
    if not (action := persistence.get_action(db, action_id)):
        raise NO_SUCH_ACTION

    topic = action.topic
    persistence.delete_action(db, action)

    # try auto close because deleted action could block closing
    auto_close_by_topic(db, topic)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
