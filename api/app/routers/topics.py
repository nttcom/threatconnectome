import os
from datetime import datetime
from typing import Dict, List, Optional, Set
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
    get_topics_internal,
    search_topics_internal,
    update_zones,
    validate_action,
    validate_misp_tag,
    validate_pteam,
    validate_zone,
)
from app.database import get_db
from app.repository.tag import TagRepository
from app.repository.topic import TopicRepository
from app.slack import alert_new_topic

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=List[schemas.TopicEntry])
def get_topics(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all topics.

    content_fingerprint is calculated as below:

        data = {
            "title": topic.title.strip(),
            "abstract": topic.abstract.strip(),
            "threat_impact": topic.threat_impact,
            "tag_names": sorted({tag.tag_name for tag in topic.tags}),
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    """
    return get_topics_internal(db, current_user.user_id)


@router.get("/search", response_model=schemas.SearchTopicsResponse)
def search_topics(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # 10 is default in web/src/pages/TopicManagement.jsx
    sort_key: schemas.TopicSortKey = Query(schemas.TopicSortKey.THREAT_IMPACT),
    threat_impacts: Optional[List[int]] = Query(None),
    topic_ids: Optional[List[str]] = Query(None),
    title_words: Optional[List[str]] = Query(None),
    abstract_words: Optional[List[str]] = Query(None),
    tag_names: Optional[List[str]] = Query(None),
    misp_tag_names: Optional[List[str]] = Query(None),
    zone_names: Optional[List[str]] = Query(None),
    creator_ids: Optional[List[str]] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    updated_after: Optional[datetime] = Query(None),
    updated_before: Optional[datetime] = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search topics by following parameters with sort and pagination.

    - threat_impacts
    - title_words
    - abstract_words
    - tag_names
    - misp_tag_names
    - zone_names
    - created_after
    - created_before
    - updated_after
    - updated_before
    - topic_ids
    - creator_ids

    Zoned topics you cannot access to will not appear in the result.
    Defaults are "" for strings, None for datetimes, both means skip filtering.
    Different parameters are AND conditions.
    Wrong names of tag, misp_tag, zone_name do not cause error, are just ignored.
    The words search is case-insensitive.
    Empty string ("") is a special keyword for empty or public for zone_names.

    Caution: If you do not want to filter by something, DO NOT give the param.

    examples:
      "...?tag_names=" -> search topics which have no tags
      (query does not include misp_tag_words) -> do not filter by misp_tag
      "...?zone_names=zone1&zone_names=" -> zone1 or public
      "...?title_words=a&title_words=%20&title_words=B" -> title includes [aAbB ]
      "...?title_words=a&title_words=&title_words=B" -> title includes [aAbB] or empty
    """
    keyword_for_empty = ""

    fixed_zone_names: Set[Optional[str]] = set()
    if zone_names is not None:
        for zone_name in zone_names:
            if zone_name == keyword_for_empty:
                fixed_zone_names.add(None)
                continue
            if not validate_zone(db, current_user.user_id, zone_name):
                continue  # ignore wrong zone_name
            if not check_zone_accessible(db, current_user.user_id, [zone_name]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have related zone",  # FIXME: fix message with others
                )
            fixed_zone_names.add(zone_name)

    tag_repository = TagRepository(db)
    fixed_tag_ids: Set[Optional[str]] = set()
    if tag_names is not None:
        for tag_name in tag_names:
            if tag_name == keyword_for_empty:
                fixed_tag_ids.add(None)
                continue
            if (tag := tag_repository.get_by_name(tag_name)) is None:
                continue  # ignore wrong tag_name
            fixed_tag_ids.add(tag.tag_id)

    fixed_misp_tag_ids: Set[Optional[str]] = set()
    if misp_tag_names is not None:
        for misp_tag_name in misp_tag_names:
            if misp_tag_name == keyword_for_empty:
                fixed_misp_tag_ids.add(None)
                continue
            if (misp_tag := validate_misp_tag(db, tag_name=misp_tag_name)) is None:
                continue  # ignore wrong misp_tag_name
            fixed_misp_tag_ids.add(misp_tag.tag_id)

    fixed_topic_ids = set()
    if topic_ids is not None:
        for topic_id in topic_ids:
            try:
                UUID(topic_id)
                fixed_topic_ids.add(topic_id)
            except ValueError:
                pass

    fixed_creator_ids = set()
    if creator_ids is not None:
        for creator_id in creator_ids:
            try:
                UUID(creator_id)
                fixed_creator_ids.add(creator_id)
            except ValueError:
                pass

    fixed_title_words: Set[Optional[str]] = set()
    if title_words is not None:
        for title_word in title_words:
            if title_word == keyword_for_empty:
                fixed_title_words.add(None)
                continue
            fixed_title_words.add(title_word)

    fixed_abstract_words: Set[Optional[str]] = set()
    if abstract_words is not None:
        for abstract_word in abstract_words:
            if abstract_word == keyword_for_empty:
                fixed_abstract_words.add(None)
                continue
            fixed_abstract_words.add(abstract_word)

    fixed_threat_impacts: Set[int] = set()
    if threat_impacts is not None:
        for threat_impact in threat_impacts:
            try:
                int_val = int(threat_impact)
                if int_val in {1, 2, 3, 4}:
                    fixed_threat_impacts.add(int_val)
            except ValueError:
                pass

    return search_topics_internal(
        db,
        current_user,
        offset=offset,
        limit=limit,
        sort_key=sort_key,
        threat_impacts=None if threat_impacts is None else list(fixed_threat_impacts),
        title_words=None if title_words is None else list(fixed_title_words),
        abstract_words=None if abstract_words is None else list(fixed_abstract_words),
        tag_ids=None if tag_names is None else list(fixed_tag_ids),
        misp_tag_ids=None if misp_tag_names is None else list(fixed_misp_tag_ids),
        zone_names=None if zone_names is None else list(fixed_zone_names),
        topic_ids=None if topic_ids is None else list(fixed_topic_ids),
        creator_ids=None if creator_ids is None else list(fixed_creator_ids),
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
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
    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

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

    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Topic already exists")

    # check tags
    tag_repository = TagRepository(db)
    action_tag_names = {tag for action in data.actions for tag in action.ext.get("tags", [])}
    requested_tags: Dict[str, Optional[models.Tag]] = {
        tag_name: tag_repository.get_by_name(tag_name)
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

    fixed_title = data.title.strip()
    fixed_abstract = data.abstract.strip()

    # create topic core
    now = datetime.now()
    topic = models.Topic(
        topic_id=str(topic_id),
        title=fixed_title,
        abstract=fixed_abstract,
        threat_impact=data.threat_impact,
        created_by=current_user.user_id,
        created_at=now,
        updated_at=now,
        content_fingerprint=calculate_topic_content_fingerprint(
            fixed_title, fixed_abstract, data.threat_impact, data.tags
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
    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

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

    new_title = None if data.title is None else data.title.strip()
    new_abstract = None if data.abstract is None else data.abstract.strip()
    new_tags: Optional[List[Optional[models.Tag]]] = None
    tag_repository = TagRepository(db)
    if data.tags is not None:
        tags_dict = {
            tag_name: tag_repository.get_by_name(tag_name) for tag_name in set(data.tags or [])
        }
        if not_exist_tag_names := [tag_name for tag_name, tag in tags_dict.items() if tag is None]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No such tags: {', '.join(sorted(not_exist_tag_names))}",
            )
        new_tags = list(tags_dict.values())
    new_zones = (
        None
        if data.zone_names is None
        else update_zones(
            db,
            current_user.user_id,
            False,
            topic.zones,
            data.zone_names,
        )
    )
    tags_updated = new_tags is not None and set(new_tags) != set(topic.tags)
    zones_updated = new_zones is not None and set(new_zones) != set(topic.zones)

    need_update_content_fingerprint = (
        new_title not in {None, topic.title}
        or new_abstract not in {None, topic.abstract}
        or data.threat_impact not in {None, topic.threat_impact}
        or tags_updated
    )
    need_auto_close = (
        (data.disabled is False and topic.disabled is True)
        or tags_updated  # Note: since the causes which prevent auto-close can be removed,
        or zones_updated  #      not only adding but also deleting should trigger auto-close
    )

    # Update topic attributes
    if new_tags is not None:
        topic.tags = new_tags
    if data.misp_tags is not None:
        topic.misp_tags = [get_misp_tag(db, tag) for tag in data.misp_tags]
    if new_zones is not None:
        topic.zones = new_zones
    if new_title is not None:
        topic.title = new_title
    if new_abstract is not None:
        topic.abstract = new_abstract
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
    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is None or topic.disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

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
def get_pteam_topic_actions(
    topic_id: UUID,
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actions list of the topic for specified pteam.
    """
    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is None or topic.disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")

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


@router.get("/{topic_id}/actions/user/me", response_model=List[schemas.ActionResponse])
def get_user_topic_actions(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actions list of the topic for current user.
    """
    topic_repository = TopicRepository(db)
    topic = topic_repository.get_by_id(topic_id)
    if topic is None or topic.disabled or not check_zone_accessible(db, current_user.user_id, topic.zones):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such topic",
        )

    pteam_zones = (
        db.query(models.PTeamZone.zone_name)
        .filter(
            or_(
                models.PTeamZone.pteam_id.in_(
                    # joined pteams
                    db.query(models.PTeamAccount.pteam_id).filter(
                        models.PTeamAccount.user_id == current_user.user_id
                    )
                ),
                models.PTeamZone.pteam_id.in_(
                    # pteams via joined ateams
                    db.query(models.ATeamPTeam.pteam_id).join(
                        models.ATeamAccount,
                        and_(
                            models.ATeamAccount.user_id == current_user.user_id,
                            models.ATeamAccount.ateam_id == models.ATeamPTeam.ateam_id,
                        ),
                    ),
                ),
            )
        )
        .distinct()
    )
    gteam_zones = db.query(models.Zone.zone_name).join(
        models.GTeamAccount,
        and_(
            models.GTeamAccount.user_id == current_user.user_id,
            models.GTeamAccount.gteam_id == models.Zone.gteam_id,
        ),
    )
    related_action_ids = (
        db.query(
            models.TopicAction.action_id,
        )
        .filter(
            models.TopicAction.topic_id == str(topic_id),
        )
        .subquery()
    )

    actions = (
        db.query(models.TopicAction)
        .join(related_action_ids, related_action_ids.c.action_id == models.TopicAction.action_id)
        .outerjoin(models.ActionZone)
        .filter(
            or_(
                models.ActionZone.zone_name.is_(None),  # public
                models.ActionZone.zone_name.in_(pteam_zones),
                models.ActionZone.zone_name.in_(gteam_zones),
            ),
        )
    ).all()

    return actions
