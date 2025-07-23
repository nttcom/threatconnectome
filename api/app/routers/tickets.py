from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import command, database, models, persistence, schemas
from app.auth.account import get_current_user
from app.routers.validators.account_validator import check_pteam_membership

router = APIRouter(prefix="/tickets", tags=["tickets"])


def ticket_to_response(ticket: models.Ticket):
    dependency = ticket.dependency
    service = dependency.service
    pteam_id = service.pteam_id
    service_id = service.service_id
    return schemas.TicketResponse(
        ticket_id=UUID(ticket.ticket_id),
        vuln_id=UUID(ticket.threat.vuln_id),
        dependency_id=UUID(ticket.dependency_id),
        service_id=service_id,
        pteam_id=pteam_id,
        created_at=ticket.created_at,
        ssvc_deployer_priority=ticket.ssvc_deployer_priority,
        ticket_safety_impact=ticket.ticket_safety_impact,
        ticket_safety_impact_change_reason=ticket.ticket_safety_impact_change_reason,
        ticket_status=(schemas.TicketStatusResponse.model_validate(ticket.ticket_status)),
    )


@router.get("", response_model=schemas.TicketListResponse)
def get_tickets(
    assigned_to_me: bool = Query(False),
    pteam_ids: list[UUID] | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_key: schemas.TicketSortKey = Query(schemas.TicketSortKey.SSVC_DEPLOYER_PRIORITY_DESC),
    exclude_statuses: list[models.VulnStatusType] | None = Query(None),
    cve_ids: list[str] | None = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Get tickets.

    Get a list of tickets with optional filtering, sorting, and pagination.

    ### Filtering:
    - `assigned_to_me`: Filter tickets assigned to the current user.
    - `pteam_ids`: List of pteam IDs to filter tickets. If not provided, uses all pteams the user belongs to.
    - `exclude_statuses`: List of vulnerability statuses to exclude from results.
    - `cve_ids`: List of CVE IDs to filter tickets by.

    ### Sorting:
    - `sort_key`: Sort key for the results. Default is `SSVC_DEPLOYER_PRIORITY_DESC`.
      Supported values:
        - `SSVC_DEPLOYER_PRIORITY`: Sort by SSVC deployer priority (ascending).
        - `SSVC_DEPLOYER_PRIORITY_DESC`: Sort by SSVC deployer priority (descending).
        - `CREATED_AT`: Sort by created_at (ascending).
        - `CREATED_AT_DESC`: Sort by created_at (descending).

    ### Pagination:
    - `offset`: Number of items to skip before starting to collect the result set.
    - `limit`: Maximum number of items to return.

    Defaults are `None` for all filtering parameters, which means skip filtering.
    Different parameters are combined with AND conditions.

    Examples:
    - `...?assigned_to_me=true` -> Only tickets assigned to the current user.
    - `...?cve_ids=CVE-2023-1234` -> Filter by the specific CVE ID.
    - `...?exclude_statuses=completed` -> Exclude completed tickets.
    """

    if not pteam_ids:
        user_pteam_ids = {UUID(str(role.pteam_id)) for role in current_user.pteam_roles}
        pteam_ids = list(user_pteam_ids)

    db_pteams = persistence.get_pteams_by_ids(db, pteam_ids)
    found_pteam_ids = {str(pteam.pteam_id) for pteam in db_pteams}
    not_found = set(str(pid) for pid in pteam_ids) - found_pteam_ids
    if not_found:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specified pteam_ids do not exist: {not_found}",
        )

    not_belong = [
        pteam.pteam_id for pteam in db_pteams if not check_pteam_membership(pteam, current_user)
    ]
    if not_belong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specified pteam_ids not belonging to the user: {not_belong}",
        )

    assigned_user_id = (
        UUID(current_user.user_id) if assigned_to_me and current_user.user_id else None
    )
    try:
        total_count, tickets = command.get_sorted_paginated_tickets_for_pteams(
            db=db,
            pteam_ids=pteam_ids,
            assigned_user_id=assigned_user_id,
            offset=offset,
            limit=limit,
            sort_key=sort_key,
            exclude_statuses=exclude_statuses,
            cve_ids=cve_ids,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {e}",
        )

    return schemas.TicketListResponse(
        total=total_count,
        tickets=[ticket_to_response(ticket) for ticket in tickets],
    )
