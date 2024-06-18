from datetime import datetime
from uuid import UUID

from sqlalchemy import Row, and_, delete, false, func, nullsfirst, or_, select, true
from sqlalchemy.orm import Session

from app import models, schemas

sortkey2orderby: dict[schemas.TopicSortKey, list] = {
    schemas.TopicSortKey.THREAT_IMPACT: [
        models.Topic.threat_impact,
        models.Topic.updated_at.desc(),
    ],
    schemas.TopicSortKey.THREAT_IMPACT_DESC: [
        models.Topic.threat_impact.desc(),
        models.Topic.updated_at.desc(),
    ],
    schemas.TopicSortKey.UPDATED_AT: [
        models.Topic.updated_at,
        models.Topic.threat_impact,
    ],
    schemas.TopicSortKey.UPDATED_AT_DESC: [
        models.Topic.updated_at.desc(),
        models.Topic.threat_impact,
    ],
}


def workaround_delete_team_authes_by_user_id(db: Session, user_id: UUID | str) -> None:
    # this is workaround until models fixed with delete on cascade
    db.execute(delete(models.PTeamAuthority).where(models.PTeamAuthority.user_id == str(user_id)))
    db.execute(delete(models.ATeamAuthority).where(models.ATeamAuthority.user_id == str(user_id)))
    db.flush()


def workaround_delete_pteam_authority(db: Session, auth: models.PTeamAuthority) -> None:
    # this is workaround until models fixed with delete on cascade
    db.delete(auth)
    db.flush()


def workaround_delete_ateam_authority(db: Session, auth: models.ATeamAuthority) -> None:
    # this is workaround until models fixed with delete on cascade
    db.delete(auth)
    db.flush()


def get_ateam_topic_statuses(
    db: Session, ateam_id: UUID | str, sort_key: schemas.TopicSortKey, search: str | None
):
    sort_rules = sortkey2orderby[sort_key] + [
        models.Topic.topic_id,  # service by topic
        nullsfirst(models.PTeamTopicTagStatus.topic_status),  # worst state on array[0]
        models.PTeamTopicTagStatus.scheduled_at.desc(),  # latest on array[0] if worst is scheduled
        models.PTeam.pteam_name,
        models.Tag.tag_name,
    ]

    join_topic_rules = [models.Topic.topic_id == models.CurrentPTeamTopicTagStatus.topic_id]
    if search:
        join_topic_rules.append(models.Topic.title.icontains(search, autoescape=True))

    select_stmt = (
        select(
            models.CurrentPTeamTopicTagStatus.topic_id,
            models.CurrentPTeamTopicTagStatus.pteam_id,
            models.PTeam.pteam_name,
            models.Tag,
            models.Topic.title,
            models.Topic.updated_at,
            models.Topic.threat_impact,
            models.PTeamTopicTagStatus,
        )
        .join(
            models.ATeamPTeam,
            and_(
                models.ATeamPTeam.ateam_id == str(ateam_id),
                models.ATeamPTeam.pteam_id == models.CurrentPTeamTopicTagStatus.pteam_id,
            ),
        )
        .join(models.PTeam, models.PTeam.pteam_id == models.CurrentPTeamTopicTagStatus.pteam_id)
        .join(models.Tag, models.Tag.tag_id == models.CurrentPTeamTopicTagStatus.tag_id)
        .join(models.Topic, and_(*join_topic_rules))
        .outerjoin(
            models.PTeamTopicTagStatus,
            models.PTeamTopicTagStatus.status_id == models.CurrentPTeamTopicTagStatus.status_id,
        )
        .where(models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed)
        .order_by(*sort_rules)
    )

    return db.execute(select_stmt).all()


