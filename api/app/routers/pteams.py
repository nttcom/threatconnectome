import io
import json
import logging
from datetime import datetime
from hashlib import sha256
from io import DEFAULT_BUFFER_SIZE, BytesIO
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from PIL import Image
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth.account import get_current_user
from app.business.ssvc_business import get_topic_ids_summary_by_service_id_and_tag_id
from app.business.ticket_business import fix_ticket_ssvc_priority
from app.database import get_db, open_db_session
from app.notification.alert import notify_sbom_upload_ended
from app.notification.slack import validate_slack_webhook_url
from app.routers.validators.account_validator import (
    check_pteam_admin_authority,
    check_pteam_membership,
)
from app.sbom.sbom_analyzer import sbom_json_to_artifact_json_lines
from app.utility.unicode_tool import count_full_width_and_half_width_characters

router = APIRouter(prefix="/pteams", tags=["pteams"])


NOT_A_PTEAM_MEMBER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not a pteam member",
)
NOT_HAVE_AUTH = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have authority",
)
NO_SUCH_PTEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
NO_SUCH_TOPIC = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
NO_SUCH_TAG = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")
NO_SUCH_SERVICE = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
NO_SUCH_TICKET = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ticket")


@router.get("", response_model=list[schemas.PTeamEntry])
def get_pteams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all pteams list.
    """
    return persistence.get_all_pteams(db)


@router.post("/apply_invitation", response_model=schemas.PTeamInfo)
def apply_invitation(
    request: schemas.ApplyInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply invitation to pteam.
    """
    command.expire_pteam_invitations(db)

    if not (invitation := persistence.get_pteam_invitation_by_id(db, request.invitation_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) invitation id"
        )
    if current_user in invitation.pteam.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined to the pteam"
        )
    new_role = models.PTeamAccountRole(
        pteam_id=invitation.pteam.pteam_id, user_id=current_user.user_id, is_admin=False
    )
    invitation.pteam.pteam_roles.append(new_role)

    pteam = invitation.pteam  # keep for the case invitation is expired
    invitation.used_count += 1
    db.flush()
    command.expire_pteam_invitations(db)

    db.commit()

    return pteam


