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

        response = request.model_dump()
        response["vuln_id"] = str(vuln_id)
        vuln_response = schemas.VulnReponse(**response)
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
            if field in update_request.keys() and getattr(request, field) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot specify None for {field}",
                )

        if "cvss_v3_score" in update_request.keys() and (
            request.cvss_v3_score > 10.0 or request.cvss_v3_score < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cvss_v3_score is out of range",
            )

        # update vuln
        if "title" in update_request.keys():
            vuln.title = request.title
        if "detail" in update_request.keys():
            vuln.detail = request.detail
        if "cve_id" in update_request.keys():
            vuln.cve_id = request.cve_id
        if "exploitation" in update_request.keys():
            vuln.exploitation = request.exploitation
        if "automatable" in update_request.keys():
            vuln.automatable = request.automatable
        if "cvss_v3_score" in update_request.keys():
            vuln.cvss_v3_score = request.cvss_v3_score
        if "vulnerable_packages" in update_request.keys():
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

            ## delete affect
            for affect in vuln.affects:
                if affect.package_id not in requested_packages.keys():
                    persistence.delete_affect(db, affect)

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
        vuln_response = schemas.VulnReponse(
            vuln_id=vuln.vuln_id,
            title=vuln.title,
            cve_id=vuln.cve_id,
            detail=vuln.detail,
            exploitation=vuln.exploitation,
            automatable=vuln.automatable,
            cvss_v3_score=vuln.cvss_v3_score,
            vulnerable_packages=request.vulnerable_packages,
        )

    new_threats: list[models.Threat] = threat_business.fix_threat_by_vuln(db, vuln)
    for threat in new_threats:
        ticket_business.fix_ticket_by_threat(db, threat)

    db.commit()

    return vuln_response


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
