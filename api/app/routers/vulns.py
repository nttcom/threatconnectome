from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import api_key
from app.auth.account import get_current_user
from app.business import threat_business, ticket_business
from app.database import get_db

router = APIRouter(prefix="/vulns", tags=["vulns"])

NO_SUCH_VULN = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such vuln")


def _create_vuln_response(db: Session, vuln: models.Vuln) -> schemas.VulnResponse:
    vulnerable_packages_response = []
    for affect in vuln.affects:
        vulnerable_packages_response.append(
            schemas.VulnerablePackageResponse(
                affected_name=affect.affected_name,
                ecosystem=affect.ecosystem,
                affected_versions=affect.affected_versions,
                fixed_versions=affect.fixed_versions,
            )
        )

    return schemas.VulnResponse(
        vuln_id=UUID(vuln.vuln_id),
        created_by=UUID(vuln.created_by) if vuln.created_by else None,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at,
        title=vuln.title,
        cve_id=vuln.cve_id,
        detail=vuln.detail,
        exploitation=vuln.exploitation,
        automatable=vuln.automatable,
        cvss_v3_score=vuln.cvss_v3_score,
        vulnerable_packages=vulnerable_packages_response,
    )


@router.put(
    "/{vuln_id}",
    response_model=schemas.VulnResponse,
    include_in_schema=False,
    dependencies=[Depends(api_key.verify_api_key)],
)
def update_vuln(
    vuln_id: UUID,
    request: schemas.VulnUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a vuln if it exists,
    or create a new vuln if the specified vuln_id is not found in the database.
    - `cvss_v3_score` : Ranges from 0.0 to 10.0.
    """
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
        vuln = __handle_create_vuln(vuln_id, request, current_user, db)
    else:
        vuln = __handle_update_vuln(vuln, request, current_user, db)

    db.refresh(vuln)
    vuln_response = _create_vuln_response(db, vuln)

    db.commit()

    return vuln_response


def __handle_create_vuln(
    vuln_id: UUID, request: schemas.VulnUpdateRequest, current_user: models.Account, db: Session
) -> models.Vuln:
    if vuln_id == UUID(int=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create default vuln"
        )

    # check request format
    update_request = request.model_dump(exclude_unset=True)
    if ("title" not in update_request.keys()) or ("detail" not in update_request.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'title' and 'detail' are required when creating a vuln.",
        )

    _check_request_fields(request, update_request)

    # create vuln
    now = datetime.now(timezone.utc)

    vuln = models.Vuln(
        vuln_id=str(vuln_id),
        title=request.title,
        detail=request.detail,
        cve_id=request.cve_id,
        created_by=current_user.user_id,
        created_at=now,
        updated_at=now,
        cvss_v3_score=request.cvss_v3_score,
        exploitation=request.exploitation,
        automatable=request.automatable,
    )

    persistence.create_vuln(db, vuln)

    for vulnerable_package in request.vulnerable_packages:
        affect = models.Affect(
            vuln_id=str(vuln_id),
            affected_versions=vulnerable_package.affected_versions,
            fixed_versions=vulnerable_package.fixed_versions,
            affected_name=vulnerable_package.affected_name,
            ecosystem=vulnerable_package.ecosystem,
        )
        persistence.create_affect(db, affect)

    new_threats: list[models.Threat] = threat_business.fix_threat_by_vuln(db, vuln)
    for threat in new_threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    # create vulnerable_packages_response
    vulnerable_packages_response = []
    for affect in vuln.affects:
        vulnerable_packages_response.append(
            schemas.VulnerablePackageResponse(
                affected_name=affect.affected_name,
                ecosystem=affect.ecosystem,
                affected_versions=affect.affected_versions,
                fixed_versions=affect.fixed_versions,
            )
        )

    return vuln


def __handle_update_vuln(
    vuln: models.Vuln,
    request: schemas.VulnUpdateRequest,
    current_user: models.Account,
    db: Session,
) -> models.Vuln:
    if vuln.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not vuln creator",
        )

    # check request format
    update_request = request.model_dump(exclude_unset=True)
    _check_request_fields(request, update_request)

    # update vuln
    if "title" in update_request.keys() and request.title is not None:
        vuln.title = request.title
    if "detail" in update_request.keys() and request.detail is not None:
        vuln.detail = request.detail
    if "cve_id" in update_request.keys():
        vuln.cve_id = request.cve_id
    if "exploitation" in update_request.keys() and request.exploitation is not None:
        vuln.exploitation = request.exploitation
    if "automatable" in update_request.keys() and request.automatable is not None:
        vuln.automatable = request.automatable
    if "cvss_v3_score" in update_request.keys():
        vuln.cvss_v3_score = request.cvss_v3_score
    if "vulnerable_packages" in update_request.keys():
        affect_keys = {
            (vulnerable_package.affected_name, vulnerable_package.ecosystem)
            for vulnerable_package in request.vulnerable_packages
        }
        for affect in vuln.affects:
            if (affect.affected_name, affect.ecosystem) not in affect_keys:
                persistence.delete_affect(db, affect)

        for vulnerable_package in request.vulnerable_packages:
            if (
                persisted_affect := _get_affect_by_affected_name_and_ecosystem(
                    vuln.affects, vulnerable_package.affected_name, vulnerable_package.ecosystem
                )
            ) is not None:
                persisted_affect.affected_versions = vulnerable_package.affected_versions
                persisted_affect.fixed_versions = vulnerable_package.fixed_versions
            else:
                new_affect = models.Affect(
                    vuln_id=str(vuln.vuln_id),
                    affected_versions=vulnerable_package.affected_versions,
                    fixed_versions=vulnerable_package.fixed_versions,
                    affected_name=vulnerable_package.affected_name,
                    ecosystem=vulnerable_package.ecosystem,
                )
                persistence.create_affect(db, new_affect)

    vuln.updated_at = datetime.now(timezone.utc)
    db.flush()

    new_threats: list[models.Threat] = threat_business.fix_threat_by_vuln(db, vuln)
    for threat in new_threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    return vuln


def _check_request_fields(request: schemas.VulnUpdateRequest, update_request: dict):
    fields_to_check = [
        "title",
        "detail",
        "exploitation",
        "automatable",
    ]
    for field in fields_to_check:
        if field in update_request.keys() and getattr(request, field) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot specify None for {field}",
            )

    # check cvss_v3_score range
    if request.cvss_v3_score is not None:
        if request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cvss_v3_score is out of range",
            )

    name_ecosystem_pairs = set()
    for vuln_pkg in request.vulnerable_packages:
        pair = (vuln_pkg.affected_name, vuln_pkg.ecosystem)
        if pair in name_ecosystem_pairs:
            message = (
                f"Duplicate package {vuln_pkg.affected_name} in ecosystem {vuln_pkg.ecosystem}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )
        name_ecosystem_pairs.add(pair)


def _get_affect_by_affected_name_and_ecosystem(
    affects: list[models.Affect], affected_name: str, ecosystem: str
) -> models.Affect | None:
    for affect in affects:
        if affect.affected_name == affected_name and affect.ecosystem == ecosystem:
            return affect
    return None


@router.delete(
    "/{vuln_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
    dependencies=[Depends(api_key.verify_api_key)],
)
def delete_vuln(
    vuln_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a vuln.
    """
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
        raise NO_SUCH_VULN

    # Delete the vuln and its associated affects
    persistence.delete_vuln(db, vuln)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{vuln_id}", response_model=schemas.VulnResponse)
def get_vuln(
    vuln_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a vuln.
    """
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
        raise NO_SUCH_VULN

    return _create_vuln_response(db, vuln)


@router.get("", response_model=schemas.VulnsListResponse)
def get_vulns(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_cvss_v3_score: float | None = Query(None),
    max_cvss_v3_score: float | None = Query(None),
    vuln_ids: list[str] | None = Query(None),
    title_words: list[str] | None = Query(None),
    detail_words: list[str] | None = Query(None),
    creator_ids: list[str] | None = Query(None),
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    updated_after: datetime | None = Query(None),
    updated_before: datetime | None = Query(None),
    pteam_id: UUID | None = Query(None),
    cve_ids: list[str] | None = Query(None),
    package_name: list[str] | None = Query(None),
    ecosystem: list[str] | None = Query(None),
    sort_keys: list = Query(["-cvss_v3_score", "-updated_at"]),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get vulns.

    Get a list of vulnerabilities with optional filtering, sorting, and pagination.

    ### Filtering:
    - `min_cvss_v3_score`: Minimum CVSS v3 score (float).
    - `max_cvss_v3_score`: Maximum CVSS v3 score (float).
    - `vuln_ids`: List of vuln IDs to filter by.
    - `title_words`: List of words to search in the title (case-insensitive).
    - `detail_words`: List of words to search in the detail (case-insensitive).
    - `creator_ids`: List of creator IDs to filter by.
    - `created_after`: Filter vulnerabilities created after this datetime.
    - `created_before`: Filter vulnerabilities created before this datetime.
    - `updated_after`: Filter vulnerabilities updated after this datetime.
    - `updated_before`: Filter vulnerabilities updated before this datetime.
    - `pteam_id`: Filter vulnerabilities associated with this PTeam ID.
    - `cve_ids`: List of CVE IDs to filter by.
    - `package_name`: List of package names to filter by.
    - `ecosystem`: List of ecosystems to filter by.

    ### Sorting:
    - `sort_keys`: Sort key for the results.
      Default is `["-cvss_v3_score", "-updated_at"]`.
      - Supported values:
        - cvss_v3_score
        - updated_at
        - created_at
        - cve_id
    - If a minus sign is added, the order is descending. if not, the order is ascending.
        - Example: -cvss_v3_score, -updated_at, -created_at etc.
    - If only one sort key is provided, a second default sort key is automatically appended.
      This ensures deterministic ordering. If the first key is "updated_at" or "-updated_at",
      "-cvss_v3_score" is appended; otherwise, "-updated_at" is appended.

    ### Pagination:
    - `offset`: Number of items to skip before starting to collect the result set.
    - `limit`: Maximum number of items to return.

    Defaults are `None` for all filtering parameters, which means skip filtering.
    Different parameters are combined with AND conditions.
    Words search is case-insensitive.

    Examples:
    - `...?title_words=a&title_words=%20&title_words=B` -> Title includes [a, A, b, B, or space].
    - `...?title_words=a&title_words=&title_words=B` -> Title includes [a, A, b, B] or is empty.
    - `...?cve_ids=CVE-2023-1234` -> Filter by the specific CVE ID.
    - `...?package_name=example` -> Filter by the package name "example".
    """
    try:
        result = command.get_vulns(
            db=db,
            offset=offset,
            limit=limit,
            min_cvss_v3_score=min_cvss_v3_score,
            max_cvss_v3_score=max_cvss_v3_score,
            vuln_ids=vuln_ids,
            title_words=title_words,
            detail_words=detail_words,
            creator_ids=creator_ids,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            pteam_id=pteam_id,
            cve_ids=cve_ids,
            package_name=package_name,
            ecosystem=ecosystem,
            sort_keys=sort_keys,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {e}",
        )

    response_vulns = []
    for vuln in result["vulns"]:
        affects = vuln.affects
        vulnerable_packages = [
            schemas.VulnerablePackageResponse(
                affected_name=affect.affected_name,
                ecosystem=affect.ecosystem,
                affected_versions=affect.affected_versions,
                fixed_versions=affect.fixed_versions,
            )
            for affect in affects
        ]
        response_vulns.append(
            schemas.VulnResponse(
                vuln_id=vuln.vuln_id,
                created_at=vuln.created_at,
                updated_at=vuln.updated_at,
                created_by=UUID(vuln.created_by) if vuln.created_by else None,
                title=vuln.title,
                cve_id=vuln.cve_id,
                detail=vuln.detail,
                exploitation=vuln.exploitation,
                automatable=vuln.automatable,
                cvss_v3_score=vuln.cvss_v3_score,
                vulnerable_packages=vulnerable_packages,
            )
        )

    return schemas.VulnsListResponse(num_vulns=result["num_vulns"], vulns=response_vulns)
