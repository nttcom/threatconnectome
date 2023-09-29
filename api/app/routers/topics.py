import os
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, token_scheme
from app.common import (
    auto_close_by_topic,
    calculate_topic_content_fingerprint,
    check_pteam_membership,
    check_topic_action_tags_integrity,
    check_zone_accessible,
    create_action_internal,
    fix_current_status_by_deleted_topic,
    fix_current_status_by_topic,
    get_misp_tag,
    search_topics,
    update_zones,
    validate_action,
    validate_pteam,
    validate_tag,
    validate_topic,
    validate_zone,
)
from app.database import get_db
from app.slack import alert_new_topic

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=List[schemas.TopicEntry])
def get_topics(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all topics.

    content_fingerprint are calculated as below:

        data = {
            "title": topic.title,
            "abstract": topic.abstract,
            "threat_impact": topic.threat_impact,
            "tag_names": sorted({tag.tag_name for tag in topic.tags}),
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    """
    return search_topics(db, current_user.user_id)


# TODO: This endpoint should be merged into get_topics after implementing pagination
@router.get("/search", response_model=List[schemas.TopicEntry])
def search_topics_(
    title_words: Optional[List[str]] = Query(None),
    abstract_words: Optional[List[str]] = Query(None),
    threat_impacts: Optional[List[int]] = Query(None),
    misp_tag_ids: Optional[List[UUID]] = Query(None),
    tag_ids: Optional[List[UUID]] = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[models.Topic]:
    """
    Search topics with following parameters.

    - title_words
    - abstract_words
    - threat_impacts
    - misp_tag_ids
    - tag_ids

    Different parameters are AND conditions.
    Within the same parameter,
    you can specify multiple OR conditions by separating them with commas.
    The string search is based on the standard PostgreSQL search.
    """
    return search_topics(
        db,
        current_user.user_id,
        title_words=title_words,
        abstract_words=abstract_words,
        threat_impacts=threat_impacts,
        misp_tag_ids=misp_tag_ids,
        tag_ids=tag_ids,
    )


@router.get("/fetch_fs/{topic_id}", response_model=schemas.FsTopicSummary)
def fetch_data_from_flashsense(
    topic_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(token_scheme),
    current_user: models.Account = Depends(get_current_user),
):
    """
    Fetch a specified topic data from flashsense.
    """
    fs_api = os.environ["FLASHSENSE_API_URL"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token.credentials}",
    }
    try:
        response = requests.get(f"{fs_api}/topics/{topic_id}", headers=headers, timeout=30)
    except requests.exceptions.Timeout as flashsense_timeout:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to flashsense",
        ) from flashsense_timeout

    if response.status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic id")
    fs_topic = response.json()

    try:
        response = requests.get(
            f"{fs_api}/messages/{fs_topic['abstract']}", headers=headers, timeout=30
        )
        fs_abstract = response.json().get("text", "") if response.status_code == 200 else ""
    except requests.exceptions.Timeout:
        fs_abstract = ""

    return schemas.FsTopicSummary(abstract=fs_abstract, actions=fs_topic["actions"])


@router.get("/{topic_id}", response_model=schemas.TopicResponse)
def get_topic(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a topic.
    """
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND, ignore_disabled=True)
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)
    return topic


