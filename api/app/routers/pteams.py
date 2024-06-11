import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas, ticket_manager
from app.auth import get_current_user
from app.common import (
    auto_close_by_pteamtags,
    check_pteam_auth,
    check_pteam_membership,
    count_service_solved_tickets_per_threat_impact,
    count_service_unsolved_tickets_per_threat_impact,
    get_or_create_topic_tag,
    get_pteam_ext_tags,
    get_sorted_solved_ticket_ids_by_service_tag_and_status,
    get_sorted_topics,
    get_sorted_unsolved_ticket_ids_by_service_tag_and_status,
    get_tag_ids_with_parent_ids,
    pteamtag_try_auto_close_topic,
    set_pteam_topic_status_internal,
)
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID
from app.database import get_db
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
    if not (
        service := next(filter(lambda x: x.service_id == str(service_id), pteam.services), None)
    ):
        raise NO_SUCH_SERVICE
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    tags_summary: dict[str, dict] = {}  # {tag_id: tag_summary}
    for dependency in service.dependencies:
        tag = dependency.tag
        # init tag summary if not yet
        if not (tag_summary := tags_summary.get(tag.tag_id)):
            tag_summary = {
                "tag_id": tag.tag_id,
                "tag_name": tag.tag_name,
                "parent_id": tag.parent_id,
                "parent_name": tag.parent_name,
                "references": [],
                "threat_impact": None,
                "updated_at": None,
                "status_count": {
                    status_type.value: 0 for status_type in list(models.TopicStatusType)
                },
            }
            tags_summary[tag.tag_id] = tag_summary
        # apply dependency
        tag_summary["references"].append(
            {
                "target": dependency.target,
                "version": dependency.version,
                "service": service.service_name,
            }
        )
        # apply threat and current ticket status
        for threat in dependency.threats:
            if not (ticket := threat.ticket):  # ignore threats if not have ticket
                continue
            topic = threat.topic
            if (
                tag_summary["threat_impact"] is None
                or tag_summary["threat_impact"] > topic.threat_impact
            ):
                tag_summary["threat_impact"] = topic.threat_impact
            if tag_summary["updated_at"] is None or tag_summary["updated_at"] < topic.updated_at:
                tag_summary["updated_at"] = topic.updated_at
            fixed_ticket_status = (
                models.TopicStatusType.alerted
                if (
                    not (current_ticket_status := ticket.current_ticket_status)
                    or current_ticket_status.topic_status is None
                )
                else current_ticket_status.topic_status
            )
            tag_summary["status_count"][fixed_ticket_status] += 1

    # count tags threat_impact
    threat_impact_count: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0}
    for tag_summary in tags_summary.values():
        threat_impact_count[str(tag_summary["threat_impact"] or 4)] += 1

    return {
        "threat_impact_count": threat_impact_count,
        "tags": sorted(
            list(tags_summary.values()),
            key=lambda x: (
                x["threat_impact"] or 4,
                -(_dt.timestamp() if (_dt := x.get("updated_at")) else 0),
                x["tag_name"],
            ),
        ),
    }


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


