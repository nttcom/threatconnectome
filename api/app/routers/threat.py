from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth.account import get_current_user
from app.business.ticket_business import fix_ticket_ssvc_priority
from app.database import get_db
from app.routers.validators.account_validator import check_pteam_membership
from app.utility.unicode_tool import count_full_width_and_half_width_characters

router = APIRouter(prefix="/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatResponse])
def get_threats(
    service_id: UUID | None = Query(None),
    dependency_id: UUID | None = Query(None),
    topic_id: UUID | None = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all threats.

    Query Params:
    - **service_id** (Optional) filter by specified service_id. Default is None.
    - **dependency_id** (Optional) filter by specified service_id. Default is None.
    - **topic_id** (Optional) filter by specified topic_id. Default is None.
    """
    threats = command.search_threats(db, service_id, dependency_id, topic_id, current_user.user_id)

    return threats


@router.get("/{threat_id}", response_model=schemas.ThreatResponse)
def get_threat(
    threat_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a threat.
    """
    if not (threat := persistence.get_threat_by_id(db, threat_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    pteam = threat.dependency.service.pteam

    if check_pteam_membership(pteam, current_user):
        return threat
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")


@router.put("/{threat_id}", response_model=schemas.ThreatResponse)
def update_threat_safety_impact(
    threat_id: UUID,
    data: schemas.ThreatUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update threat_safety_impact.
    """
    max_reason_safety_impact_length_in_half = 500

    if not (threat := persistence.get_threat_by_id(db, threat_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such threat")

    pteam = threat.dependency.service.pteam

    if not check_pteam_membership(pteam, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a pteam member")

    need_fix_ssvc_priority = False
    updated_keys = data.model_dump(exclude_unset=True).keys()
    if "threat_safety_impact" in updated_keys:
        need_fix_ssvc_priority = threat.threat_safety_impact != data.threat_safety_impact
        threat.threat_safety_impact = data.threat_safety_impact
    if "reason_safety_impact" in updated_keys:
        if data.reason_safety_impact and (
            reason_safety_impact := data.reason_safety_impact.strip()
        ):
            if (
                count_full_width_and_half_width_characters(reason_safety_impact)
                > max_reason_safety_impact_length_in_half
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Too long reason_safety_impact. "
                        f"Max length is {max_reason_safety_impact_length_in_half} in half-width "
                        f"or {int(max_reason_safety_impact_length_in_half / 2)} in full-width"
                    ),
                )
            threat.reason_safety_impact = reason_safety_impact
        else:
            threat.reason_safety_impact = None

    if threat.ticket and need_fix_ssvc_priority:
        db.flush()
        fix_ticket_ssvc_priority(db, threat.ticket)

    db.commit()

    return threat
