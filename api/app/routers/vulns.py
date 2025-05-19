from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth.account import get_current_user
from app.business import package_business, threat_business, ticket_business
from app.database import get_db

router = APIRouter(prefix="/vulns", tags=["vulns"])

NO_SUCH_VULN = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such vuln")


@router.put("/{vuln_id}", response_model=schemas.VulnResponse)
def update_vuln(
    vuln_id: UUID,
    request: schemas.VulnUpdate,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a vuln.
    - `cvss_v3_score` : Ranges from 0.0 to 10.0.
    """
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
        vuln_response = __handle_create_vuln(vuln_id, request, current_user, db)
    else:
        vuln_response = __handle_update_vuln(vuln, vuln_id, request, current_user, db)

    db.commit()

    return vuln_response


def __handle_create_vuln(
    vuln_id: UUID, request: schemas.VulnUpdate, current_user: models.Account, db: Session
):
    # TODO: It may be unnecessary to check
    if vuln_id == UUID(int=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create default vuln"
        )

    # check request format
    if (request.title is None) or (request.detail is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'title' and 'detail' are required when creating a vuln.",
        )

    # check packages
    requested_packages = _get_requested_packages(db, request.vulnerable_packages)

    # check cvss_v3_score range
    if request.cvss_v3_score is not None:
        if request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cvss_v3_score is out of range",
            )

    # create vuln
    now = datetime.now()

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

    for package_id, vulnerable_package in requested_packages.items():
        affect = models.Affect(
            vuln_id=str(vuln_id),
            package_id=package_id,
            affected_versions=vulnerable_package.affected_versions,
            fixed_versions=vulnerable_package.fixed_versions,
        )
        persistence.create_affect(db, affect)

    new_threats: list[models.Threat] = threat_business.fix_threat_by_vuln(db, vuln)
    for threat in new_threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    db.commit()

    return schemas.VulnResponse(
        vuln_id=str(vuln_id),
        created_by=UUID(vuln.created_by) if vuln.created_by else None,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at,
        title=vuln.title,
        cve_id=vuln.cve_id,
        detail=vuln.detail,
        exploitation=vuln.exploitation,
        automatable=vuln.automatable,
        cvss_v3_score=vuln.cvss_v3_score,
        vulnerable_packages=request.vulnerable_packages,
    )


def __handle_update_vuln(
    vuln: models.Vuln,
    vuln_id: UUID,
    request: schemas.VulnUpdate,
    current_user: models.Account,
    db: Session,
):
    if vuln.created_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not vuln creator",
        )

    # check request format
    update_request = request.model_dump(exclude_unset=True)
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

    if (
        "cvss_v3_score" in update_request.keys()
        and request.cvss_v3_score is not None
        and (request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cvss_v3_score is out of range",
        )

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
        requested_packages = _get_requested_packages(db, request.vulnerable_packages)

        # update affect
        for affect in vuln.affects:
            if affect.package_id not in requested_packages.keys():
                package = affect.package
                persistence.delete_affect(db, affect)
                package_business.fix_package(db, package)

        for package_id, vulnerable_package in requested_packages.items():
            if (
                persisted_affect := persistence.get_affect_by_package_id_and_vuln_id(
                    db, package_id, vuln_id
                )
            ) is not None:
                persisted_affect.affected_versions = vulnerable_package.affected_versions
                persisted_affect.fixed_versions = vulnerable_package.fixed_versions
            else:
                new_affect = models.Affect(
                    vuln_id=str(vuln_id),
                    package_id=package_id,
                    affected_versions=vulnerable_package.affected_versions,
                    fixed_versions=vulnerable_package.fixed_versions,
                )
                persistence.create_affect(db, new_affect)

    vuln.updated_at = datetime.now()

    new_threats: list[models.Threat] = threat_business.fix_threat_by_vuln(db, vuln)
    for threat in new_threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    db.commit()

    vulnerable_packages = [
        schemas.VulnerablePackage(
            package_id=affect.package_id,
            name=affect.package.name,
            ecosystem=affect.package.ecosystem,
            affected_versions=affect.affected_versions,
            fixed_versions=affect.fixed_versions,
        )
        for affect in vuln.affects
    ]

    return schemas.VulnResponse(
        vuln_id=vuln.vuln_id,
        created_by=UUID(vuln.created_by) if vuln.created_by else None,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at,
        title=vuln.title,
        cve_id=vuln.cve_id,
        detail=vuln.detail,
        exploitation=vuln.exploitation,
        automatable=vuln.automatable,
        cvss_v3_score=vuln.cvss_v3_score,
        vulnerable_packages=vulnerable_packages,
    )


def _get_requested_packages(db: Session, vulnerable_packages: list) -> dict:
    requested_packages = {}
    for vuln_pkg in vulnerable_packages:
        package = persistence.get_package_by_name_and_ecosystem(
            db, vuln_pkg.name, vuln_pkg.ecosystem
        )
        if not package:
            package = models.Package(name=vuln_pkg.name, ecosystem=vuln_pkg.ecosystem)
            persistence.create_package(db, package)
        requested_packages[package.package_id] = vuln_pkg
    return requested_packages


@router.delete("/{vuln_id}", status_code=status.HTTP_204_NO_CONTENT)
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

    packages: list[models.Package] = [affect.package for affect in vuln.affects]

    # Delete the vuln and its associated affects
    persistence.delete_vuln(db, vuln)

    for package in packages:
        package_business.fix_package(db, package)

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

    # Fetch vulnerable packages associated with the vuln
    vulnerable_packages = [
        schemas.VulnerablePackage(
            package_id=affect.package_id,
            name=affect.package.name,
            ecosystem=affect.package.ecosystem,
            affected_versions=affect.affected_versions,
            fixed_versions=affect.fixed_versions,
        )
        for affect in vuln.affects
    ]

    return schemas.VulnResponse(
        vuln_id=vuln.vuln_id,
        created_by=UUID(vuln.created_by) if vuln.created_by else None,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at,
        title=vuln.title,
        cve_id=vuln.cve_id,
        detail=vuln.detail,
        exploitation=vuln.exploitation,
        automatable=vuln.automatable,
        cvss_v3_score=vuln.cvss_v3_score,
        vulnerable_packages=vulnerable_packages,
    )


@router.get("", response_model=list[schemas.VulnResponse])
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
    package_manager: str | None = Query(None),
    sort_key: schemas.VulnSortKey = Query(schemas.VulnSortKey.CVSS_V3_SCORE_DESC),
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
    - `package_manager`: Package manager to filter by.

    ### Sorting:
    - `sort_key`: Sort key for the results. Default is `CVSS_V3_SCORE_DESC`.
      Supported values:
        - `CVSS_V3_SCORE`: Sort by CVSS v3 score (ascending).
        - `CVSS_V3_SCORE_DESC`: Sort by CVSS v3 score (descending).
        - `UPDATED_AT`: Sort by updated_at (ascending).
        - `UPDATED_AT_DESC`: Sort by updated_at (descending).

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
        vulns = command.get_vulns(
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
            package_manager=package_manager,
            sort_key=sort_key,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {e}",
        )

    response_vulns = []
    for vuln in vulns:
        # Fetch vulnerable packages associated with the vuln
        vulnerable_packages = [
            schemas.VulnerablePackage(
                package_id=affect.package_id,
                name=affect.package.name,
                ecosystem=affect.package.ecosystem,
                affected_versions=affect.affected_versions,
                fixed_versions=affect.fixed_versions,
            )
            for affect in vuln.affects
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

    return response_vulns


@router.get("/{vuln_id}/actions", response_model=list[schemas.ActionResponse])
def get_vuln_actions(
    vuln_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the list of actions associated with the specified vulnerability.
    """
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
        raise NO_SUCH_VULN

    # Use the new relationship to fetch actions
    return vuln.vuln_actions
