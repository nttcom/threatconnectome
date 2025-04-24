import re
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import (
    and_,
    delete,
    or_,
    select,
)
from sqlalchemy.orm import Session, joinedload

from app import models, persistence, schemas


def missing_pteam_admin(db: Session, pteam: models.PTeam) -> bool:
    return (
        db.execute(
            select(models.PTeamAccountRole).where(
                models.PTeamAccountRole.pteam_id == pteam.pteam_id,
                models.PTeamAccountRole.is_admin.is_(True),
            )
        ).first()
        is None
    )


def search_threats(
    db: Session,
    service_id: UUID | str | None,
    dependency_id: UUID | str | None,
    topic_id: UUID | str | None,
    user_id: UUID | str | None = None,
) -> Sequence[models.Threat]:
    select_stmt = select(models.Threat)

    select_stmt = (
        select_stmt.join(models.Dependency)
        .join(models.Service)
        .join(models.PTeam)
        .join(models.PTeamAccountRole)
        .join(models.Account)
    )

    if user_id:
        select_stmt = select_stmt.where(models.Account.user_id == str(user_id))

    if service_id:
        select_stmt = select_stmt.where(models.Dependency.service_id == str(service_id))
    if dependency_id:
        select_stmt = select_stmt.where(models.Threat.dependency_id == str(dependency_id))
    if topic_id:
        select_stmt = select_stmt.where(models.Threat.topic_id == str(topic_id))

    return db.scalars(select_stmt).all()


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


def get_sorted_tickets_related_to_service_and_package_and_vuln(
    db: Session,
    service_id: UUID | str | None,
    package_id: UUID | str | None,
    vuln_id: UUID | str | None,
) -> Sequence[models.Ticket]:
    select_stmt = (
        select(models.Ticket)
        .options(
            joinedload(models.Ticket.ticket_status, innerjoin=True).joinedload(
                models.TicketStatus.action_logs, innerjoin=False
            ),
        )
        .join(
            models.Threat,
            models.Threat.threat_id == models.Ticket.threat_id,
        )
    )

    if vuln_id:
        select_stmt = select_stmt.where(models.Threat.vuln_id == str(vuln_id))
    if package_id:
        select_stmt = select_stmt.join(
            models.PackageVersion,
            and_(
                models.PackageVersion.package_version_id == models.Threat.package_version_id,
                models.PackageVersion.package_id == str(package_id),
            ),
        )
    if service_id:
        select_stmt = select_stmt.join(
            models.Dependency,
            and_(
                models.Dependency.dependency_id == models.Ticket.dependency_id,
                models.Dependency.service_id == str(service_id),
            ),
        )

    select_stmt = select_stmt.order_by(
        models.Ticket.ssvc_deployer_priority, models.Ticket.created_at
    )

    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading
    return db.scalars(select_stmt).unique().all()


def get_vulns(
    db: Session,
    offset: int,
    limit: int,
    min_cvss_v3_score: Optional[float] = None,
    max_cvss_v3_score: Optional[float] = None,
    vuln_ids: Optional[list[str]] = None,
    title_words: Optional[list[str]] = None,
    detail_words: Optional[list[str]] = None,
    creator_ids: Optional[list[str]] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    updated_after: Optional[datetime] = None,
    updated_before: Optional[datetime] = None,
    cve_ids: Optional[list[str]] = None,
    package_name: Optional[list[str]] = None,
    ecosystem: Optional[list[str]] = None,
    package_manager: Optional[str] = None,
    sort_key: str = "cvss_v3_score_desc",  # set default sort key
) -> Sequence[models.Vuln]:

    keyword_for_empty = ""

    # Remove duplicates from lists
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

    fixed_detail_words: set[str | None] = set()
    if detail_words is not None:
        for detail_word in detail_words:
            if detail_word == keyword_for_empty:
                fixed_detail_words.add(None)
                continue
            fixed_detail_words.add(detail_word)

    fixed_cve_ids: set[str | None] = set()
    if cve_ids is not None:
        for cve_id in cve_ids:
            if re.match(schemas.CVE_PATTERN, cve_id):
                fixed_cve_ids.add(cve_id)
            else:
                raise ValueError(f"Invalid CVE ID format: {cve_id}")

    # Base query
    query = (
        select(models.Vuln)
        .join(models.Affect)
        .join(models.Package, models.Affect.package_id == models.Package.package_id)
    )

    # Conditionally join Dependency if package_manager is specified
    if package_manager:
        query = query.outerjoin(
            models.PackageVersion, models.Package.package_id == models.PackageVersion.package_id
        ).outerjoin(
            models.Dependency,
            models.PackageVersion.package_version_id == models.Dependency.package_version_id,
        )

    filters = []

    if min_cvss_v3_score is not None:
        filters.append(models.Vuln.cvss_v3_score >= min_cvss_v3_score)
    if max_cvss_v3_score is not None:
        filters.append(models.Vuln.cvss_v3_score <= max_cvss_v3_score)
    if vuln_ids:
        filters.append(models.Vuln.vuln_id.in_(vuln_ids))
    filters.append(
        or_(
            *[
                (
                    models.Vuln.title == ""
                    if title_word is None
                    else models.Vuln.title.icontains(title_word, autoescape=True)
                )
                for title_word in fixed_title_words
            ]
        )
    )
    filters.append(
        or_(
            *[
                (
                    models.Vuln.detail == ""
                    if detail_word is None
                    else models.Vuln.detail.icontains(detail_word, autoescape=True)
                )
                for detail_word in fixed_detail_words
            ]
        )
    )
    filters.append(models.Vuln.cve_id.in_(fixed_cve_ids))
    if created_after:
        filters.append(models.Vuln.created_at >= created_after)
    if created_before:
        filters.append(models.Vuln.created_at <= created_before)
    if updated_after:
        filters.append(models.Vuln.updated_at >= updated_after)
    if updated_before:
        filters.append(models.Vuln.updated_at <= updated_before)
    filters.append(models.Vuln.created_by.in_(fixed_creator_ids))

    # Affect filters
    if package_name:
        filters.append(models.Affect.package.has(models.Package.name.in_(package_name)))
    if ecosystem:
        filters.append(models.Affect.package.has(models.Package.ecosystem.in_(ecosystem)))

    # Dependency filters
    if package_manager:
        filters.append(models.Dependency.package_manager == package_manager)

    if filters:
        query = query.where(and_(*filters))

    # Sorting logic
    if sort_key == "cvss_v3_score":
        query = query.order_by(models.Vuln.cvss_v3_score.asc())
    elif sort_key == "cvss_v3_score_desc":
        query = query.order_by(models.Vuln.cvss_v3_score.desc())
    elif sort_key == "updated_at":
        query = query.order_by(models.Vuln.updated_at.asc())
    elif sort_key == "updated_at_desc":
        query = query.order_by(models.Vuln.updated_at.desc())
    else:
        # デフォルトのソート順
        query = query.order_by(models.Vuln.cvss_v3_score.desc())

    # Pageination
    query = query.offset(offset).limit(limit)

    return db.scalars(query).unique().all()