def get_ateam_topic_comments(
    db: Session, ateam_id: UUID | str, topic_id: UUID | str
) -> list[Row[tuple[str, str, str, str, datetime, datetime | None, str, str | None]]]:
    return (
        db.query(
            models.ATeamTopicComment.comment_id,
            models.ATeamTopicComment.topic_id,
            models.ATeamTopicComment.ateam_id,
            models.ATeamTopicComment.user_id,
            models.ATeamTopicComment.created_at,
            models.ATeamTopicComment.updated_at,
            models.ATeamTopicComment.comment,
            models.Account.email,
        )
        .join(
            models.Account,
            models.Account.user_id == models.ATeamTopicComment.user_id,
        )
        .filter(
            models.ATeamTopicComment.ateam_id == str(ateam_id),
            models.ATeamTopicComment.topic_id == str(topic_id),
        )
        .order_by(
            models.ATeamTopicComment.created_at.desc(),
        )
        .all()
    )


def missing_ateam_admin(db: Session, ateam: models.ATeam) -> bool:
    return (
        db.execute(
            select(models.ATeamAuthority).where(
                models.ATeamAuthority.ateam_id == ateam.ateam_id,
                models.ATeamAuthority.authority.op("&")(models.ATeamAuthIntFlag.ADMIN) != 0,
            )
        ).first()
        is None
    )


def missing_pteam_admin(db: Session, pteam: models.PTeam) -> bool:
    return (
        db.execute(
            select(models.PTeamAuthority).where(
                models.PTeamAuthority.pteam_id == pteam.pteam_id,
                models.PTeamAuthority.authority.op("&")(models.PTeamAuthIntFlag.ADMIN) != 0,
            )
        ).first()
        is None
    )


def get_pteam_topic_statuses_summary(db: Session, pteam: models.PTeam, tag: models.Tag) -> dict:
    rows = (
        db.query(
            models.Tag,
            models.Topic,
            models.PTeamTopicTagStatus.created_at.label("executed_at"),
            models.PTeamTopicTagStatus.topic_status,
        )
        .filter(
            models.Tag.tag_id == tag.tag_id,
        )
        .join(
            models.TopicTag, models.TopicTag.tag_id.in_([models.Tag.tag_id, models.Tag.parent_id])
        )
        .join(models.Topic, models.Topic.topic_id == models.TopicTag.topic_id)
        .outerjoin(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
                models.CurrentPTeamTopicTagStatus.tag_id == models.Tag.tag_id,
                models.CurrentPTeamTopicTagStatus.topic_id == models.TopicTag.topic_id,
            ),
        )
        .outerjoin(
            models.PTeamTopicTagStatus,
        )
        .order_by(
            models.Topic.threat_impact,
            models.Topic.updated_at.desc(),
        )
        .all()
    )

    return {
        "tag_id": tag.tag_id,
        "topics": [
            {
                **row.Topic.__dict__,
                "topic_status": row.topic_status or models.TopicStatusType.alerted,
                "executed_at": row.executed_at,
            }
            for row in rows
        ],
    }


def check_tag_is_related_to_topic(db: Session, tag: models.Tag, topic: models.Topic) -> bool:
    row = (
        db.query(models.Tag, models.TopicTag)
        .filter(models.Tag.tag_id == tag.tag_id)
        .outerjoin(
            models.TopicTag,
            and_(
                models.TopicTag.topic_id == topic.topic_id,
                models.TopicTag.tag_id.in_([models.Tag.tag_id, models.Tag.parent_id]),
            ),
        )
        .first()
    )
    return row is not None and row.TopicTag is not None


def get_last_updated_at_in_current_pteam_topic_tag_status(
    db: Session,
    pteam_id: UUID | str,
    tag_id: UUID | str,
) -> datetime | None:
    return db.scalars(
        select(func.max(models.CurrentPTeamTopicTagStatus.updated_at)).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
            models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed,
        )
    ).one()


