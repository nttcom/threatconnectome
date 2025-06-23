import re
from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import (
    and_,
    delete,
    false,
    func,
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
    assigned_user_id: UUID | str | None = None,
) -> Sequence[models.Ticket]:
    select_stmt = select(models.Ticket)
    if assigned_user_id:
        select_stmt = select_stmt.join(
            models.TicketStatus,
            and_(
                models.TicketStatus.ticket_id == models.Ticket.ticket_id,
                func.array_position(models.TicketStatus.assignees, str(assigned_user_id)).isnot(
                    None
                ),
            ),
        )
    else:
        select_stmt = select_stmt.options(
            joinedload(models.Ticket.ticket_status, innerjoin=True).joinedload(
                models.TicketStatus.action_logs, innerjoin=False
            ),
        )

    select_stmt = select_stmt.join(
        models.Threat,
        models.Threat.threat_id == models.Ticket.threat_id,
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


def get_vulns_count(
    db: Session,
    filters,
    pteam_id: UUID | str | None,
) -> int:
    count_query = select(func.count(models.Vuln.vuln_id.distinct()))
    count_query = count_query.join(
        models.Affect,
    )

    # Add a JOIN if referencing Dependency
    if pteam_id:
        count_query = (
            count_query.outerjoin(
                models.PackageVersion,
                models.Package.package_id == models.PackageVersion.package_id,
            )
            .join(
                models.Dependency,
                models.PackageVersion.package_version_id == models.Dependency.package_version_id,
            )
            .join(
                models.Service,
                and_(
                    models.Service.service_id == models.Dependency.service_id,
                    models.Service.pteam_id == str(pteam_id),
                ),
            )
        )

    if filters:
        count_query = count_query.where(and_(*filters))
    result = db.scalar(count_query)
    return result if result is not None else 0


def get_vulns(
    db: Session,
    offset: int,
    limit: int,
    min_cvss_v3_score: float | None = None,
    max_cvss_v3_score: float | None = None,
    vuln_ids: list[str] | None = None,
    title_words: list[str] | None = None,
    detail_words: list[str] | None = None,
    creator_ids: list[str] | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    updated_after: datetime | None = None,
    updated_before: datetime | None = None,
    pteam_id: UUID | str | None = None,
    cve_ids: list[str] | None = None,
    package_name: list[str] | None = None,
    ecosystem: list[str] | None = None,
    sort_key: schemas.VulnSortKey = schemas.VulnSortKey.CVSS_V3_SCORE_DESC,  # set default sort key
) -> dict:
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
            fixed_title_words.add(title_word)

    fixed_detail_words: set[str | None] = set()
    if detail_words is not None:
        for detail_word in detail_words:
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
        select(models.Vuln, models.Affect, models.Package)
        .join(models.Affect, models.Affect.vuln_id == models.Vuln.vuln_id)
        .join(
            models.Package,
            or_(
                # LangPackage: name, ecosystem
                and_(
                    models.Package.type == models.PackageType.LANG,
                    models.Package.name == models.Affect.affected_name,
                    models.Package.ecosystem == models.Affect.ecosystem,
                ),
                # OSPackage: source_name, ecosystem
                and_(
                    models.Package.type == models.PackageType.OS,
                    models.OSPackage.source_name == models.Affect.affected_name,
                    models.Package.ecosystem == models.Affect.ecosystem,
                ),
            ),
        )
    )

    filters = []

    if min_cvss_v3_score is not None:
        filters.append(models.Vuln.cvss_v3_score >= min_cvss_v3_score)
    if max_cvss_v3_score is not None:
        filters.append(models.Vuln.cvss_v3_score <= max_cvss_v3_score)
    if vuln_ids:
        filters.append(models.Vuln.vuln_id.in_(vuln_ids))
    if len(fixed_title_words) > 0:
        filters.append(
            or_(
                false(),
                *[
                    (
                        models.Vuln.title == ""
                        if title_word == ""
                        else models.Vuln.title.icontains(title_word, autoescape=True)
                    )
                    for title_word in fixed_title_words
                ],
            )
        )
    if len(fixed_detail_words) > 0:
        filters.append(
            or_(
                false(),
                *[
                    (
                        models.Vuln.detail == ""
                        if detail_word == ""
                        else models.Vuln.detail.icontains(detail_word, autoescape=True)
                    )
                    for detail_word in fixed_detail_words
                ],
            )
        )
    if len(fixed_cve_ids) > 0:
        filters.append(models.Vuln.cve_id.in_(fixed_cve_ids))
    if created_after:
        filters.append(models.Vuln.created_at >= created_after)
    if created_before:
        filters.append(models.Vuln.created_at <= created_before)
    if updated_after:
        filters.append(models.Vuln.updated_at >= updated_after)
    if updated_before:
        filters.append(models.Vuln.updated_at <= updated_before)
    if len(fixed_creator_ids) > 0:
        filters.append(models.Vuln.created_by.in_(fixed_creator_ids))

    if package_name:
        filters.append(models.Affect.affected_name.in_(package_name))
    if ecosystem:
        filters.append(models.Affect.ecosystem.in_(ecosystem))

    # PTeam filter
    if pteam_id:
        query = (
            query.outerjoin(
                models.PackageVersion,
                models.Package.package_id == models.PackageVersion.package_id,
            )
            .join(
                models.Dependency,
                models.PackageVersion.package_version_id == models.Dependency.package_version_id,
            )
            .join(
                models.Service,
                and_(
                    models.Service.service_id == models.Dependency.service_id,
                    models.Service.pteam_id == str(pteam_id),
                ),
            )
        )

    # Count total number of vulnerabilities matching the filters
    num_vulns = get_vulns_count(db, filters, pteam_id)

    if filters:
        query = query.where(and_(*filters))

    sortkey2orderby: dict[schemas.VulnSortKey, list] = {
        schemas.VulnSortKey.CVSS_V3_SCORE: [
            models.Vuln.cvss_v3_score.nulls_first(),
            models.Vuln.updated_at.desc(),
        ],
        schemas.VulnSortKey.CVSS_V3_SCORE_DESC: [
            models.Vuln.cvss_v3_score.desc().nullslast(),
            models.Vuln.updated_at.desc(),
        ],
        schemas.VulnSortKey.UPDATED_AT: [
            models.Vuln.updated_at,
            models.Vuln.cvss_v3_score.desc().nullslast(),
        ],
        schemas.VulnSortKey.UPDATED_AT_DESC: [
            models.Vuln.updated_at.desc(),
            models.Vuln.cvss_v3_score.desc().nullslast(),
        ],
    }

    query = query.order_by(*sortkey2orderby[sort_key])

    # Pageination
    query = query.distinct().offset(offset).limit(limit)

    rows = db.execute(query).all()

    vuln_dict = {}
    for vuln, affect, package in rows:
        if vuln.vuln_id not in vuln_dict:
            vuln_dict[vuln.vuln_id] = {
                "vuln": vuln,
                "affects": [],
            }
        vuln_dict[vuln.vuln_id]["affects"].append((affect, package))

    result = {
        "num_vulns": num_vulns,
        "vulns": list(vuln_dict.values()),
    }
    return result


