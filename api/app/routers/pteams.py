import json
from datetime import datetime
from hashlib import sha256
from io import DEFAULT_BUFFER_SIZE, BytesIO
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.alert import notify_sbom_upload_ended
from app.auth import get_current_user
from app.common import (
    check_pteam_auth,
    check_pteam_membership,
    count_threat_impact_from_summary,
    create_topic_tag,
    fix_threats_for_dependency,
    get_pteam_ext_tags,
    get_sorted_topics,
    get_tag_ids_with_parent_ids,
    get_topic_ids_summary_by_service_id_and_tag_id,
)
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID
from app.database import get_db, open_db_session
from app.sbom import sbom_json_to_artifact_json_lines
from app.slack import validate_slack_webhook_url

router = APIRouter(prefix="/pteams", tags=["pteams"])


NOT_A_PTEAM_MEMBER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not a pteam member",
)
NOT_HAVE_AUTH = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have authority",
)
NO_SUCH_ATEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ateam")
NO_SUCH_PTEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
NO_SUCH_TOPIC = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
NO_SUCH_TAG = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")
NO_SUCH_SERVICE = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service")
NO_SUCH_PTEAM_TAG = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")
NO_SUCH_TICKET = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ticket")


@router.get("", response_model=list[schemas.PTeamEntry])
def get_pteams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all pteams list.
    """
    return persistence.get_all_pteams(db)


@router.get("/auth_info", response_model=schemas.PTeamAuthInfo)
def get_auth_info(current_user: models.Account = Depends(get_current_user)):
    """
    Get pteam authority information.
    """
    return schemas.PTeamAuthInfo(
        authorities=[
            schemas.PTeamAuthInfo.PTeamAuthEntry(
                enum=key, name=str(value["name"]), desc=str(value["desc"])
            )
            for key, value in models.PTeamAuthEnum.info().items()
        ],
        pseudo_uuids=[
            schemas.PTeamAuthInfo.PseudoUUID(name="member", uuid=MEMBER_UUID),
            schemas.PTeamAuthInfo.PseudoUUID(name="others", uuid=NOT_MEMBER_UUID),
        ],
    )


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
    invitation.pteam.members.append(current_user)

    if invitation.authority:  # invitation with authority
        # Note: non-members never have pteam auth
        pteam_auth = models.PTeamAuthority(
            pteam_id=invitation.pteam_id,
            user_id=current_user.user_id,
            authority=invitation.authority,
        )
        persistence.create_pteam_authority(db, pteam_auth)

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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return pteam


@router.get("/{pteam_id}/services", response_model=list[schemas.PTeamServiceResponse])
def get_pteam_services(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return sorted(pteam.services, key=lambda x: x.service_name)


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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    tags_summary = command.get_tags_summary_by_service_id(db, service_id)

    threat_impact_count = count_threat_impact_from_summary(tags_summary)

    return {
        "threat_impact_count": threat_impact_count,
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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    tags_summary = command.get_tags_summary_by_pteam_id(db, pteam_id)

    threat_impact_count = count_threat_impact_from_summary(tags_summary)

    return {
        "threat_impact_count": threat_impact_count,
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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE

    return service.dependencies


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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return get_pteam_ext_tags(db, pteam)


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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not persistence.get_tag_by_id(db, tag_id):
        raise NO_SUCH_TAG
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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not (ticket := persistence.get_ticket_by_id(db, ticket_id)):
        raise NO_SUCH_TICKET
    if ticket.threat.dependency.service_id != str(service_id):
        raise NO_SUCH_TICKET

    fixed_status = (
        {**ticket.current_ticket_status.ticket_status.__dict__}
        if ticket.current_ticket_status and ticket.current_ticket_status.ticket_status
        else {"ticket_id": ticket_id}  # all params except ticket_id are default
    )
    return fixed_status


@router.post(
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
    Current status should be inherited if requested value is None.

    To clear scheduled_at give datetime.fromtimestamp(0) to scheduled_at.

    scheduled_at is necessary to make topic_status "scheduled".
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not (ticket := persistence.get_ticket_by_id(db, ticket_id)):
        raise NO_SUCH_TICKET
    if ticket.threat.dependency.service_id != str(service_id):
        raise NO_SUCH_TICKET

    if data.topic_status == models.TopicStatusType.alerted:
        # user cannot set alerted
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")
    if data.topic_status == models.TopicStatusType.scheduled and not data.scheduled_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="If statsu is schduled, specify schduled_at",
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
        if not check_pteam_membership(db, pteam, a_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a pteam member",
            )

    current_ticket_status = ticket.current_ticket_status
    fixed_assignees: list[str] | None = None
    if (
        current_ticket_status.topic_status == models.TopicStatusType.alerted
        and data.topic_status == models.TopicStatusType.acknowledged
        and not data.assignees
    ):
        # force assign current_user if no assignees given for the 1st ack
        fixed_assignees = [current_user.user_id]
    elif data.assignees is not None:
        fixed_assignees = list(map(str, data.assignees))

    # create base status inheriting current status
    if _current := current_ticket_status.ticket_status:
        new_status = models.TicketStatus(
            ticket_id=str(ticket_id),
            user_id=current_user.user_id,
            topic_status=_current.topic_status,
            note=_current.note,
            logging_ids=_current.logging_ids,
            assignees=_current.assignees,
            scheduled_at=_current.scheduled_at,
            created_at=datetime.now(),
        )
    else:
        new_status = models.TicketStatus(
            ticket_id=str(ticket_id),
            topic_status=models.TopicStatusType.alerted,
            user_id=current_user.user_id,
        )
    # overwrite only if required
    if fixed_assignees is not None:
        new_status.assignees = fixed_assignees
    if data.topic_status is not None:
        new_status.topic_status = data.topic_status
    if data.logging_ids is not None:
        new_status.logging_ids = list(map(str, data.logging_ids))
    if data.note is not None:
        new_status.note = data.note
    if data.scheduled_at is not None:
        if data.scheduled_at == datetime.fromtimestamp(0):
            new_status.scheduled_at = None
        else:
            new_status.scheduled_at = data.scheduled_at

    persistence.create_ticket_status(db, new_status)
    ret_status = {**new_status.__dict__}

    # update current_status
    current_ticket_status.status_id = new_status.status_id
    current_ticket_status.topic_status = new_status.topic_status

    db.commit()

    return ret_status


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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    if not persistence.get_tag_by_id(db, tag_id):
        raise NO_SUCH_TAG

    tickets = command.get_sorted_tickets_related_to_service_and_topic_and_tag(
        db, service_id, topic_id, tag_id
    )

    ret = [
        {
            **ticket.__dict__,
            "threat": ticket.threat.__dict__,
            "current_ticket_status": (
                {**ticket.current_ticket_status.ticket_status.__dict__}
                if ticket.current_ticket_status and ticket.current_ticket_status.ticket_status
                else {"ticket_id": ticket.ticket_id}
            ),
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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    if not pteam.tags:
        return []
    topic_tag_ids = get_tag_ids_with_parent_ids(pteam.tags)
    return get_sorted_topics(persistence.get_topics_by_tag_ids(db, topic_tag_ids))


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
        alert_threat_impact=data.alert_threat_impact,
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

    # join to the created pteam
    pteam.members.append(current_user)

    # set default authority
    user_auth = models.PTeamAuthority(
        pteam_id=pteam.pteam_id,
        user_id=current_user.user_id,
        authority=models.PTeamAuthIntFlag.PTEAM_MASTER,
    )
    member_auth = models.PTeamAuthority(
        pteam_id=pteam.pteam_id,
        user_id=str(MEMBER_UUID),
        authority=models.PTeamAuthIntFlag.PTEAM_MEMBER,
    )
    not_member_auth = models.PTeamAuthority(
        pteam_id=pteam.pteam_id,
        user_id=str(NOT_MEMBER_UUID),
        authority=models.PTeamAuthIntFlag.FREE_TEMPLATE,
    )
    persistence.create_pteam_authority(db, user_auth)
    persistence.create_pteam_authority(db, member_auth)
    persistence.create_pteam_authority(db, not_member_auth)

    db.commit()

    return pteam


@router.post("/{pteam_id}/authority", response_model=list[schemas.PTeamAuthResponse])
def update_pteam_auth(
    pteam_id: UUID,
    requests: list[schemas.PTeamAuthRequest],
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update pteam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : pteam member
      - 00000000-0000-0000-0000-0000cafe0002 : not pteam member
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    str_ids = [str(request.user_id) for request in requests]
    if len(set(str_ids)) != len(str_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous request")

    response = []
    for request in requests:
        if (user_id := str(request.user_id)) in list(map(str, [MEMBER_UUID, NOT_MEMBER_UUID])):
            if "admin" in request.authorities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot give ADMIN to pseudo account",
                )
        else:
            if not (user := persistence.get_account_by_id(db, user_id)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user id",
                )
            if not check_pteam_membership(db, pteam, user, ignore_ateam=True):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not a pteam member",
                )
        if not (auth := persistence.get_pteam_authority(db, pteam_id, user_id)):
            auth = models.PTeamAuthority(
                pteam_id=str(pteam_id),
                user_id=user_id,
                authority=0,  # fix later
            )
            persistence.create_pteam_authority(db, auth)
        auth.authority = models.PTeamAuthIntFlag.from_enums(request.authorities)

    db.flush()
    if command.missing_pteam_admin(db, pteam):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )

    db.commit()

    for request in requests:
        auth = persistence.get_pteam_authority(db, pteam_id, request.user_id)
        response.append(
            {
                "user_id": request.user_id,
                "authorities": models.PTeamAuthIntFlag(auth.authority).to_enums() if auth else [],
            }
        )
    return response


@router.get("/{pteam_id}/authority", response_model=list[schemas.PTeamAuthResponse])
def get_pteam_auth(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pteam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : pteam member
      - 00000000-0000-0000-0000-0000cafe0002 : not pteam member
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM

    if current_user in pteam.members:  # member can get all authorities
        authorities = persistence.get_pteam_all_authorities(db, pteam_id)
    else:  # not member can get only for NOT_MEMBER_UUID
        auth_for_not_member = persistence.get_pteam_authority(db, pteam_id, NOT_MEMBER_UUID)
        authorities = [auth_for_not_member] if auth_for_not_member else []

    response = []
    for auth in authorities:
        enums = models.PTeamAuthIntFlag(auth.authority).to_enums()
        response.append({"user_id": auth.user_id, "authorities": enums})
    return response


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
            apply_service_tags(db, service, json_lines, auto_create_tags=force_mode)
        except ValueError:
            notify_sbom_upload_ended(service, filename, False)
            return

        now = datetime.now()
        service.sbom_uploaded_at = now

        db.commit()

        notify_sbom_upload_ended(service, filename, True)


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
    if not check_pteam_membership(db, pteam, current_user):
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
    if not check_pteam_membership(db, pteam, current_user):
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

    return get_pteam_ext_tags(db, pteam)


def apply_service_tags(
    db: Session,
    service: models.Service,
    json_lines: list[dict],
    auto_create_tags=False,
) -> None:
    # Check file format and get tag_names
    missing_tags = set()
    new_dependencies_set: set[tuple[str, str, str]] = set()  # (tag_id, target, version)
    for line in json_lines:
        if not (_tag_name := line.get("tag_name")):
            raise ValueError("Missing tag_name")
        if not (_refs := line.get("references")):
            raise ValueError("Missing references")
        if any(None in {_ref.get("target"), _ref.get("version")} for _ref in _refs):
            raise ValueError("Missing target and|or version")
        if not (_tag := persistence.get_tag_by_name(db, _tag_name)):
            if auto_create_tags:
                _tag = create_topic_tag(db, _tag_name)
            else:
                missing_tags.add(_tag_name)
        if _tag:
            for ref in line.get("references", [{}]):
                new_dependencies_set.add(
                    (_tag.tag_id, ref.get("target", ""), ref.get("version", ""))
                )
    if missing_tags:
        raise ValueError(f"No such tags: {', '.join(sorted(missing_tags))}")

    # separate dependencis to keep, delete or create
    obsoleted_dependencies = []
    for dependency in service.dependencies:
        if (
            item := (dependency.tag_id, dependency.target, dependency.version)
        ) in new_dependencies_set:
            new_dependencies_set.remove(item)  # already exists
            continue
        obsoleted_dependencies.append(dependency)
    for obsoleted in obsoleted_dependencies:
        service.dependencies.remove(obsoleted)
    # create new dependencies
    for [tag_id, target, version] in new_dependencies_set:
        new_dependency = models.Dependency(
            service_id=service.service_id,
            tag_id=tag_id,
            version=version,
            target=target,
        )
        service.dependencies.append(new_dependency)
        db.flush()
        fix_threats_for_dependency(db, new_dependency)
    db.flush()


@router.delete("/{pteam_id}/tags", status_code=status.HTTP_204_NO_CONTENT)
def remove_pteam_tags_by_service(
    pteam_id: UUID,
    service: str = Query("", description="name of service(repository or product)"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove pteam tags filtered by service.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    if not (
        service_model := next(filter(lambda x: x.service_name == service, pteam.services), None)
    ):
        # do not raise error even if specified service does not exist
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    pteam.services.remove(service_model)

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
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH
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
    if data.alert_threat_impact is not None:
        pteam.alert_threat_impact = data.alert_threat_impact
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
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    return pteam.members


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
    if current_user.user_id != str(user_id) and not check_pteam_auth(
        db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN
    ):
        raise NOT_HAVE_AUTH

    target_users = [x for x in pteam.members if x.user_id == str(user_id)]
    if len(target_users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam member")

    # remove all extra authorities  # FIXME: should be deleted on cascade
    if auth := persistence.get_pteam_authority(db, pteam_id, user_id):
        command.workaround_delete_pteam_authority(db, auth)

    # remove from members
    pteam.members.remove(target_users[0])

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
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH
    # only ADMIN can set authorities to the invitation
    if request.authorities is not None and not check_pteam_auth(
        db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADMIN required to set authorities"
        )
    intflag = models.PTeamAuthIntFlag.from_enums(request.authorities or [])
    if request.limit_count is not None and request.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give Null for unlimited)",
        )

    command.expire_pteam_invitations(db)

    del request.authorities
    invitation = models.PTeamInvitation(
        **request.model_dump(),
        pteam_id=str(pteam_id),
        user_id=current_user.user_id,
        authority=intflag,
    )
    persistence.create_pteam_invitation(db, invitation)

    ret = {
        **invitation.__dict__,  # cannot get after db.commit() without refresh
        "authorities": models.PTeamAuthIntFlag(invitation.authority).to_enums(),
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
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH

    command.expire_pteam_invitations(db)
    # do not commit within GET method

    return [
        {
            **invitation.__dict__,
            "authorities": models.PTeamAuthIntFlag(invitation.authority).to_enums(),
        }
        for invitation in persistence.get_pteam_invitations(db, pteam_id)
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
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH

    command.expire_pteam_invitations(db)

    invitation = persistence.get_pteam_invitation_by_id(db, invitation_id)
    if invitation:  # can be expired before deleting
        persistence.delete_pteam_invitation(db, invitation)

    db.commit()  # commit not only deleted but also expired

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.get("/{pteam_id}/watchers", response_model=list[schemas.ATeamEntry])
def get_pteam_watchers(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get watching pteams of the ateam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return pteam.ateams


@router.delete("/{pteam_id}/watchers/{ateam_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watcher_ateam(
    pteam_id: UUID,
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove ateam from watchers list.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if ateam in pteam.ateams:  # ignore removing not-watcher
        pteam.ateams.remove(ateam)
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
