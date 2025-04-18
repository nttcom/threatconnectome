from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth.account import get_current_user
from app.business import threat_business, ticket_business
from app.database import get_db

router = APIRouter(prefix="/vulns", tags=["vulns"])

NO_SUCH_VULN = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such vuln")


@router.put("/{vuln_id}", response_model=schemas.VulnReponse)
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
    if not persistence.get_vuln_by_id(db, vuln_id):
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
        requested_packages = {}
        for vulneraable_package in request.vulnerable_packages:
            if not (
                package := persistence.get_package_by_name_and_ecosystem(
                    db, vulneraable_package.name, vulneraable_package.ecosystem
                )
            ):
                package = models.Package(
                    name=vulneraable_package.name, ecosystem=vulneraable_package.ecosystem
                )
                persistence.create_package(db, package)
            requested_packages[package.package_id] = vulneraable_package

        # check cvss_v3_score range
        if request.cvss_v3_score is not None:
            if request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="cvss_v3_score is out of range",
                )

        # create vuln
        now = datetime.now()

        ## ToDo add content_fingerprint
        vuln = models.Vuln(
            vuln_id=str(vuln_id),
            title=request.title,
            detail=request.detail,
            cve_id=request.cve_id,
            created_by=current_user.user_id,
            created_at=now,
            updated_at=now,
            cvss_v3_score=request.cvss_v3_score,
            content_fingerprint="dummy_fingerprint",
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

        response = request.model_dump()
        response["vuln_id"] = str(vuln_id)

    return schemas.VulnReponse(**response)


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

    # Delete the vuln and its associated affects
    persistence.delete_vuln(db, vuln)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{vuln_id}", response_model=schemas.VulnReponse)
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
            name=affect.package.name,
            ecosystem=affect.package.ecosystem,
            affected_versions=affect.affected_versions,
            fixed_versions=affect.fixed_versions,
        )
        for affect in vuln.affects
    ]

    return schemas.VulnReponse(
        vuln_id=vuln.vuln_id,
        title=vuln.title,
        cve_id=vuln.cve_id,
        detail=vuln.detail,
        exploitation=vuln.exploitation,
        automatable=vuln.automatable,
        cvss_v3_score=vuln.cvss_v3_score,
        vulnerable_packages=vulnerable_packages,
    )


@router.get("", response_model=list[schemas.VulnReponse])
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
    cve_ids: list[str] | None = Query(None),
    package_name: list[str] | None = Query(None),
    ecosystem: list[str] | None = Query(None),
    package_manager: str | None = Query(None),
    sort_key: str = Query(
        "cvss_v3_score_desc",
        pattern="^(cvss_v3_score|cvss_v3_score_desc|updated_at|updated_at_desc)$",
    ),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a vuln.

    Search vulnerabilities by the following parameters with sorting and pagination:

    - `min_cvss_v3_score`: Minimum CVSS v3 score (float).
    - `max_cvss_v3_score`: Maximum CVSS v3 score (float).
    - `title_words`: List of words to search in the title (case-insensitive).
    - `detail_words`: List of words to search in the detail (case-insensitive).
    - `creator_ids`: List of creator IDs to filter by.
    - `created_after`: Filter vulnerabilities created after this datetime.
    - `created_before`: Filter vulnerabilities created before this datetime.
    - `updated_after`: Filter vulnerabilities updated after this datetime.
    - `updated_before`: Filter vulnerabilities updated before this datetime.
    - `cve_ids`: List of CVE IDs to filter by.
    - `package_name`: List of package names to filter by.
    - `ecosystem`: List of ecosystems to filter by.
    - `package_manager`: Package manager to filter by.

    Defaults are `None` for all parameters, which means skip filtering.
    Different parameters are combined with AND conditions.
    Words search is case-insensitive.

    Examples:
    - `...?title_words=a&title_words=%20&title_words=B` -> Title includes [a, A, b, B, or space].
    - `...?title_words=a&title_words=&title_words=B` -> Title includes [a, A, b, B] or is empty.
    - `...?cve_ids=CVE-2023-1234` -> Filter by the specific CVE ID.
    - `...?package_name=example` -> Filter by the package name "example".
    """

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
        cve_ids=cve_ids,
        package_name=package_name,
        ecosystem=ecosystem,
        package_manager=package_manager,
        sort_key=sort_key,
    )

    response_vulns = []
    for vuln in vulns:
        # Fetch vulnerable packages associated with the vuln
        vulnerable_packages = [
            schemas.VulnerablePackage(
                name=affect.package.name,
                ecosystem=affect.package.ecosystem,
                affected_versions=affect.affected_versions,
                fixed_versions=affect.fixed_versions,
            )
            for affect in vuln.affects
        ]

        response_vulns.append(
            schemas.VulnReponse(
                vuln_id=vuln.vuln_id,
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