def ticket_status_to_response(
    db: Session,
    status: models.TicketStatus,
) -> schemas.TopicStatusResponse:
    threat = status.ticket.threat
    dependency = threat.dependency
    service = dependency.service
    actionlogs = db.scalars(
        select(models.ActionLog)
        .where(
            and_(
                func.array_position(status.logging_ids, models.ActionLog.logging_id).is_not(None),
                models.ActionLog.service_id == service.service_id,
            )
        )
        .order_by(models.ActionLog.executed_at.desc())
    ).all()
    return schemas.TopicStatusResponse(
        status_id=UUID(status.status_id),
        topic_id=UUID(threat.topic.topic_id),
        pteam_id=UUID(service.pteam.pteam_id),
        service_id=UUID(service.service_id),
        tag_id=UUID(dependency.tag.tag_id),
        user_id=UUID(status.user_id),
        topic_status=status.topic_status,
        created_at=status.created_at,
        assignees=list(map(UUID, status.assignees)),
        note=status.note,
        scheduled_at=status.scheduled_at,
        action_logs=[schemas.ActionLogResponse(**log.__dict__) for log in actionlogs],
    )


def search_topics_internal(
    db: Session,
    offset: int = 0,
    limit: int = 10,
    sort_key: schemas.TopicSortKey = schemas.TopicSortKey.THREAT_IMPACT,
    threat_impacts: list[int] | None = None,
    title_words: list[str | None] | None = None,
    abstract_words: list[str | None] | None = None,
    tag_ids: list[str | None] | None = None,
    misp_tag_ids: list[str | None] | None = None,
    topic_ids: list[str] | None = None,
    creator_ids: list[str] | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    updated_after: datetime | None = None,
    updated_before: datetime | None = None,
) -> dict:
    # search conditions
    search_by_threat_impacts_stmt = (
        true()
        if threat_impacts is None  # do not filter by threat_impact
        else models.Topic.threat_impact.in_(threat_impacts)
    )
    search_by_tag_ids_stmt = (
        true()
        if tag_ids is None  # do not filter by tag_id
        else or_(
            false(),
            *[
                (
                    models.TopicTag.tag_id.is_(None)  # no tags
                    if tag_id is None
                    else models.TopicTag.tag_id == tag_id
                )
                for tag_id in tag_ids
            ],
        )
    )
    search_by_misp_tag_ids_stmt = (
        true()
        if misp_tag_ids is None  # do not filter by misp_tag_id
        else or_(
            false(),
            *[
                (
                    models.TopicMispTag.tag_id.is_(None)  # no misp_tags
                    if misp_tag_id is None
                    else models.TopicMispTag.tag_id == misp_tag_id
                )
                for misp_tag_id in misp_tag_ids
            ],
        )
    )
    search_by_topic_ids_stmt = (
        true()
        if topic_ids is None  # do not filter by topic_id
        else models.Topic.topic_id.in_(topic_ids)
    )
    search_by_creator_ids_stmt = (
        true()
        if creator_ids is None  # do not filter by created_by
        else models.Topic.created_by.in_(creator_ids)
    )
    search_by_title_words_stmt = (
        true()
        if title_words is None  # do not filter by title
        else or_(
            false(),
            *[
                (
                    models.Topic.title == ""  # empty title
                    if title_word is None
                    else models.Topic.title.icontains(title_word, autoescape=True)
                )
                for title_word in title_words
            ],
        )
    )
    search_by_abstract_words_stmt = (
        true()
        if abstract_words is None  # do not filter by abstract
        else or_(
            false(),
            *[
                (
                    models.Topic.abstract == ""  # empty abstract
                    if abstract_word is None
                    else models.Topic.abstract.icontains(abstract_word, autoescape=True)
                )
                for abstract_word in abstract_words
            ],
        )
    )
    search_by_created_before_stmt = (
        true()
        if created_before is None  # do not filter by created_before
        else models.Topic.created_at <= created_before
    )
    search_by_created_after_stmt = (
        true()
        if created_after is None  # do not filter by created_after
        else models.Topic.created_at >= created_after
    )
    search_by_updated_before_stmt = (
        true()
        if updated_before is None  # do not filter by updated_before
        else models.Topic.updated_at <= updated_before
    )
    search_by_updated_after_stmt = (
        true()
        if updated_after is None  # do not filter by updated_after
        else models.Topic.updated_at >= updated_after
    )

    search_conditions = [
        search_by_threat_impacts_stmt,
        search_by_tag_ids_stmt,
        search_by_misp_tag_ids_stmt,
        search_by_topic_ids_stmt,
        search_by_creator_ids_stmt,
        search_by_title_words_stmt,
        search_by_abstract_words_stmt,
        search_by_created_before_stmt,
        search_by_created_after_stmt,
        search_by_updated_before_stmt,
        search_by_updated_after_stmt,
    ]
    filter_topics_stmt = and_(
        true(),
        *search_conditions,
    )
    filter_topics_stmt = and_(*search_conditions)

    # join tables only if required
    select_topics_stmt = select(models.Topic)
    select_count_stmt = select(func.count(models.Topic.topic_id.distinct()))
    if tag_ids is not None:
        select_topics_stmt = select_topics_stmt.outerjoin(models.TopicTag)
        select_count_stmt = select_count_stmt.outerjoin(models.TopicTag)
    if misp_tag_ids is not None:
        select_topics_stmt = select_topics_stmt.outerjoin(models.TopicMispTag)
        select_count_stmt = select_count_stmt.outerjoin(models.TopicMispTag)

    # count total amount of matched topics
    count_result_stmt = select_count_stmt.where(filter_topics_stmt)
    num_topics = db.scalars(count_result_stmt).one()

    # search topics
    search_topics_stmt = (
        select_topics_stmt.where(filter_topics_stmt)
        .distinct()
        .order_by(*sortkey2orderby[sort_key])
        .offset(offset)
        .limit(limit)
    )
    topics = db.scalars(search_topics_stmt).all()

    result = {
        "num_topics": num_topics,
        "sort_key": sort_key,
        "offset": offset,
        "limit": limit,
        "topics": topics,
    }
    return result


