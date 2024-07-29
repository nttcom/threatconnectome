from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import (
    Row,
    Subquery,
    and_,
    delete,
    false,
    func,
    nullsfirst,
    or_,
    select,
    true,
)
from sqlalchemy.orm import Session, joinedload

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
        nullsfirst(models.CurrentTicketStatus.topic_status),  # worst state on array[0]
        models.TicketStatus.scheduled_at.desc(),  # latest on array[0] if worst is scheduled
        models.PTeam.pteam_name,
        models.Tag.tag_name,
    ]

    join_topic_rules = [models.Topic.topic_id == models.Threat.topic_id]
    if search:
        join_topic_rules.append(models.Topic.title.icontains(search, autoescape=True))

    select_stmt = (
        select(
            models.ATeamPTeam.ateam_id,
            models.PTeam.pteam_id,
            models.PTeam.pteam_name,
            models.Service.service_id,
            models.Service.service_name,
            models.Tag,
            models.Topic.topic_id,
            models.Topic.title,
            models.Topic.updated_at,
            models.Topic.threat_impact,
            models.TicketStatus,
        )
        .join(
            models.PTeam,
            and_(
                models.ATeamPTeam.ateam_id == str(ateam_id),
                models.ATeamPTeam.pteam_id == models.PTeam.pteam_id,
            ),
        )
        .join(models.Service)
        .join(models.Dependency)
        .join(models.Tag)
        .join(models.Threat)
        .join(models.Topic, and_(*join_topic_rules))
        .join(models.Ticket)
        .join(
            models.CurrentTicketStatus,
            and_(
                models.CurrentTicketStatus.ticket_id == models.Ticket.ticket_id,
                models.CurrentTicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .outerjoin(models.TicketStatus)
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
    pteam_id: UUID | None = None,
    ateam_id: UUID | None = None,
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

    subq_team_affected_tag: Subquery | None = None
    if pteam_id:
        subq_team_affected_tag = (
            select(models.Tag)
            .join(models.Dependency)
            .join(
                models.Service,
                and_(
                    models.Service.service_id == models.Dependency.service_id,
                    models.Service.pteam_id == str(pteam_id),
                ),
            )
            .subquery()
        )
    elif ateam_id:
        subq_team_affected_tag = (
            select(models.Tag)
            .join(models.Dependency)
            .join(models.Service)
            .join(
                models.ATeamPTeam,
                and_(
                    models.Service.pteam_id == models.ATeamPTeam.pteam_id,
                    models.ATeamPTeam.ateam_id == str(ateam_id),
                ),
            )
            .subquery()
        )

    # join tables only if required
    select_topics_stmt = select(models.Topic)
    select_count_stmt = select(func.count(models.Topic.topic_id.distinct()))
    if subq_team_affected_tag is not None:
        # filter by join
        # Note: use inner join because Tag required to check affected
        select_topics_stmt = select_topics_stmt.join(models.TopicTag).join(
            subq_team_affected_tag,
            models.TopicTag.tag_id.in_(
                [subq_team_affected_tag.c.tag_id, subq_team_affected_tag.c.parent_id]
            ),
        )
        select_count_stmt = select_count_stmt.join(models.TopicTag).join(
            subq_team_affected_tag,
            models.TopicTag.tag_id.in_(
                [subq_team_affected_tag.c.tag_id, subq_team_affected_tag.c.parent_id]
            ),
        )
    elif tag_ids is not None:
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


def get_tags_summary_by_service_id(db: Session, service_id: UUID | str) -> list[dict]:
    threat_impact = func.min(models.Topic.threat_impact).label("threat_impact")
    updated_at = func.max(models.Topic.updated_at).label("updated_at")
    summarize_stmt = (
        select(
            models.Tag.tag_id,
            models.Tag.tag_name,
            models.Tag.parent_id,
            models.Tag.parent_name,
            threat_impact,
            updated_at,
        )
        .join(
            models.Dependency,
            and_(
                models.Dependency.tag_id == models.Tag.tag_id,
                models.Dependency.service_id == str(service_id),
            ),
        )
        .outerjoin(models.Threat)
        .outerjoin(models.Ticket)
        .outerjoin(models.CurrentTicketStatus)
        .outerjoin(
            models.Topic,  # do not count completed topic
            and_(
                models.Topic.topic_id == models.Threat.topic_id,
                models.CurrentTicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .group_by(models.Tag.tag_id)
        .order_by(
            func.coalesce(threat_impact, 4),
            updated_at.desc().nullslast(),
            models.Tag.tag_name,
        )
    )

    count_status_stmt = (
        select(
            models.Tag.tag_id,
            models.CurrentTicketStatus.topic_status,
            func.count(models.CurrentTicketStatus.topic_status).label("num_status"),
        )
        .join(
            models.Dependency,
            and_(
                models.Dependency.tag_id == models.Tag.tag_id,
                models.Dependency.service_id == str(service_id),
            ),
        )
        .join(models.Threat)
        .join(models.Ticket)
        .join(models.CurrentTicketStatus)
        .group_by(models.Tag.tag_id, models.CurrentTicketStatus.topic_status)
    )

    status_count_dict = {
        (row.tag_id, row.topic_status): row.num_status
        for row in db.execute(count_status_stmt).all()
    }
    summary = [
        {
            "tag_id": row.tag_id,
            "tag_name": row.tag_name,
            "parent_id": row.parent_id,
            "parent_name": row.parent_name,
            "threat_impact": row.threat_impact,
            "updated_at": row.updated_at,
            "status_count": {
                status_type.value: status_count_dict.get((row.tag_id, status_type.value), 0)
                for status_type in list(models.TopicStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]
    return summary


def get_tags_summary_by_pteam_id(db: Session, pteam_id: UUID | str) -> list[dict]:
    threat_impact = func.min(models.Topic.threat_impact).label("threat_impact")
    updated_at = func.max(models.Topic.updated_at).label("updated_at")
    service_ids = func.array_agg(models.Service.service_id.distinct()).label("service_ids")
    summarize_stmt = (
        select(
            models.Tag.tag_id,
            models.Tag.tag_name,
            models.Tag.parent_id,
            models.Tag.parent_name,
            threat_impact,
            updated_at,
            service_ids,
        )
        .join(
            models.Dependency,
            models.Dependency.tag_id == models.Tag.tag_id,
        )
        .join(
            models.Service,
            and_(
                models.Service.service_id == models.Dependency.service_id,
                models.Service.pteam_id == str(pteam_id),
            ),
        )
        .outerjoin(models.Threat)
        .outerjoin(models.Ticket)
        .outerjoin(models.CurrentTicketStatus)
        .outerjoin(
            models.Topic,  # do not count completed topic
            and_(
                models.Topic.topic_id == models.Threat.topic_id,
                models.CurrentTicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .group_by(models.Tag.tag_id)
        .order_by(
            func.coalesce(threat_impact, 4),
            updated_at.desc().nullslast(),
            models.Tag.tag_name,
        )
    )

    count_status_stmt = (
        select(
            models.Tag.tag_id,
            models.CurrentTicketStatus.topic_status,
            func.count(models.CurrentTicketStatus.topic_status).label("num_status"),
        )
        .join(models.Dependency)
        .join(
            models.Service,
            and_(
                models.Service.service_id == models.Dependency.service_id,
                models.Service.pteam_id == str(pteam_id),
            ),
        )
        .join(models.Threat)
        .join(models.Ticket)
        .join(models.CurrentTicketStatus)
        .group_by(models.Tag.tag_id, models.CurrentTicketStatus.topic_status)
    )

    status_count_dict = {
        (row.tag_id, row.topic_status): row.num_status
        for row in db.execute(count_status_stmt).all()
    }

    summary = [
        {
            "tag_id": row.tag_id,
            "tag_name": row.tag_name,
            "parent_id": row.parent_id,
            "parent_name": row.parent_name,
            "service_ids": row.service_ids,
            "threat_impact": row.threat_impact,
            "updated_at": row.updated_at,
            "status_count": {
                status_type.value: status_count_dict.get((row.tag_id, status_type.value), 0)
                for status_type in list(models.TopicStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]

    return summary


def get_sorted_tickets_related_to_service_and_topic(
    db: Session,
    service_id: UUID | str,
    topic_id: UUID | str,
) -> Sequence[models.Ticket]:
    select_stmt = (
        select(models.Ticket)
        .options(
            joinedload(models.Ticket.current_ticket_status, innerjoin=True).joinedload(
                models.CurrentTicketStatus.ticket_status, innerjoin=False
            ),
            joinedload(models.Ticket.threat, innerjoin=True),
        )
        .join(
            models.Threat,
            and_(
                models.Threat.threat_id == models.Ticket.threat_id,
                models.Threat.topic_id == str(topic_id),
            ),
        )
        .join(
            models.Dependency,
            and_(
                models.Dependency.dependency_id == models.Threat.dependency_id,
                models.Dependency.service_id == str(service_id),
            ),
        )
        .order_by(models.Ticket.ssvc_deployer_priority, models.Dependency.target)
    )
    return db.scalars(select_stmt).all()
