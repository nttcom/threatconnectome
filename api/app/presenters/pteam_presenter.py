from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app import command, models
from app.database import get_db


def _count_ssvc_priority_from_summary(tags_summary: list[dict]):
    ssvc_priority_count: dict[models.SSVCDeployerPriorityEnum, int] = {
        priority: 0 for priority in list(models.SSVCDeployerPriorityEnum)
    }
    for tag_summary in tags_summary:
        ssvc_priority_count[
            tag_summary["ssvc_priority"] or models.SSVCDeployerPriorityEnum.DEFER
        ] += 1
    return ssvc_priority_count


def get_pteam_service_tags_summary(
    service_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    tags_summary = command.get_tags_summary_by_service_id(db, service_id)

    ssvc_priority_count = _count_ssvc_priority_from_summary(tags_summary)

    return {
        "ssvc_priority_count": ssvc_priority_count,
        "tags": tags_summary,
    }


def get_pteam_tags_summary(
    pteam_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    tags_summary = command.get_tags_summary_by_pteam_id(db, pteam_id)

    ssvc_priority_count = _count_ssvc_priority_from_summary(tags_summary)

    return {
        "ssvc_priority_count": ssvc_priority_count,
        "tags": tags_summary,
    }
