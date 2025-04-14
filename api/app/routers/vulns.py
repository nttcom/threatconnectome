from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence, schemas
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
    if not (vuln := persistence.get_vuln_by_id(db, vuln_id)):
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
    else:
        # 仕様メモ
        # userがcreated_byとは一致しない場合、403エラーを返す
        # title、detail、cve_id、exploitation、automatable,cvss_v3_scoreがrequest中に含まれ、かつNoneだったら400
        # cvss_v3_scoreが範囲外だったら400
        # title、cve_id、detail、exploitation、automatable、cvss_v3_score、vulnerable_packagesが空でなかったら更新
        # ssvcのautomatableとexploitationが変更になった場合はssvcの再計算を行う
        # ssvcの対象は

        if vuln.created_by != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not vuln creator",
            )

        # check request format
        # update_topicだと、cve_idや、exploitation、automatableのNoneも許していないが、誤った入力を修正する意味で許容するべき？
        update_request = request.model_dump(exclude_unset=True)
        fields_to_check = [
            "title",
            "detail",
            "cve_id",
            "exploitation",
            "automatable",
            "cvss_v3_score",
        ]
        for field in fields_to_check:
            if field in update_request.keys() and request.title is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot specify None for {field}",
                )

        if "vulnerable_packages" in update_request.keys() and request.vulnerable_packages == []:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify None for vulnerable_packages",
            )
        if "cvss_v3_score" in update_request.keys() and request.vulnerable_packages == []:
            if request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="cvss_v3_score is out of range",
                )

        # update vuln
        if request.title is not None:
            vuln.title = request.title
        if request.detail is not None:
            vuln.detail = request.detail
        if request.cve_id is not None:
            vuln.cve_id = request.cve_id
        if request.exploitation is not None:
            previous_exploitation = vuln.exploitation
            vuln.exploitation = request.exploitation
        if request.automatable is not None:
            previous_automatable = vuln.automatable
            vuln.automatable is vuln.automatable
        if request.vulnerable_packages != []:
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
            ## reset affect
            for affect in vuln.affects:
                persistence.delete_affect(db, affect)

            for package_id, vulnerable_package in requested_packages.items():
                affect = models.Affect(
                    vuln_id=str(vuln_id),
                    package_id=package_id,
                    affected_versions=vulnerable_package.affected_versions,
                    fixed_versions=vulnerable_package.fixed_versions,
                )
                persistence.create_affect(db, affect)

        vuln.updated_at = datetime.now()

        db.flush()

        ## ToDO ssvc calucate
        if (request.exploitation and request.exploitation != previous_exploitation) or (
            request.automatable and request.automatable != previous_automatable
        ):

            pass

        db.commit()

    return schemas.VulnReponse(**response)


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
