from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import (
    Subquery,
    and_,
    delete,
    false,
    func,
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
    db.flush()


def workaround_delete_pteam_authority(db: Session, auth: models.PTeamAuthority) -> None:
    # this is workaround until models fixed with delete on cascade
    db.delete(auth)
    db.flush()


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


def search_threats(
    db: Session,
    service_id: UUID | str | None,
    dependency_id: UUID | str | None,
    topic_id: UUID | str | None,
    current_user: models.Account | None = None,
) -> Sequence[models.Threat]:
    select_stmt = select(models.Threat)

    select_stmt = (
        select_stmt.join(models.Dependency)
        .join(models.Service)
        .join(models.PTeam)
        .join(models.PTeamAccount)
        .join(models.Account)
    )

    if current_user:
        select_stmt = select_stmt.where(models.Account.user_id == current_user.user_id)

    if service_id:
        select_stmt = select_stmt.where(models.Dependency.service_id == str(service_id))
    if dependency_id:
        select_stmt = select_stmt.where(models.Threat.dependency_id == str(dependency_id))
    if topic_id:
        select_stmt = select_stmt.where(models.Threat.topic_id == str(topic_id))

    return db.scalars(select_stmt).all()


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


def get_tags_summary_by_service_id(db: Session, service_id: UUID | str) -> list[dict]:
    unsolved_subq = (
        select(
            models.Threat.dependency_id,
            models.Ticket.ssvc_deployer_priority,
            models.Topic.updated_at,
        )
        .join(models.Ticket)
        .join(
            models.TicketStatus,
            and_(
                models.TicketStatus.ticket_id == models.Ticket.ticket_id,
                models.TicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .join(models.Topic)
        .subquery()
    )
    min_unsolved_ssvc_priority = func.min(unsolved_subq.c.ssvc_deployer_priority).label(
        "min_ssvc_priority"
    )
    max_unsolved_updated_at = func.max(unsolved_subq.c.updated_at).label("max_updated_at")
    summarize_stmt = (
        select(
            models.Tag.tag_id,
            models.Tag.tag_name,
            models.Tag.parent_id,
            models.Tag.parent_name,
            min_unsolved_ssvc_priority,
            max_unsolved_updated_at,
        )
        .join(
            models.Dependency,
            and_(
                models.Dependency.tag_id == models.Tag.tag_id,
                models.Dependency.service_id == str(service_id),
            ),
        )
        .outerjoin(
            unsolved_subq,
            unsolved_subq.c.dependency_id == models.Dependency.dependency_id,
        )
        .group_by(models.Tag.tag_id)
        .order_by(
            min_unsolved_ssvc_priority.nullslast(),
            max_unsolved_updated_at.desc().nullslast(),
            models.Tag.tag_name,
        )
    )

    count_status_stmt = (
        select(
            models.Tag.tag_id,
            models.TicketStatus.topic_status,
            func.count(models.TicketStatus.topic_status).label("num_status"),
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
        .join(models.TicketStatus)
        .group_by(models.Tag.tag_id, models.TicketStatus.topic_status)
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
            "ssvc_priority": row.min_ssvc_priority,
            "updated_at": row.max_updated_at,
            "status_count": {
                status_type.value: status_count_dict.get((row.tag_id, status_type.value), 0)
                for status_type in list(models.TopicStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]
    return summary


def get_tags_summary_by_pteam_id(db: Session, pteam_id: UUID | str) -> list[dict]:
    unsolved_subq = (
        select(
            models.Threat.dependency_id,
            models.Ticket.ssvc_deployer_priority,
            models.Topic.updated_at,
        )
        .join(models.Ticket)
        .join(
            models.TicketStatus,
            and_(
                models.TicketStatus.ticket_id == models.Ticket.ticket_id,
                models.TicketStatus.topic_status != models.TopicStatusType.completed,
            ),
        )
        .join(models.Topic)
        .subquery()
    )
    min_unsolved_ssvc_priority = func.min(unsolved_subq.c.ssvc_deployer_priority).label(
        "min_ssvc_priority"
    )
    max_unsolved_updated_at = func.max(unsolved_subq.c.updated_at).label("max_updated_at")
    service_ids = func.array_agg(models.Service.service_id.distinct()).label("service_ids")
    summarize_stmt = (
        select(
            models.Tag.tag_id,
            models.Tag.tag_name,
            models.Tag.parent_id,
            models.Tag.parent_name,
            min_unsolved_ssvc_priority,
            max_unsolved_updated_at,
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
        .outerjoin(
            unsolved_subq,
            unsolved_subq.c.dependency_id == models.Dependency.dependency_id,
        )
        .group_by(models.Tag.tag_id)
        .order_by(
            min_unsolved_ssvc_priority.nullslast(),
            max_unsolved_updated_at.desc().nullslast(),
            models.Tag.tag_name,
        )
    )

    count_status_stmt = (
        select(
            models.Tag.tag_id,
            models.TicketStatus.topic_status,
            func.count(models.TicketStatus.topic_status).label("num_status"),
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
        .join(models.TicketStatus)
        .group_by(models.Tag.tag_id, models.TicketStatus.topic_status)
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
            "ssvc_priority": row.min_ssvc_priority,
            "updated_at": row.max_updated_at,
            "status_count": {
                status_type.value: status_count_dict.get((row.tag_id, status_type.value), 0)
                for status_type in list(models.TopicStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]

    return summary


def get_sorted_tickets_related_to_service_and_topic_and_tag(
    db: Session,
    service_id: UUID | str,
    topic_id: UUID | str,
    tag_id: UUID | str,
) -> Sequence[models.Ticket]:
    select_stmt = (
        select(models.Ticket)
        .options(
            joinedload(models.Ticket.ticket_status, innerjoin=True).joinedload(
                models.TicketStatus.action_logs, innerjoin=False
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
                models.Dependency.tag_id == str(tag_id),
            ),
        )
        .order_by(models.Ticket.ssvc_deployer_priority, models.Dependency.target)
    )
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading
    return db.scalars(select_stmt).unique().all()