### Artifact Tag


def get_num_of_child_tags(db: Session, tag: models.Tag) -> int:
    return (
        db.query(models.Tag)
        .filter(
            models.Tag.parent_id == tag.tag_id,
            models.Tag.tag_id != tag.tag_id,
        )
        .count()
    )


def get_num_of_tags_by_tag_id_of_pteam_tag_reference(
    db: Session,
    tag_id: UUID,
) -> int:
    return db.query(models.Dependency).filter(models.Dependency.tag_id == str(tag_id)).count()


def get_num_of_tags_by_tag_id_of_topic_tag(
    db: Session,
    tag_id: UUID,
) -> int:
    return db.query(models.TopicTag).filter(models.TopicTag.tag_id == str(tag_id)).count()


def expire_pteam_invitations(db: Session) -> None:
    db.execute(
        delete(models.PTeamInvitation).where(
            or_(
                models.PTeamInvitation.expiration < datetime.now(),
                and_(
                    models.PTeamInvitation.limit_count.is_not(None),
                    models.PTeamInvitation.limit_count <= models.PTeamInvitation.used_count,
                ),
            ),
        )
    )
    db.flush()


def expire_ateam_invitations(db: Session) -> None:
    db.execute(
        delete(models.ATeamInvitation).where(
            or_(
                models.ATeamInvitation.expiration < datetime.now(),
                and_(
                    models.ATeamInvitation.limit_count.is_not(None),
                    models.ATeamInvitation.limit_count <= models.ATeamInvitation.used_count,
                ),
            ),
        )
    )
    db.flush()


def expire_ateam_watching_requests(db: Session) -> None:
    db.execute(
        delete(models.ATeamWatchingRequest).where(
            or_(
                models.ATeamWatchingRequest.expiration < datetime.now(),
                and_(
                    models.ATeamWatchingRequest.limit_count.is_not(None),
                    models.ATeamWatchingRequest.limit_count
                    <= models.ATeamWatchingRequest.used_count,
                ),
            ),
        )
    )
    db.flush()
