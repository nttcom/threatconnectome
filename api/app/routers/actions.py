from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.business import ticket_business
from app.database import get_db

router = APIRouter(prefix="/actions", tags=["actions"])


NO_SUCH_ACTION = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic action")


@router.post("", response_model=schemas.ActionResponse)
def create_action(
    request: schemas.ActionCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a vuln action.
    """
    if not request.vuln_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing vuln_id")
    if not (vuln := persistence.get_vuln_by_id(db, request.vuln_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such vuln")

    now = datetime.now()
    action = models.VulnAction(
        # vuln_id will be filled at appending to vuln.vuln_actions
        action=request.action,
        action_type=request.action_type,
        recommended=request.recommended,
        created_at=now,
    )
    vuln.vuln_actions.append(action)
    db.flush()

    for threat in vuln.threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    db.commit()

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
    if not (action := persistence.get_action_by_id(db, action_id)):
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
    if not (action := persistence.get_action_by_id(db, action_id)):
        raise NO_SUCH_ACTION
    update_data = data.model_dump(exclude_unset=True)
    if "action" in update_data.keys() and data.action is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for action",
        )
    if "action_type" in update_data.keys() and data.action_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for action_type",
        )
    if "recommended" in update_data.keys() and data.recommended is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for recommended",
        )
    if "ext" in update_data.keys() and data.ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for ext",
        )
    if data.ext:
        # TODO Provisional Processing
        # if not_exist_tags := {
        #     tag_name
        #     for tag_name in data.ext.get("tags", [])
        #     if not persistence.get_tag_by_name(db, tag_name)
        # }:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"No such tags: {', '.join(sorted(not_exist_tags))}",
        #     )

        # TODO Provisional Processing
        # if not check_topic_action_tags_integrity(action.topic.tags, data.ext.get("tags")):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Action Tag mismatch with Topic Tag",
        #     )
        pass

    for key, value in data:
        if value is None:
            continue
        else:
            setattr(action, key, value)

    # Note:
    #   do not try auto close topic because core of action should be immutable

    db.commit()

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
    if not (action := persistence.get_action_by_id(db, action_id)):
        raise NO_SUCH_ACTION

    topic = action.topic
    persistence.delete_action(db, action)

    # TODO Provisional Processing
    # fix_threats_for_topic(db, topic)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