@router.get("/invitation/{invitation_id}", response_model=schemas.PTeamInviterResponse)
def invited_pteam(invitation_id: UUID, db: Session = Depends(get_db)):
    if not (invitation := persistence.get_pteam_invitation_by_id(db, invitation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invitation id")

    invitation_detail = {
        "pteam_id": invitation.pteam_id,
        "pteam_name": invitation.pteam.pteam_name,
        "email": invitation.inviter.email,
        "user_id": invitation.user_id,
    }
    return invitation_detail


@router.get("/{pteam_id}", response_model=schemas.PTeamInfo)
def get_pteam(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pteam details. members only.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return pteam


@router.post("/{pteam_id}/fix_ssvc_priorities")
def force_calculate_ssvc_priority(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger ssvc priority calculation.

    Note: Many alerts may occur. Check your Alert-Threshold setting.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    now = datetime.now()
    for ticket in [ticket for service in pteam.services for ticket in service.tickets]:
        fix_ticket_ssvc_priority(db, ticket, now=now)

    db.commit()
    return "OK"


@router.get("/{pteam_id}/services", response_model=list[schemas.PTeamServiceResponse])
def get_pteam_services(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return sorted(pteam.services, key=lambda x: x.service_name)


@router.put("/{pteam_id}/services/{service_id}", response_model=schemas.PTeamServiceUpdateResponse)
def update_pteam_service(
    pteam_id: UUID,
    service_id: UUID,
    data: schemas.PTeamServiceUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update params of the pteam service.
    - service_name
      * max length: 255 in half-width or 127 in full-width
    - keywords
      * max number: 5
      * max length: 20 in half-width or 10 in full-width
    - description
      * max length: 300 in half-width or 150 in full-width
    """
    max_service_name_length_in_half = 255
    max_keywords = 5
    max_keyword_length_in_half = 20
    max_description_length_in_half = 300
    error_too_long_service_name = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Too long service name. Max length is {max_service_name_length_in_half} in half-width "
            f"or {int(max_service_name_length_in_half / 2)} in full-width"
        ),
    )
    error_too_many_keywords = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Too many keywords, max number: {max_keywords}",
    )
    error_too_long_keyword = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Too long keyword. Max length is {max_keyword_length_in_half} in half-width or "
            f"{int(max_keyword_length_in_half / 2)} in full-width"
        ),
    )
    error_too_long_description = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Too long description. Max length is {max_description_length_in_half} in half-width "
            f"or {int(max_description_length_in_half / 2)} in full-width"
        ),
    )

    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    update_data = data.model_dump(exclude_unset=True)
    if "service_name" in update_data.keys() and data.service_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for service_name",
        )
    if "keywords" in update_data.keys() and data.keywords is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for keywords",
        )
    if "system_exposure" in update_data.keys() and data.system_exposure is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for system_exposure",
        )
    if "service_mission_impact" in update_data.keys() and data.service_mission_impact is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for service_mission_impact",
        )
    if "service_safety_impact" in update_data.keys() and data.service_safety_impact is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for service_safety_impact",
        )

    if "description" in update_data.keys():
        if data.description is None:
            service.description = None
        elif description := data.description.strip():
            if (
                count_full_width_and_half_width_characters(description)
                > max_description_length_in_half
            ):
                raise error_too_long_description
            service.description = description
        else:
            service.description = None
    if data.keywords is not None:
        fixed_words = {fixed_word for keyword in data.keywords if (fixed_word := keyword.strip())}
        if len(fixed_words) > max_keywords:
            raise error_too_many_keywords
        if any(
            count_full_width_and_half_width_characters(fixed_word) > max_keyword_length_in_half
            for fixed_word in fixed_words
        ):
            raise error_too_long_keyword
        service.keywords = sorted(fixed_words)
    if data.service_name is not None:
        update_service_name = data.service_name.strip()
        if (
            count_full_width_and_half_width_characters(update_service_name)
            > max_service_name_length_in_half
        ):
            raise error_too_long_service_name

        if service.service_name != update_service_name:
            existing_service_names = [service.service_name for service in pteam.services]
            if update_service_name in existing_service_names:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Service name already exists in the same team",
                )
            service.service_name = update_service_name

    need_fix_tickets = False

    if data.system_exposure not in {None, service.system_exposure}:
        service.system_exposure = data.system_exposure
        need_fix_tickets = True

    if data.service_mission_impact not in {None, service.service_mission_impact}:
        service.service_mission_impact = data.service_mission_impact
        need_fix_tickets = True

    if data.service_safety_impact not in {None, service.service_safety_impact}:
        service.service_safety_impact = data.service_safety_impact
        need_fix_tickets = True

    if need_fix_tickets:
        db.flush()
        for ticket in service.tickets:
            fix_ticket_ssvc_priority(db, ticket, now=datetime.now())

    db.commit()

    return service


@router.post("/{pteam_id}/services/{service_id}/thumbnail")
async def upload_service_thumbnail(
    pteam_id: UUID,
    service_id: UUID,
    uploaded: UploadFile,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload thumbnail image file of the pteam service.

    Maximum file size: 512 KiB
    Supported media types: image/png
    """
    width_size = 720
    height_size = 480
    max_size = 512 * 1024
    error_filesize_exceeds_max = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Filesize exceeds max(512KiB)"
    )
    supported_media_types = {"image/png"}
    # https://www.iana.org/assignments/media-types/media-types.xhtml

    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # check without loading file
    if not uploaded.content_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Content-Type")
    media_type = uploaded.content_type.split(";", 1)[0].lower()
    if media_type not in supported_media_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported media type"
        )
    if uploaded.size is not None and uploaded.size > max_size:
        raise error_filesize_exceeds_max

    # load file data
    image_data = await uploaded.read()

    # check width, height size
    thumbnail_image = Image.open(io.BytesIO(image_data))
    width, height = thumbnail_image.size
    if width != width_size or height != height_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dimensions must be {width_size} x {height_size} px",
        )

    # check actual data size
    if len(image_data) > max_size:
        raise error_filesize_exceeds_max

    service.thumbnail = models.ServiceThumbnail(
        service_id=str(service_id), media_type=media_type, image_data=image_data
    )

    db.commit()

    return "OK"


@router.get("/{pteam_id}/services/{service_id}/thumbnail", response_class=Response)
def get_service_thumbnail(
    pteam_id: UUID,
    service_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get thumbnail image file of the pteam service.
    """

    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if service.thumbnail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No thumbnail")

    return Response(content=service.thumbnail.image_data, media_type=service.thumbnail.media_type)


@router.delete(
    "/{pteam_id}/services/{service_id}/thumbnail", status_code=status.HTTP_204_NO_CONTENT
)
def remove_service_thumbnail(
    pteam_id: UUID,
    service_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove thumbnail image file of the pteam service.
    """

    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    service.thumbnail = None

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _count_ssvc_priority_from_summary(tags_summary: list[dict]):
    ssvc_priority_count: dict[models.SSVCDeployerPriorityEnum, int] = {
        priority: 0 for priority in list(models.SSVCDeployerPriorityEnum)
    }
    for tag_summary in tags_summary:
        ssvc_priority_count[
            tag_summary["ssvc_priority"] or models.SSVCDeployerPriorityEnum.DEFER
        ] += 1
    return ssvc_priority_count


@router.get(
    "/{pteam_id}/services/{service_id}/tags/summary", response_model=schemas.PTeamServiceTagsSummary
)
def get_pteam_service_tags_summary(
    pteam_id: UUID,
    service_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tags summary of the pteam service.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not next(filter(lambda x: x.service_id == str(service_id), pteam.services), None):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # TODO Provisional Processing
    # tags_summary = command.get_tags_summary_by_service_id(db, service_id)
    tags_summary = []

    ssvc_priority_count = _count_ssvc_priority_from_summary(tags_summary)

    return {
        "ssvc_priority_count": ssvc_priority_count,
        "tags": tags_summary,
    }


@router.get("/{pteam_id}/tags/summary", response_model=schemas.PTeamTagsSummary)
def get_pteam_tags_summary(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tags summary of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # TODO Provisional Processing
    # tags_summary = command.get_tags_summary_by_pteam_id(db, pteam_id)
    tags_summary = []

    ssvc_priority_count = _count_ssvc_priority_from_summary(tags_summary)

    return {
        "ssvc_priority_count": ssvc_priority_count,
        "tags": tags_summary,
    }


@router.get(
    "/{pteam_id}/services/{service_id}/dependencies",
    response_model=list[schemas.DependencyResponse],
)
def get_dependencies(
    pteam_id: UUID,
    service_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE

    return service.dependencies


@router.get(
    "/{pteam_id}/services/{service_id}/dependencies/{dependency_id}",
    response_model=schemas.DependencyResponse,
)
def get_dependency(
    pteam_id: UUID,
    service_id: UUID,
    dependency_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not (
        dependency := next(
            filter(lambda x: x.dependency_id == str(dependency_id), service.dependencies), None
        )
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such dependency")

    return dependency


@router.get("/{pteam_id}/tags", response_model=list[schemas.ExtTagResponse])
def get_pteam_tags(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tags of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # TODO Provisional Processing
    # return get_pteam_ext_tags(pteam)
    return []


@router.get(
    "/{pteam_id}/services/{service_id}/tags/{tag_id}/topic_ids",
    response_model=schemas.ServiceTaggedTopicsSolvedUnsolved,
)
def get_service_tagged_topic_ids(
    pteam_id: UUID,
    service_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    # TODO Provisional Processing
    # if not persistence.get_tag_by_id(db, tag_id):
    # raise NO_SUCH_TAG
    if not persistence.get_dependency_from_service_id_and_tag_id(db, service_id, tag_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service tag")

    ## sovled
    topic_ids_summary = get_topic_ids_summary_by_service_id_and_tag_id(service, tag_id)

    return {
        "pteam_id": pteam_id,
        "service_id": service_id,
        "tag_id": tag_id,
        **topic_ids_summary,
    }


@router.get(
    "/{pteam_id}/services/{service_id}/ticketstatus/{ticket_id}",
    response_model=schemas.TicketStatusResponse,
)
def get_ticket_status(
    pteam_id: UUID,
    service_id: UUID,
    ticket_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current status of the ticket.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not (ticket := persistence.get_ticket_by_id(db, ticket_id)):
        raise NO_SUCH_TICKET
    if ticket.threat.dependency.service_id != str(service_id):
        raise NO_SUCH_TICKET

    return ticket.ticket_status


@router.put(
    "/{pteam_id}/services/{service_id}/ticketstatus/{ticket_id}",
    response_model=schemas.TicketStatusResponse,
)
def set_ticket_status(
    pteam_id: UUID,
    service_id: UUID,
    ticket_id: UUID,
    data: schemas.TicketStatusRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set status of the ticket.
    Current value should be inherited if not specified.

    scheduled_at is necessary to make topic_status "scheduled".
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not (ticket := persistence.get_ticket_by_id(db, ticket_id)):
        raise NO_SUCH_TICKET
    if ticket.threat.dependency.service_id != str(service_id):
        raise NO_SUCH_TICKET

    update_data = data.model_dump(exclude_unset=True)

    if "topic_status" in update_data.keys() and data.topic_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for topic_status",
        )
    if "logging_ids" in update_data.keys() and data.logging_ids is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for logging_ids",
        )
    if "assignees" in update_data.keys() and data.assignees is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for assignees",
        )

    if data.topic_status == models.TopicStatusType.alerted:
        # user cannot set alerted
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")

    now = datetime.now()
    if data.scheduled_at:
        data_scheduled_at = data.scheduled_at.replace(tzinfo=None)

    if data.topic_status == models.TopicStatusType.scheduled or (
        "topic_status" not in update_data.keys()
        and ticket.ticket_status.topic_status == models.TopicStatusType.scheduled
    ):
        if "scheduled_at" not in update_data.keys():
            if ticket.ticket_status.topic_status != models.TopicStatusType.scheduled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="If status is scheduled, specify schduled_at",
                )
        else:
            if data.scheduled_at is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="If status is scheduled, unable to reset schduled_at",
                )
            elif data_scheduled_at < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="If status is scheduled, schduled_at must be a future time",
                )
    else:
        if "scheduled_at" not in update_data.keys():
            if ticket.ticket_status.topic_status == models.TopicStatusType.scheduled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "If current status is not scheduled and previous status is schduled, "
                        "need to reset schduled_at"
                    ),
                )
        else:
            if data.scheduled_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="If status is not scheduled, do not specify schduled_at",
                )

    for logging_id_ in data.logging_ids or []:
        if not (log := persistence.get_action_log_by_id(db, logging_id_)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such actionlog",
            )
        if log.ticket_id != str(ticket_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not an actionlog for the ticket",
            )
    for assignee in data.assignees or []:
        if not (a_user := persistence.get_account_by_id(db, assignee)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such user",
            )
        if not check_pteam_membership(pteam, a_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a pteam member",
            )

    # update only if required
    if "assignees" in update_data.keys() and data.assignees is not None:
        ticket.ticket_status.assignees = list(map(str, data.assignees))
    elif ticket.ticket_status.assignees == []:
        ticket.ticket_status.assignees = [UUID(current_user.user_id)]
    if "topic_status" in update_data.keys():
        ticket.ticket_status.topic_status = data.topic_status
    elif ticket.ticket_status.topic_status == models.TopicStatusType.alerted:
        # this is the first update
        ticket.ticket_status.topic_status = models.TopicStatusType.acknowledged
    if "logging_ids" in update_data.keys() and data.logging_ids is not None:
        ticket.ticket_status.logging_ids = list(map(str, data.logging_ids))
    if "note" in update_data.keys():
        ticket.ticket_status.note = data.note
    if "scheduled_at" in update_data.keys():
        if data.scheduled_at is None:
            ticket.ticket_status.scheduled_at = None
        elif (
            data_scheduled_at > now
            and ticket.ticket_status.topic_status == models.TopicStatusType.scheduled
        ):
            ticket.ticket_status.scheduled_at = data.scheduled_at

    # set last updated by
    ticket.ticket_status.user_id = current_user.user_id

    db.commit()

    return ticket.ticket_status


@router.get(
    "/{pteam_id}/services/{service_id}/topics/{topic_id}/tags/{tag_id}/tickets",
    response_model=list[schemas.TicketResponse],
)
def get_tickets_with_status_by_service_id_and_topic_id(
    pteam_id: UUID,
    service_id: UUID,
    topic_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tickets (with status) related to the service, topic and tag.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    # TODO Provisional Processing
    # if not persistence.get_topic_by_id(db, topic_id):
    #     raise NO_SUCH_TOPIC
    # if not persistence.get_tag_by_id(db, tag_id):
    # raise NO_SUCH_TAG

    tickets = command.get_sorted_tickets_related_to_service_and_topic_and_tag(
        db, service_id, topic_id, tag_id
    )

    ret = [
        {
            **ticket.__dict__,
            "threat": ticket.threat.__dict__,
            "ticket_status": ticket.ticket_status.__dict__,
        }
        for ticket in tickets
    ]
    return ret


@router.get("/{pteam_id}/topics", response_model=list[schemas.TopicResponse])
def get_pteam_topics(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topics of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    if not pteam.tags:
        return []
    # TODO Provisional Processing
    # topic_tag_ids = get_tag_ids_with_parent_ids(pteam.tags)

    # TODO Provisional Processing
    # return get_sorted_topics(persistence.get_topics_by_tag_ids(db, topic_tag_ids))
    return []


@router.post("", response_model=schemas.PTeamInfo)
def create_pteam(
    data: schemas.PTeamCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a pteam.

    `tags` is optional, the default is an empty list.
    """

    if data.alert_slack and data.alert_slack.webhook_url:
        validate_slack_webhook_url(data.alert_slack.webhook_url)
    pteam = models.PTeam(
        pteam_name=data.pteam_name.strip(),
        contact_info=data.contact_info.strip(),
        alert_ssvc_priority=data.alert_ssvc_priority,
    )
    pteam.alert_slack = models.PTeamSlack(
        pteam_id=pteam.pteam_id,
        enable=data.alert_slack.enable if data.alert_slack else True,
        webhook_url=data.alert_slack.webhook_url if data.alert_slack else "",
    )
    pteam.alert_mail = models.PTeamMail(
        pteam_id=pteam.pteam_id,
        enable=data.alert_mail.enable if data.alert_mail else True,
        address=data.alert_mail.address if data.alert_mail else "",
    )
    persistence.create_pteam(db, pteam)

    # join to the created pteam and set default authority
    user_auth = models.PTeamAccountRole(
        pteam_id=pteam.pteam_id, user_id=current_user.user_id, is_admin=True
    )

    persistence.create_pteam_account_role(db, user_auth)

    db.commit()

    return pteam


def _check_file_extention(file: UploadFile, extention: str):
    """
    Error when file don't have a specified extention
    """
    if file.filename is None or not file.filename.endswith(extention):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please upload a file with {extention} as extension",
        )


def _check_empty_file(file: UploadFile):
    """
    Error when file is empty
    """
    if len(file.file.read().decode()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload file is empty",
        )
    file.file.seek(0)  # move the cursor back to the beginning


def _json_loads(s: str | bytes | bytearray):
    try:
        return json.loads(s)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Wrong file content: " + f'{s[:32]!s}{"..." if len(s) > 32 else ""}'),
        ) from error


def bg_create_tags_from_sbom_json(
    sbom_json: dict,
    pteam_id: UUID | str,
    service_name: str,
    force_mode: bool,
    filename: str | None,
):
    # TODO
    #   functions for background tasks should be divided to another source file.

    log = logging.getLogger(__name__)
    log.info(f"Start SBOM uploade as a service: {service_name}")

    with open_db_session() as db:
        if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
            # TODO: cannot notify error without pteam
            raise ValueError(f"Invalid pteam_id: {pteam_id}")
        if not (
            service := next(filter(lambda x: x.service_name == service_name, pteam.services), None)
        ):
            service = models.Service(pteam_id=str(pteam_id), service_name=service_name)
            pteam.services.append(service)
            db.flush()

        try:
            json_lines = sbom_json_to_artifact_json_lines(sbom_json)
            apply_service_packages(db, service, json_lines, auto_create_packages=force_mode)
        except ValueError:
            notify_sbom_upload_ended(service, filename, False)
            log.error(f"Failed uploading SBOM as a service: {service_name}")
            return

        now = datetime.now()
        service.sbom_uploaded_at = now

        db.commit()

        notify_sbom_upload_ended(service, filename, True)
        log.info(f"SBOM uploaded as a service: {service_name}")


@router.post("/{pteam_id}/upload_sbom_file")
async def upload_pteam_sbom_file(
    pteam_id: UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: str = Query("", description="name of service(repository or product)"),
    force_mode: bool = Query(False, description="if true, create unexist tags"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    upload sbom file
    """
    if len(service) > 255:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Length of Service name exceeds 255 characters",
        )

    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing service_name")
    _check_file_extention(file, ".json")
    _check_empty_file(file)

    sbom_sha256 = sha256()
    while data := await file.read(DEFAULT_BUFFER_SIZE):
        sbom_sha256.update(BytesIO(data).getbuffer())
    ret = {
        "pteam_id": pteam_id,
        "service_name": service,
        "sbom_file_sha256": sbom_sha256.hexdigest(),
    }

    try:
        await file.seek(0)
        sbom_json = json.load(file.file)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Wrong file content"),
        ) from error

    background_tasks.add_task(
        bg_create_tags_from_sbom_json, sbom_json, pteam_id, service, force_mode, file.filename
    )
    return ret


@router.post("/{pteam_id}/upload_tags_file", response_model=list[schemas.ExtTagResponse])
def upload_pteam_tags_file(
    pteam_id: UUID,
    file: UploadFile,
    service: str = Query("", description="name of service(repository or product)"),
    force_mode: bool = Query(False, description="if true, create unexist tags"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update pteam tags by uploading a .jsonl file.

    Format of file content must be JSON Lines.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing service_name")
    _check_file_extention(file, ".jsonl")
    _check_empty_file(file)

    # Read from file
    json_lines = []
    for bline in file.file:
        json_lines.append(_json_loads(bline))

    if not (
        service_model := next(filter(lambda x: x.service_name == service, pteam.services), None)
    ):
        service_model = models.Service(pteam_id=pteam_id, service_name=service)
        pteam.services.append(service_model)
        db.flush()

    try:
        apply_service_tags(db, service_model, json_lines, auto_create_tags=force_mode)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    now = datetime.now()
    service_model.sbom_uploaded_at = now

    db.commit()

    # TODO Provisional Processing
    # return get_pteam_ext_tags(pteam)
    return []


def apply_service_packages(
    db: Session,
    service: models.Service,
    json_lines: list[dict],
    auto_create_packages=False,
) -> None:
    # Check file format and get tag_names
    missing_packages: set[str] = set()
    new_dependencies_set: set[tuple[str, str, str]] = (
        set()
    )  # (package_version_id, target, package_manager)
    for line in json_lines:
        if not (package_name := str(line.get("package_name"))):
            raise ValueError("Missing  package name")
        if not (ecosystem := str(line.get("ecosystem"))):
            raise ValueError("Missing ecosystem")
        if not (package_manager := str(line.get("package_manager"))):
            raise ValueError("Missing package_manager")
        if not (_refs := line.get("references")):
            raise ValueError("Missing references")
        if any(None in {_ref.get("target"), _ref.get("version")} for _ref in _refs):
            raise ValueError("Missing target and|or version")
        if not (
            _package := persistence.get_package_by_name_and_ecosystem(db, package_name, ecosystem)
        ):
            if auto_create_packages:
                # create new package
                _package = models.Package(name=package_name, ecosystem=ecosystem)
                persistence.create_package(db, _package)

            else:
                missing_packages.add(package_name + ":" + ecosystem)

        if _package:
            for ref in line.get("references", [{}]):
                if not (
                    _package_version := persistence.get_package_version_by_package_id_and_version(
                        db, _package.package_id, ref.get("version", "")
                    )
                ):
                    # create new package version
                    _package_version = models.PackageVersion(
                        package_id=_package.package_id,
                        version=ref.get("version", ""),
                    )
                    persistence.create_package_version(db, _package_version)
                new_dependencies_set.add(
                    (_package_version.package_version_id, ref.get("target", ""), package_manager)
                )

    if missing_packages:
        raise ValueError(f"No such packages: {', '.join(sorted(missing_packages))}")

    # separate dependencis to keep, delete or create
    obsoleted_dependencies = []
    for dependency in service.dependencies:
        if (
            item := (dependency.package_version_id, dependency.target, dependency.package_manager)
        ) in new_dependencies_set:
            new_dependencies_set.remove(item)  # already exists
            continue
        obsoleted_dependencies.append(dependency)
    for obsoleted in obsoleted_dependencies:
        service.dependencies.remove(obsoleted)
    # create new dependencies
    for [package_version_id, target, package_manager] in new_dependencies_set:
        new_dependency = models.Dependency(
            service_id=service.service_id,
            package_version_id=package_version_id,
            target=target,
            package_manager=package_manager,
        )
        service.dependencies.append(new_dependency)
        db.flush()
        # TODO Provisional Processing
        # fix_threats_for_dependency(db, new_dependency)
    db.flush()


@router.delete("/{pteam_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_service(
    pteam_id: UUID,
    service_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove service.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)) or service.pteam_id != str(
        pteam_id
    ):
        # do not raise error even if specified service does not exist
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    pteam.services.remove(service)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{pteam_id}", response_model=schemas.PTeamInfo)
def update_pteam(
    pteam_id: UUID,
    data: schemas.PTeamUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a pteam.

    Note: monitoring tags cannot be update with this api. use (add|update|remove)_pteamtag instead.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    update_data = data.model_dump(exclude_unset=True)
    if "pteam_name" in update_data.keys() and data.pteam_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for pteam_name",
        )
    if "contact_info" in update_data.keys() and data.contact_info is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for contact_info",
        )
    if "alert_slack" in update_data.keys() and data.alert_slack is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for alert_slack",
        )
    if "alert_ssvc_priority" in update_data.keys() and data.alert_ssvc_priority is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for alert_ssvc_priority",
        )
    if "alert_mail" in update_data.keys() and data.alert_mail is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify None for alert_mail",
        )

    if data.alert_slack and data.alert_slack.webhook_url:
        validate_slack_webhook_url(data.alert_slack.webhook_url)
        pteam.alert_slack = models.PTeamSlack(
            pteam_id=pteam.pteam_id,
            enable=data.alert_slack.enable,
            webhook_url=data.alert_slack.webhook_url,
        )
    elif data.alert_slack and data.alert_slack.webhook_url == "":
        pteam.alert_slack = models.PTeamSlack(
            pteam_id=pteam.pteam_id,
            enable=data.alert_slack.enable,
            webhook_url="",
        )

    if data.pteam_name is not None:
        pteam.pteam_name = data.pteam_name
    if data.contact_info is not None:
        pteam.contact_info = data.contact_info
    if data.alert_ssvc_priority is not None:
        pteam.alert_ssvc_priority = data.alert_ssvc_priority
    if data.alert_mail is not None:
        pteam.alert_mail = models.PTeamMail(**data.alert_mail.__dict__)

    db.commit()

    return pteam


@router.get("/{pteam_id}/members", response_model=list[schemas.UserResponse])
def get_pteam_members(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get members of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    return pteam.members


@router.put("/{pteam_id}/members/{user_id}", response_model=schemas.PTeamMemberResponse)
def update_pteam_member(
    pteam_id: UUID,
    user_id: UUID,
    data: schemas.PTeamMemberRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not (user := persistence.get_pteam_account_role(db, pteam_id, user_id)):
        raise NOT_A_PTEAM_MEMBER
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    user.is_admin = data.is_admin
    db.flush()

    if data.is_admin is False and command.missing_pteam_admin(db, pteam):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )

    db.commit()

    return {"pteam_id": pteam_id, "user_id": user_id, "is_admin": user.is_admin}


@router.delete("/{pteam_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    pteam_id: UUID,
    user_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    User leaves the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if current_user.user_id != str(user_id) and not check_pteam_admin_authority(
        db, pteam, current_user
    ):
        raise NOT_HAVE_AUTH

    # remove from members
    target_role = persistence.get_pteam_account_role(db, pteam_id, user_id)
    if target_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam member")
    pteam.pteam_roles.remove(target_role)

    db.flush()
    if command.missing_pteam_admin(db, pteam):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.post("/{pteam_id}/invitation", response_model=schemas.PTeamInvitationResponse)
def create_invitation(
    pteam_id: UUID,
    request: schemas.PTeamInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new pteam invitation token.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    if request.limit_count is not None and request.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give Null for unlimited)",
        )

    command.expire_pteam_invitations(db)

    invitation = models.PTeamInvitation(
        **request.model_dump(),
        pteam_id=str(pteam_id),
        user_id=current_user.user_id,
    )
    persistence.create_pteam_invitation(db, invitation)

    ret = {
        **invitation.__dict__,  # cannot get after db.commit() without refresh
    }

    db.commit()

    return ret


@router.get("/{pteam_id}/invitation", response_model=list[schemas.PTeamInvitationResponse])
def list_invitations(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    list effective invitations.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    command.expire_pteam_invitations(db)
    # do not commit within GET method

    return [
        {**invitation.__dict__} for invitation in persistence.get_pteam_invitations(db, pteam_id)
    ]


@router.delete("/{pteam_id}/invitation/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invitation(
    pteam_id: UUID,
    invitation_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    command.expire_pteam_invitations(db)

    invitation = persistence.get_pteam_invitation_by_id(db, invitation_id)
    if invitation:  # can be expired before deleting
        persistence.delete_pteam_invitation(db, invitation)

    db.commit()  # commit not only deleted but also expired

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.delete("/{pteam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pteam(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_admin_authority(db, pteam, current_user):
        raise NOT_HAVE_AUTH

    persistence.delete_pteam(db, pteam)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