@router.get("/{pteam_id}/tags/summary", response_model=schemas.PTeamTagsSummary)
def get_pteam_tags_summary(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary of the pteam tags.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return command.get_pteam_tags_summary(db, pteam)


@router.get("/{pteam_id}/tags/{tag_id}/solved_topic_ids", response_model=schemas.PTeamTaggedTopics)
def get_pteam_tagged_solved_topic_ids(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tagged and solved topic id list of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    topic_ids = command.get_sorted_topic_ids_by_pteam_tag_and_status(db, pteam_id, tag_id, True)
    threat_impact_count = command.count_pteam_topics_per_threat_impact(db, pteam_id, tag_id, True)

    return {
        "pteam_id": pteam_id,
        "tag_id": tag_id,
        "topic_ids": topic_ids,
        "threat_impact_count": threat_impact_count,
    }


@router.get(
    "/{pteam_id}/tags/{tag_id}/unsolved_topic_ids", response_model=schemas.PTeamTaggedTopics
)
def get_pteam_tagged_unsolved_topic_ids(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tagged and unsolved topic id list of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    topic_ids = command.get_sorted_topic_ids_by_pteam_tag_and_status(db, pteam_id, tag_id, False)
    threat_impact_count = command.count_pteam_topics_per_threat_impact(db, pteam_id, tag_id, False)

    return {
        "pteam_id": pteam_id,
        "tag_id": tag_id,
        "threat_impact_count": threat_impact_count,
        "topic_ids": topic_ids,
    }


@router.get(
    "/{pteam_id}/services/{service_id}/tags/{tag_id}/ticket_ids",
    response_model=schemas.ServiceTaggedTopicsSolvedUnsolved,
)
def get_service_tagged_ticket_ids(
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
    if not persistence.get_dependency_from_service_id_and_tag_id(db, str(service_id), str(tag_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such service tag")

    ## sovled
    ticket_ids_soloved = get_sorted_solved_ticket_ids_by_service_tag_and_status(service, tag_id)
    threat_impact_count_soloved = count_service_solved_tickets_per_threat_impact(service, tag_id)

    ## unsovled
    ticket_ids_unsoloved = get_sorted_unsolved_ticket_ids_by_service_tag_and_status(service, tag_id)
    threat_impact_count_unsoloved = count_service_unsolved_tickets_per_threat_impact(
        service, tag_id
    )

    return {
        "solved": {
            "pteam_id": pteam_id,
            "service_id": service_id,
            "tag_id": tag_id,
            "threat_impact_count": threat_impact_count_soloved,
            "ticket_ids": ticket_ids_soloved,
        },
        "unsolved": {
            "pteam_id": pteam_id,
            "service_id": service_id,
            "tag_id": tag_id,
            "threat_impact_count": threat_impact_count_unsoloved,
            "ticket_ids": ticket_ids_unsoloved,
        },
    }


@router.get(
    "/{pteam_id}/services/{service_id}/topicstatus/{topic_id}/{tag_id}",
    response_model=schemas.TopicStatusResponse | None,
)
def get_service_topic_status(
    pteam_id: UUID,
    service_id: UUID,
    topic_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current status (or None) of the service.
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
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    firstest_status: models.TicketStatus | None = None
    for dependency in service.dependencies:
        if dependency.tag_id != str(tag_id):
            continue
        for threat in persistence.search_threats(db, dependency.dependency_id, topic_id):
            if not (ticket := threat.ticket):
                continue
            if not (current_ticket_status := ticket.current_ticket_status):
                continue

            if ticket_status := current_ticket_status.ticket_status:
                if (
                    firstest_status is None
                    or ticket_status.updated_at < firstest_status.current_ticket_status.updated_at
                ):
                    firstest_status = ticket_status

    return (
        command.ticket_status_to_response(db, firstest_status)
        if firstest_status is not None
        else {
            "pteam_id": pteam_id,
            "service_id": service_id,
            "topic_id": topic_id,
            "tag_id": tag_id,
        }
    )


@router.post(
    "/{pteam_id}/services/{service_id}/topicstatus/{topic_id}/{tag_id}",
    response_model=schemas.TopicStatusResponse | None,
)
def set_services_topic_status(
    pteam_id: UUID,
    service_id: UUID,
    topic_id: UUID,
    tag_id: UUID,
    data: schemas.TopicStatusRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set topic status of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (service := persistence.get_service_by_id(db, service_id)):
        raise NO_SUCH_SERVICE
    if service.pteam_id != str(pteam_id):
        raise NO_SUCH_SERVICE
    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    if not command.check_tag_is_related_to_topic(db, tag, topic):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag mismatch")

    if data.topic_status not in {
        models.TopicStatusType.acknowledged,
        models.TopicStatusType.scheduled,
        models.TopicStatusType.completed,
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")

    for logging_id_ in data.logging_ids:
        if not (log := persistence.get_action_log_by_id(db, logging_id_)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such actionlog",
            )
        if log.pteam_id != str(pteam_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not an actionlog for the pteam",
            )
        if log.topic_id != str(topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not an actionlog for the topic",
            )
    for assignee in data.assignees:
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

    response = ticket_manager.set_ticket_statuses_in_service(
        db, current_user, service, topic, tag, data
    )
    db.commit()

    return response


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


@router.get("/{pteam_id}/tags/{tag_id}", response_model=schemas.PTeamtagExtResponse)
def get_pteamtag(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detals of the pteam tag with last updated date.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    references = []
    for service in pteam.services:
        for dependency in service.dependencies:
            if dependency.tag_id == str(tag_id):
                references.append(
                    {
                        "service": service.service_name,
                        "target": dependency.target,
                        "version": dependency.version,
                    }
                )

    last_updated_at = command.get_last_updated_at_in_current_pteam_topic_tag_status(
        db, pteam_id, tag_id
    )

    return {
        "pteam_id": pteam_id,
        "tag_id": tag_id,
        "references": references,
        "last_updated_at": last_updated_at,
    }


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


@router.post("/{pteam_id}/upload_sbom_file", response_model=list[schemas.ExtTagResponse])
def upload_pteam_sbom_file(
    pteam_id: UUID,
    file: UploadFile,
    service: str = Query("", description="name of service(repository or product)"),
    force_mode: bool = Query(False, description="if true, create unexist tags"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    upload sbom file
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing service_name")
    _check_file_extention(file, ".json")
    _check_empty_file(file)
    try:
        jdata = json.load(file.file)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Wrong file content"),
        ) from error

    if not (
        service_model := next(filter(lambda x: x.service_name == service, pteam.services), None)
    ):
        service_model = models.Service(pteam_id=str(pteam_id), service_name=service)
        pteam.services.append(service_model)
        db.flush()

    try:
        json_lines = sbom_json_to_artifact_json_lines(jdata)
        apply_service_tags(
            db, pteam, service_model, json_lines, auto_create_tags=force_mode, auto_close=False
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    db.commit()

    return get_pteam_ext_tags(db, pteam)


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
        apply_service_tags(
            db, pteam, service_model, json_lines, auto_create_tags=force_mode, auto_close=True
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    db.commit()

    return get_pteam_ext_tags(db, pteam)


def apply_service_tags(
    db: Session,
    pteam: models.PTeam,
    service: models.Service,
    json_lines: list[dict],
    auto_create_tags=False,
    auto_close=False,
) -> None:
    def _collect_versions_of_pteam_tags(pteam: models.PTeam) -> dict[str, set[str]]:
        ret: dict[str, set[str]] = {}
        for service in pteam.services:
            for dependency in service.dependencies:
                versions = ret.get(dependency.tag_id, set())
                versions.add(dependency.version)
                ret[dependency.tag_id] = versions
        return ret

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
                _tag = get_or_create_topic_tag(db, _tag_name)  # FIXME!!
            else:
                missing_tags.add(_tag_name)
        if _tag:
            for ref in line.get("references", [{}]):
                new_dependencies_set.add(
                    (_tag.tag_id, ref.get("target", ""), ref.get("version", ""))
                )
    if missing_tags:
        raise ValueError(f"No such tags: {', '.join(sorted(missing_tags))}")

    if auto_close:
        old_versions = _collect_versions_of_pteam_tags(pteam)

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

    # try auto close if make sense
    if auto_close:
        new_versions = _collect_versions_of_pteam_tags(pteam)
        if tags_for_auto_close := [
            tag
            for tag in pteam.tags
            if new_versions.get(tag.tag_id, set()) != old_versions.get(tag.tag_id, set())
        ]:
            auto_close_by_pteamtags(db, [(pteam, tag) for tag in tags_for_auto_close])

    command.fix_current_status_by_pteam(db, pteam)


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
    db.flush()
    command.fix_current_status_by_pteam(db, pteam)

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


@router.get(
    "/{pteam_id}/topicstatusessummary/{tag_id}", response_model=schemas.PTeamTopicStatusesSummary
)
def get_pteam_topic_statuses_summary(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current status summary of all pteam topics.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG
    return command.get_pteam_topic_statuses_summary(db, pteam, tag)


@router.post(
    "/{pteam_id}/topicstatus/{topic_id}/{tag_id}", response_model=schemas.PTeamTopicStatusResponse
)
def set_pteam_topic_status(
    pteam_id: UUID,
    topic_id: UUID,
    tag_id: UUID,
    data: schemas.TopicStatusRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set topic status of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # TODO: should check pteam auth: topic_status

    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise NO_SUCH_TOPIC
    # TODO: should check pteam topic???
    # TODO: should check topic tag?? -- should care about parent&child

    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    if not command.check_tag_is_related_to_topic(db, tag, topic):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag mismatch")

    if data.topic_status not in {
        models.TopicStatusType.acknowledged,
        models.TopicStatusType.scheduled,
        models.TopicStatusType.completed,
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")

    for logging_id_ in data.logging_ids:
        if not (log := persistence.get_action_log_by_id(db, logging_id_)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No such actionlog",
            )
        if log.pteam_id != str(pteam_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not an actionlog for the pteam",
            )
        if log.topic_id != str(topic_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not an actionlog for the topic",
            )
    for assignee in data.assignees:
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

    ret = set_pteam_topic_status_internal(db, current_user, pteam, topic, tag, data)
    ticket_manager.set_ticket_statuses_in_pteam(db, current_user, pteam, topic, tag, data)

    db.commit()

    return ret


@router.get(
    "/{pteam_id}/topicstatus/{topic_id}/{tag_id}", response_model=schemas.PTeamTopicStatusResponse
)
def get_pteam_topic_status(
    pteam_id: UUID,
    topic_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current status (or None) of the pteam topic.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    # TODO: should check pteam topic???
    # TODO: should check topic tag?? -- should care about parent&child

    current_row = persistence.get_current_pteam_topic_tag_status(db, pteam_id, topic_id, tag_id)
    if current_row is None or current_row.status_id is None:
        # should not happen if request is right
        return {
            "pteam_id": pteam_id,
            "topic_id": topic_id,
            "tag_id": tag_id,
        }

    status_row = persistence.get_pteam_topic_tag_status_by_id(db, current_row.status_id)
    assert status_row
    return command.pteam_topic_tag_status_to_response(db, status_row)


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


@router.post("/{pteam_id}/fix_status_mismatch")
def fix_status_mismatch(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    for tag, topic in command.get_auto_close_triable_pteam_tags_and_topics(db, pteam):
        pteamtag_try_auto_close_topic(db, pteam, tag, topic)

    db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.post("/{pteam_id}/tags/{tag_id}/fix_status_mismatch")
def fix_status_mismatch_tag(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)):
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in pteam.tags:
        raise NO_SUCH_PTEAM_TAG

    for topic in command.get_auto_close_triable_pteam_topics(db, pteam, tag):
        pteamtag_try_auto_close_topic(db, pteam, tag, topic)

    db.commit()

    return Response(status_code=status.HTTP_200_OK)
