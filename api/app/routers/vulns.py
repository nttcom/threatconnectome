from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.database import get_db

router = APIRouter(prefix="/vulns", tags=["vulns"])


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

        # check same id vuln already exists
        # if persistence.get_vuln_by_id(db, vuln_id):

        # check packages
        requested_packages: dict[str, models.Package | None] = {
            package.name: persistence.get_package_by_name(db, package.name)
            for package in request.vulnerable_packages
        }

        if not_exist_package_names := [
            package_name for package_name, package in requested_packages.items() if package is None
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No such packages: {', '.join(sorted(not_exist_package_names))}",
            )

        # check cvss_v3_score range
        if request.cvss_v3_score is not None:
            if request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="cvss_v3_score is out of range",
                )

        # create or update vuln
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

        for vulnerable_package in request.vulnerable_packages:
            package = persistence.get_package_by_name(db, vulnerable_package.name)
            affect = models.Affect(
                vuln_id=str(vuln_id),
                package_id=package.package_id,
                affected_versions=vulnerable_package.affected_versions,
                fixed_versions=vulnerable_package,
            )
            persistence.create_affect(db, affect)

        ## ToDo fix_threats_for_topic

        db.commit()

        response = request.model_dump()
        response["vuln_id"] = str(vuln_id)

    return schemas.VulnReponse(**response)
