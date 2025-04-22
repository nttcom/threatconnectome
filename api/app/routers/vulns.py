from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth.account import get_current_user
from app.business import threat_business, ticket_business
from app.database import get_db
from app.routers.validators.account_validator import check_pteam_membership

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
        content_fingerprint=vuln.content_fingerprint,
    )


@router.get("", response_model=list[schemas.VulnReponse])
def get_vulns(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a vuln.
    """

    vulns = command.get_vulns(db, offset, limit)
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
                content_fingerprint=vuln.content_fingerprint,
            )
        )

    return response_vulns


@router.get(
    "/{vuln_id}/actions", response_model=schemas.VulnActionsResponse | list[schemas.ActionResponse]
)
def get_vuln_actions(
    vuln_id: UUID,
    pteam_id: UUID | None = None,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get actions list of the vuln for specified pteam or current user.
    """
    if not persistence.get_vuln_by_id(db, vuln_id):
        raise NO_SUCH_VULN

    if pteam_id:
        # Fetch actions for a specific pteam
        if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
        if not check_pteam_membership(pteam, current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")

        actions = persistence.get_actions_by_vuln_id(db, vuln_id)
        return {
            "vuln_id": vuln_id,
            "pteam_id": pteam_id,
            "actions": actions,
        }

    else:
        # Fetch actions for the current user
        actions = persistence.get_actions_by_vuln_id(db, vuln_id)
        return actions