@router.post("/{topic_id}", response_model=schemas.TopicCreateResponse)
def create_topic(
    topic_id: UUID,
    data: schemas.TopicCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a topic.
    - `threat_impact` : The value is in 1, 2, 3, 4.
      (immediate: 1, off-cycle: 2, acceptable: 3, none: 4)
    - `tags` : Optional. The default is an empty list.
    - `misp_tags` : Optional. The default is an empty list.
    - `actions` : Optional. The default is an empty list.
    """
    # TODO: It may be unnecessary to check
    if topic_id == UUID(int=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create default topic"
        )
    if validate_topic(db, topic_id, ignore_disabled=True) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Topic already exists")

    # check tags
    action_tag_names = {tag for action in data.actions for tag in action.ext.get("tags", [])}
    requested_tags: Dict[str, Optional[models.Tag]] = {
        tag_name: validate_tag(db, tag_name=tag_name)
        for tag_name in set(data.tags) | action_tag_names
    }
    if not_exist_tag_names := [tag_name for tag_name, tag in requested_tags.items() if tag is None]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No such tags: {', '.join(sorted(not_exist_tag_names))}",
        )
    check_topic_action_tags_integrity(
        data.tags,
        list(action_tag_names),
        on_error=status.HTTP_400_BAD_REQUEST,
    )

    # check zones
    for zone_str in {zone_name for action in data.actions or [] for zone_name in action.zone_names}:
        validate_zone(  # looks redundant but need check before commit something
            db,
            current_user.user_id,
            zone_str,
            on_error=status.HTTP_400_BAD_REQUEST,
            auth_mode="apply",
            on_auth_error=status.HTTP_400_BAD_REQUEST,
            on_archived=status.HTTP_400_BAD_REQUEST,
        )

    # check actions
    action_ids = [action.action_id for action in data.actions if action.action_id]
    if len(action_ids) != len(set(action_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ambiguous action ids",
        )
    for action_id in action_ids:
        if validate_action(db, action_id) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action id already exists",
            )
    if any(action.topic_id != topic_id for action in data.actions if action.topic_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TopicId in actions mismatch",
        )

    # create topic core
    now = datetime.now()
    topic = models.Topic(
        topic_id=str(topic_id),
        title=data.title.strip(),
        abstract=data.abstract.strip(),
        threat_impact=data.threat_impact,
        created_by=current_user.user_id,
        created_at=now,
        updated_at=now,
        content_fingerprint=calculate_topic_content_fingerprint(
            data.title, data.abstract, data.threat_impact, data.tags
        ),
    )
    # fix relations
    topic.tags = [requested_tags[tag_name] for tag_name in set(data.tags)]
    topic.misp_tags = [get_misp_tag(db, tag) for tag in set(data.misp_tags)]
    topic.zones = update_zones(db, current_user.user_id, True, [], data.zone_names)

    db.add(topic)
    db.commit()
    db.refresh(topic)

    # create and bind actions -- needs active topic_id
    for action in data.actions:
        del action.topic_id
        create_action_internal(
            db,
            current_user,
            schemas.ActionCreateRequest(**action.model_dump(), topic_id=UUID(topic.topic_id)),
        )
    db.refresh(topic)

    auto_close_by_topic(db, topic)
    fix_current_status_by_topic(db, topic)

    alert_new_topic(db, topic)

    return topic


@router.put("/{topic_id}", response_model=schemas.TopicResponse)
def update_topic(
    topic_id: UUID,
    data: schemas.TopicUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a topic.
    """
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND, ignore_disabled=True)
    assert topic

    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)

    if topic.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not topic creator",
        )

    # If the topic is already zoned, it cannot be returned to public status.
    is_request_to_clear_all_existing_zones = (
        len(topic.zones) >= 1
        and data.zone_names == []
        and update_zones(db, current_user.user_id, False, topic.zones, []) == []
    )
    if is_request_to_clear_all_existing_zones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Once a topic has been zoned, it cannot be returned to public status. "
                "Consider deleting and recreating the topic."
            ),
        )

    need_update_content_fingerprint = False
    if (
        data.title not in {None, topic.title}
        or data.abstract not in {None, topic.abstract}
        or data.threat_impact not in {None, topic.threat_impact}
        or (data.tags is not None and set(data.tags) != {tag.tag_name for tag in topic.tags})
    ):
        need_update_content_fingerprint = True

    need_auto_close = (data.disabled is False and topic.disabled is True) or (
        data.zone_names and set(data.zone_names) - {z.zone_name for z in topic.zones}
    )

    # Update topic attributes

    if data.tags is not None:
        tags_dict: Dict[str, Optional[models.Tag]] = {
            tag_name: validate_tag(db, tag_name=tag_name) for tag_name in set(data.tags)
        }
        if not_exist_tag_names := [tag_name for tag_name, tag in tags_dict.items() if tag is None]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No such tags: {', '.join(sorted(not_exist_tag_names))}",
            )
        topic.tags = list(tags_dict.values())

    if data.misp_tags is not None:
        topic.misp_tags = [get_misp_tag(db, tag) for tag in data.misp_tags]

    if data.zone_names is not None:
        topic.zones = update_zones(
            db,
            current_user.user_id,
            False,
            topic.zones,
            data.zone_names,
        )
    # Other fields are not needed to be adjusted
    if data.title is not None:
        topic.title = data.title
    if data.abstract is not None:
        topic.abstract = data.abstract
    if data.threat_impact is not None:
        topic.threat_impact = data.threat_impact
    if data.disabled is not None:
        topic.disabled = data.disabled

    if need_update_content_fingerprint:
        topic.content_fingerprint = calculate_topic_content_fingerprint(
            topic.title, topic.abstract, topic.threat_impact, [tag.tag_name for tag in topic.tags]
        )

    topic.updated_at = datetime.now()
    db.add(topic)
    db.commit()
    db.refresh(topic)

    if need_auto_close:
        auto_close_by_topic(db, topic)
    fix_current_status_by_topic(db, topic)

    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a topic and related records except actionlog and secbadge.
    """
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)

    if topic.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not topic creator",
        )

    db.delete(topic)
    db.commit()

    fix_current_status_by_deleted_topic(db, topic.topic_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{topic_id}/actions/pteam/{pteam_id}", response_model=schemas.TopicActionsResponse)
def get_topic_actions(
    topic_id: UUID,
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actions list of the topic for specified pteam.
    """
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    # If there is no common zones between topic and pteam, access is not permitted.
    if len(topic.zones) > 0 and not set(topic.zones) & set(pteam.zones):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic id")

    pteam_zones = db.query(
        models.PTeamZone.zone_name,
    ).filter(
        models.PTeamZone.pteam_id == str(pteam_id),
    )  # Query, not subquery

    action_ids = (
        db.query(
            models.TopicAction.action_id,
        )
        .filter(
            models.TopicAction.topic_id == str(topic_id),
        )
        .subquery()
    )

    actions_accessible_from_pteam = (
        db.query(
            models.TopicAction,
        )
        .join(action_ids, action_ids.c.action_id == models.TopicAction.action_id)
        .outerjoin(
            models.ActionZone,
            and_(
                models.TopicAction.topic_id == str(topic_id),
                models.ActionZone.action_id == models.TopicAction.action_id,
            ),
        )
        .filter(
            or_(
                models.ActionZone.zone_name.is_(None),
                models.ActionZone.zone_name.in_(pteam_zones),
            ),
        )
        .all()
    )

    return {
        "topic_id": topic_id,
        "pteam_id": pteam_id,
        "actions": actions_accessible_from_pteam,
    }