def get_packages_summary(
    db: Session, pteam_id: UUID | str, service_id: UUID | str | None
) -> list[dict]:
    unsolved_subq = (
        select(
            models.Ticket.dependency_id,
            models.Ticket.ssvc_deployer_priority,
            models.Vuln.updated_at,
        )
        .join(
            models.TicketStatus,
            and_(
                models.TicketStatus.ticket_id == models.Ticket.ticket_id,
                models.TicketStatus.vuln_status != models.VulnStatusType.completed,
            ),
        )
        .join(models.Threat)
        .join(models.Vuln)
        .subquery()
    )
    min_unsolved_ssvc_priority = func.min(unsolved_subq.c.ssvc_deployer_priority).label(
        "min_ssvc_priority"
    )
    max_unsolved_updated_at = func.max(unsolved_subq.c.updated_at).label("max_updated_at")
    service_ids = func.array_agg(models.Service.service_id.distinct()).label("service_ids")
    package_managers = func.array_agg(models.Dependency.package_manager.distinct()).label(
        "package_managers"
    )

    summarize_stmt = (
        select(
            models.Package.package_id,
            models.Package.name,
            models.Package.ecosystem,
            package_managers,
            min_unsolved_ssvc_priority,
            max_unsolved_updated_at,
            service_ids,
        )
        .join(models.PackageVersion, models.PackageVersion.package_id == models.Package.package_id)
        .join(models.Dependency)
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
        .group_by(models.Package.package_id)
        .order_by(
            min_unsolved_ssvc_priority.nullslast(),
            max_unsolved_updated_at.desc().nullslast(),
            models.Package.name,
            models.Package.ecosystem,
        )
    )

    if service_id is not None:
        summarize_stmt = summarize_stmt.where(models.Dependency.service_id == str(service_id))

    count_status_stmt = (
        select(
            models.Package.package_id,
            models.TicketStatus.vuln_status,
            func.count(models.TicketStatus.vuln_status).label("num_status"),
        )
        .join(models.PackageVersion)
        .join(models.Dependency)
        .join(
            models.Service,
            and_(
                models.Service.service_id == models.Dependency.service_id,
                models.Service.pteam_id == str(pteam_id),
            ),
        )
        .join(models.Ticket)
        .join(models.TicketStatus)
        .group_by(
            models.Package.package_id,
            models.TicketStatus.vuln_status,
        )
    )

    if service_id is not None:
        count_status_stmt = count_status_stmt.where(models.Dependency.service_id == str(service_id))

    status_count_dict = {
        (row.package_id, row.vuln_status): row.num_status
        for row in db.execute(count_status_stmt).all()
    }
    summary = [
        {
            "package_id": row.package_id,
            "package_name": row.name,
            "ecosystem": row.ecosystem,
            "package_managers": row.package_managers,
            "ssvc_priority": row.min_ssvc_priority,
            "updated_at": row.max_updated_at,
            "service_ids": row.service_ids,
            "status_count": {
                status_type.value: status_count_dict.get((row.package_id, status_type.value), 0)
                for status_type in list(models.VulnStatusType)
            },
        }
        for row in db.execute(summarize_stmt).all()
    ]

    return summary


def get_related_packages_by_affect(db: Session, affect: models.Affect) -> Sequence[models.Package]:
    return db.scalars(
        select(models.Package).where(
            and_(
                models.Package.ecosystem == str(affect.ecosystem),
                or_(
                    models.OSPackage.source_name == str(affect.affected_name),
                    models.Package.name == str(affect.affected_name),
                ),
            )
        )
    ).all()


def get_related_affects_by_package(db: Session, package: models.Package) -> Sequence[models.Affect]:
    affected_name_condition = [models.Affect.affected_name == str(package.name)]
    if isinstance(package, models.OSPackage):
        affected_name_condition.append(models.Affect.affected_name == str(package.source_name))

    return db.scalars(
        select(models.Affect).where(
            and_(
                models.Affect.ecosystem == str(package.ecosystem),
                or_(*affected_name_condition),
            )
        )
    ).all()
