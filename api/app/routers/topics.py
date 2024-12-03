from datetime import datetime
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.business.misp_tag_business import get_or_create_misp_tag
from app.business.tag_business import check_topic_action_tags_integrity
from app.business.ticket_business import ticket_meets_condition_to_create_alert
from app.business.topic_business import (
    calculate_topic_content_fingerprint,
    get_sorted_topics,
)
from app.database import get_db
from app.detector.vulnerability_detector import fix_threats_for_topic
from app.notification.alert import send_alert_to_pteam
from app.routers.validators.account_validator import check_pteam_membership
from app.ssvc import ssvc_calculator

router = APIRouter(prefix="/topics", tags=["topics"])


NO_SUCH_TOPIC = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")


@router.get("", response_model=list[schemas.TopicEntry])
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
    return get_sorted_topics(persistence.get_all_topics(db))


@router.get("/search", response_model=schemas.SearchTopicsResponse)
def search_topics(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # 10 is default in web/src/pages/TopicManagement.jsx
    sort_key: schemas.TopicSortKey = Query(schemas.TopicSortKey.THREAT_IMPACT),
    threat_impacts: list[int] | None = Query(None),
    topic_ids: list[str] | None = Query(None),
    title_words: list[str] | None = Query(None),
    abstract_words: list[str] | None = Query(None),
    tag_names: list[str] | None = Query(None),
    misp_tag_names: list[str] | None = Query(None),
    creator_ids: list[str] | None = Query(None),
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    updated_after: datetime | None = Query(None),
    updated_before: datetime | None = Query(None),
    pteam_id: UUID | None = Query(None),
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
    - created_after
    - created_before
    - updated_after
    - updated_before
    - topic_ids
    - creator_ids

    Defaults are "" for strings, None for datetimes, both means skip filtering.
    Different parameters are AND conditions.
    Wrong names of tag and misp_tag do not cause error, are just ignored.
    The words search is case-insensitive.

    Caution: If you do not want to filter by something, DO NOT give the param.

    examples:
      "...?tag_names=" -> search topics which have no tags
      (query does not include misp_tag_words) -> do not filter by misp_tag
      "...?title_words=a&title_words=%20&title_words=B" -> title includes [aAbB ]
      "...?title_words=a&title_words=&title_words=B" -> title includes [aAbB] or empty
    """
    keyword_for_empty = ""

    fixed_tag_ids: set[str | None] = set()
    if tag_names is not None:
        for tag_name in tag_names:
            if tag_name == keyword_for_empty:
                fixed_tag_ids.add(None)
                continue
            if not (tag := persistence.get_tag_by_name(db, tag_name)):
                continue  # ignore wrong tag_name
            fixed_tag_ids.add(tag.tag_id)

    fixed_misp_tag_ids: set[str | None] = set()
    if misp_tag_names is not None:
        for misp_tag_name in misp_tag_names:
            if misp_tag_name == keyword_for_empty:
                fixed_misp_tag_ids.add(None)
                continue
            if not (misp_tag := persistence.get_misp_tag_by_name(db, misp_tag_name)):
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
            if not persistence.get_account_by_id(db, creator_id):
                continue
            fixed_creator_ids.add(creator_id)

    fixed_title_words: set[str | None] = set()
    if title_words is not None:
        for title_word in title_words:
            if title_word == keyword_for_empty:
                fixed_title_words.add(None)
                continue
            fixed_title_words.add(title_word)

    fixed_abstract_words: set[str | None] = set()
    if abstract_words is not None:
        for abstract_word in abstract_words:
            if abstract_word == keyword_for_empty:
                fixed_abstract_words.add(None)
                continue
            fixed_abstract_words.add(abstract_word)

    fixed_threat_impacts: set[int] = set()
    if threat_impacts is not None:
        for threat_impact in threat_impacts:
            try:
                int_val = int(threat_impact)
                if int_val in {1, 2, 3, 4}:
                    fixed_threat_impacts.add(int_val)
            except ValueError:
                pass

    return command.search_topics_internal(
        db,
        offset=offset,
        limit=limit,
        sort_key=sort_key,
        threat_impacts=None if threat_impacts is None else list(fixed_threat_impacts),
        title_words=None if title_words is None else list(fixed_title_words),
        abstract_words=None if abstract_words is None else list(fixed_abstract_words),
        tag_ids=None if tag_names is None else list(fixed_tag_ids),
        misp_tag_ids=None if misp_tag_names is None else list(fixed_misp_tag_ids),
        topic_ids=None if topic_ids is None else list(fixed_topic_ids),
        creator_ids=None if creator_ids is None else list(fixed_creator_ids),
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        pteam_id=pteam_id,
    )


@router.get("/{topic_id}", response_model=schemas.TopicResponse)
def get_topic(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a topic.
    """
    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC

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
    - `cvss_v3_score` : Ranges from 0.0 to 10.0. -1.0 indicates not set.
    """
    # TODO: It may be unnecessary to check
    if topic_id == UUID(int=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create default topic"
        )
    if persistence.get_topic_by_id(db, topic_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Topic already exists")

    # check tags
    action_tag_names = {tag for action in data.actions for tag in action.ext.get("tags", [])}
    requested_tags: dict[str, models.Tag | None] = {
        tag_name: persistence.get_tag_by_name(db, tag_name)
        for tag_name in set(data.tags) | action_tag_names
    }
    if not_exist_tag_names := [tag_name for tag_name, tag in requested_tags.items() if tag is None]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No such tags: {', '.join(sorted(not_exist_tag_names))}",
        )
    if not check_topic_action_tags_integrity(
        data.tags,
        list(action_tag_names),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action Tag mismatch with Topic Tag",
        )

    # check actions
    action_ids = [action.action_id for action in data.actions if action.action_id]
    if len(action_ids) != len(set(action_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ambiguous action ids",
        )
    for action_id in action_ids:
        if persistence.get_action_by_id(db, action_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action id already exists",
            )
    if any(action.topic_id != topic_id for action in data.actions if action.topic_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TopicId in actions mismatch",
        )

    cvss_v3_score = -1.0 if data.cvss_v3_score is None else data.cvss_v3_score
    if cvss_v3_score > 10.0 or cvss_v3_score < -1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cvss_v3_score is out of range",
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
        cvss_v3_score=cvss_v3_score,
        content_fingerprint=calculate_topic_content_fingerprint(
            fixed_title, fixed_abstract, data.threat_impact, data.tags
        ),
        exploitation=data.exploitation,
        automatable=data.automatable,
    )
    # fix relations
    topic.tags = [requested_tags[tag_name] for tag_name in set(data.tags)]
    topic.misp_tags = [get_or_create_misp_tag(db, tag) for tag in set(data.misp_tags)]
    for action in data.actions:
        new_action = models.TopicAction(
            action_id=str(action.action_id) if action.action_id else None,
            # topic_id will be filled at appending to topic.actions
            action=action.action,
            action_type=action.action_type,
            recommended=action.recommended,
            ext=action.ext,
            created_by=current_user.user_id,
            created_at=now,
        )
        topic.actions.append(new_action)

    persistence.create_topic(db, topic)

    fix_threats_for_topic(db, topic)

    db.commit()

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
    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC
    if topic.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not topic creator",
        )

    new_title = None if data.title is None else data.title.strip()
    new_abstract = None if data.abstract is None else data.abstract.strip()
    new_tags: list[models.Tag | None] | None = None
    if data.tags is not None:
        tags_dict = {
            tag_name: persistence.get_tag_by_name(db, tag_name) for tag_name in set(data.tags or [])
        }
        if not_exist_tag_names := [tag_name for tag_name, tag in tags_dict.items() if tag is None]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No such tags: {', '.join(sorted(not_exist_tag_names))}",
            )
        new_tags = list(tags_dict.values())
    tags_updated = new_tags is not None and set(new_tags) != set(topic.tags)

    new_cvss_v3_score = None if data.cvss_v3_score is None else data.cvss_v3_score
    if new_cvss_v3_score is not None and (new_cvss_v3_score > 10.0 or new_cvss_v3_score < -1.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cvss_v3_score is out of range",
        )

    # Update topic attributes
    if new_tags is not None:
        topic.tags = new_tags
    if data.misp_tags is not None:
        topic.misp_tags = [get_or_create_misp_tag(db, tag) for tag in data.misp_tags]
    if new_title is not None:
        topic.title = new_title
    if new_abstract is not None:
        topic.abstract = new_abstract
    if data.threat_impact is not None:
        topic.threat_impact = data.threat_impact
    if data.exploitation is not None:
        previous_exploitation = topic.exploitation
        topic.exploitation = data.exploitation
    if data.automatable is not None:
        previous_automatable = topic.automatable
        topic.automatable = data.automatable
    if new_cvss_v3_score is not None:
        topic.cvss_v3_score = new_cvss_v3_score

    topic.content_fingerprint = calculate_topic_content_fingerprint(
        topic.title, topic.abstract, topic.threat_impact, [tag.tag_name for tag in topic.tags]
    )

    topic.updated_at = datetime.now()

    db.flush()

    created_ticket_ids: list[str] = []
    if tags_updated:
        created_ticket_ids = fix_threats_for_topic(db, topic)

    # calculate ssvc priority
    if (data.exploitation and data.exploitation != previous_exploitation) or (
        data.automatable and data.automatable != previous_automatable
    ):

        threats: list[models.Threat] = []
        threats.extend(command.search_threats(db, None, None, topic.topic_id))

        now = datetime.now()
        for threat in threats:
            ticket = threat.ticket
            if ticket is not None:
                _ssvc_deployer_priority = ssvc_calculator.calculate_ssvc_priority_by_threat(threat)
                if _ssvc_deployer_priority == ticket.ssvc_deployer_priority:
                    continue
                ticket.ssvc_deployer_priority = _ssvc_deployer_priority

                if (
                    ticket.ticket_id not in created_ticket_ids
                    and ticket_meets_condition_to_create_alert(ticket)
                ):
                    alert = models.Alert(
                        ticket_id=ticket.ticket_id,
                        alerted_at=now,
                        alert_content="",  # alert_content is not used
                    )
                    persistence.create_alert(db, alert)
                    send_alert_to_pteam(alert)

    db.commit()

    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a topic and related records except actionlog.
    """
    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC

    if topic.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not topic creator",
        )

    persistence.delete_topic(db, topic)

    db.commit()

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
    if not (persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
    if not check_pteam_membership(pteam, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")

    # Note: no limitations currently, thus return all topic actions
    actions = persistence.get_actions_by_topic_id(db, topic_id)

    return {
        "topic_id": topic_id,
        "pteam_id": pteam_id,
        "actions": actions,
    }


@router.get("/{topic_id}/actions/user/me", response_model=Sequence[schemas.ActionResponse])
def get_user_topic_actions(
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actions list of the topic for current user.
    """
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC

    # Note: no limitations currently, thus return all topic actions
    actions = persistence.get_actions_by_topic_id(db, topic_id)

    return actions
