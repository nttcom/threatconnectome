from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.common import (
    check_ateam_auth,
    check_ateam_membership,
    check_pteam_auth,
)
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.database import get_db
from app.slack import validate_slack_webhook_url

router = APIRouter(prefix="/ateams", tags=["ateams"])

NO_SUCH_ATEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ateam")
NO_SUCH_TOPIC = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
NOT_AN_ATEAM_MEMBER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not an ateam member",
)
NOT_HAVE_AUTH = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have authority",
)


def _make_ateam_info(ateam: models.ATeam) -> schemas.ATeamInfo:
    return schemas.ATeamInfo(
        ateam_id=UUID(ateam.ateam_id),
        ateam_name=ateam.ateam_name,
        contact_info=ateam.contact_info,
        alert_slack=schemas.Slack(**ateam.alert_slack.__dict__),
        alert_mail=schemas.Mail(**ateam.alert_mail.__dict__),
        pteams=ateam.pteams,
    )


@router.get("", response_model=List[schemas.ATeamEntry])
def get_ateams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all ateam entries.
    """
    return persistence.get_all_ateams(db)


@router.post("", response_model=schemas.ATeamInfo)
def create_ateam(
    data: schemas.ATeamCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create an ateam.
    """
    if data.alert_slack and data.alert_slack.webhook_url:
        validate_slack_webhook_url(data.alert_slack.webhook_url)
    ateam = models.ATeam(
        ateam_name=data.ateam_name.strip(),
        contact_info=data.contact_info.strip(),
    )
    ateam.alert_slack = models.ATeamSlack(
        ateam_id=ateam.ateam_id,
        enable=data.alert_slack.enable if data.alert_slack else True,
        webhook_url=data.alert_slack.webhook_url if data.alert_slack else "",
    )
    ateam.alert_mail = models.ATeamMail(
        ateam_id=ateam.ateam_id,
        enable=data.alert_mail.enable if data.alert_mail else True,
        address=data.alert_mail.address if data.alert_mail else "",
    )
    ateam = persistence.create_ateam(db, ateam)

    # join to the created ateam
    ateam.members.append(current_user)

    # set default authority
    user_auth = models.ATeamAuthority(
        ateam_id=ateam.ateam_id,
        user_id=current_user.user_id,
        authority=models.ATeamAuthIntFlag.ATEAM_MASTER,
    )
    member_auth = models.ATeamAuthority(
        ateam_id=ateam.ateam_id,
        user_id=str(MEMBER_UUID),
        authority=models.ATeamAuthIntFlag.ATEAM_MEMBER,
    )
    not_member_auth = models.ATeamAuthority(
        ateam_id=ateam.ateam_id,
        user_id=str(NOT_MEMBER_UUID),
        authority=models.ATeamAuthIntFlag.FREE_TEMPLATE,
    )
    persistence.create_ateam_authority(db, user_auth)
    persistence.create_ateam_authority(db, member_auth)
    persistence.create_ateam_authority(db, not_member_auth)

    db.commit()

    return _make_ateam_info(ateam)


@router.get("/auth_info", response_model=schemas.ATeamAuthInfo)
def get_auth_info(current_user: models.Account = Depends(get_current_user)):
    """
    Get ateam authority information.
    """
    return schemas.ATeamAuthInfo(
        authorities=[
            schemas.ATeamAuthInfo.ATeamAuthEntry(
                enum=key, name=str(value["name"]), desc=str(value["desc"])
            )
            for key, value in models.ATeamAuthEnum.info().items()
        ],
        pseudo_uuids=[
            schemas.ATeamAuthInfo.PseudoUUID(name="member", uuid=MEMBER_UUID),
            schemas.ATeamAuthInfo.PseudoUUID(name="others", uuid=NOT_MEMBER_UUID),
        ],
    )


@router.post("/apply_invitation", response_model=schemas.ATeamInfo)
def apply_invitation(
    data: schemas.ApplyInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply invitation to ateam.
    """
    persistence.expire_ateam_invitations(db)

    if not (invitation := persistence.get_ateam_invitation_by_id(db, data.invitation_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) invitation id"
        )
    if current_user in invitation.ateam.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined to the ateam"
        )

    invitation.ateam.members.append(current_user)

    if invitation.authority:  # invitation with authority
        # Note: non-members never have ateam auth
        ateam_auth = models.ATeamAuthority(
            ateam_id=invitation.ateam_id,
            user_id=current_user.user_id,
            authority=invitation.authority,
        )
        persistence.create_ateam_authority(db, ateam_auth)

    invitation.used_count += 1

    db.commit()
    return _make_ateam_info(invitation.ateam)


@router.post("/apply_watching_request", response_model=schemas.PTeamInfo)
def apply_watching_request(
    data: schemas.ApplyWatchingRequestRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply watching request.
    """
    persistence.expire_ateam_watching_requests(db)

    if not (watching_request := persistence.get_ateam_watching_request_by_id(db, data.request_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) request id"
        )
    if str(data.pteam_id) in [_pteam.pteam_id for _pteam in watching_request.ateam.pteams]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already connect to the ateam"
        )
    if not (pteam := persistence.get_pteam_by_id(db, data.pteam_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pteam id")
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    watching_request.ateam.pteams.append(pteam)
    watching_request.used_count += 1
    db.flush()
    persistence.expire_ateam_watching_requests(db)

    db.commit()

    return pteam


@router.get("/{ateam_id}", response_model=schemas.ATeamInfo)
def get_ateam(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get ateam details. members only.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER
    return _make_ateam_info(ateam)


@router.put("/{ateam_id}", response_model=schemas.ATeamInfo)
def update_ateam(
    ateam_id: UUID,
    data: schemas.ATeamUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an ateam.
    """

    if data.alert_slack and data.alert_slack.webhook_url:
        validate_slack_webhook_url(data.alert_slack.webhook_url)

    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH
    for key, value in data:
        if value is None:
            continue
        if key == "alert_slack":
            setattr(ateam, key, models.ATeamSlack(**value.__dict__))
            continue
        if key == "alert_mail":
            setattr(ateam, key, models.ATeamMail(**value.__dict__))
            continue
        setattr(ateam, key, value)

    db.commit()
    db.refresh(ateam)

    return _make_ateam_info(ateam)


@router.post("/{ateam_id}/authority", response_model=List[schemas.ATeamAuthResponse])
def update_ateam_auth(
    ateam_id: UUID,
    requests: List[schemas.ATeamAuthRequest],
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update ateam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : ateam member
      - 00000000-0000-0000-0000-0000cafe0002 : not ateam member
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    str_ids = [str(x.user_id) for x in requests]
    if len(set(str_ids)) != len(str_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous request")

    response = []
    for request in requests:
        if (user_id := str(request.user_id)) == str(SYSTEM_UUID):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
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
            if not check_ateam_membership(ateam, user):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not an ateam member",
                )
        if not (auth := persistence.get_ateam_authority(db, ateam_id, user_id)):
            auth = models.ATeamAuthority(
                ateam_id=str(ateam_id),
                user_id=user_id,
                authority=0,
            )
            auth = persistence.create_ateam_authority(db, auth)
        auth.authority = models.ATeamAuthIntFlag.from_enums(request.authorities)

    db.flush()
    if command.missing_ateam_admin(db, ateam):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )

    db.commit()

    for request in requests:
        auth = persistence.get_ateam_authority(db, ateam_id, request.user_id)
        response.append(
            {
                "user_id": request.user_id,
                "authorities": models.ATeamAuthIntFlag(auth.authority).to_enums() if auth else [],
            }
        )
    return response


@router.get("/{ateam_id}/authority", response_model=List[schemas.ATeamAuthResponse])
def get_ateam_auth(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get ateam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : ateam member
      - 00000000-0000-0000-0000-0000cafe0002 : not ateam member
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if current_user in ateam.members:  # member can get all authorities
        authorities = persistence.get_ateam_all_authorities(db, ateam_id)
    else:  # not member can get only for NOT_MEMBER_UUID
        auth_for_not_member = persistence.get_ateam_authority(db, ateam_id, NOT_MEMBER_UUID)
        authorities = [auth_for_not_member] if auth_for_not_member else []

    response = []
    for auth in authorities:
        enums = models.ATeamAuthIntFlag(auth.authority).to_enums()
        response.append({"user_id": auth.user_id, "authorities": enums})
    return response


@router.get("/{ateam_id}/members", response_model=List[schemas.UserResponse])
def get_ateam_members(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get members of the ateam.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER

    return ateam.members


@router.delete("/{ateam_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    ateam_id: UUID,
    user_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    User leaves the ateam.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if user_id in {MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove pseudo account"
        )

    if current_user.user_id != str(user_id) and not check_ateam_auth(
        db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN
    ):
        raise NOT_HAVE_AUTH

    target_users = [x for x in ateam.members if x.user_id == str(user_id)]
    if len(target_users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such ateam member")

    # remove all extra authorities  # FIXME: should be deleted on cascade
    if auth := persistence.get_ateam_authority(db, ateam_id, user_id):
        command.workaround_delete_ateam_authority(db, auth)

    # remove from members
    ateam.members.remove(target_users[0])

    db.flush()
    if command.missing_ateam_admin(db, ateam):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{ateam_id}/invitation", response_model=schemas.ATeamInvitationResponse)
def create_invitation(
    ateam_id: UUID,
    data: schemas.ATeamInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new ateam invitation token.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH
    if data.authorities is not None and not check_ateam_auth(
        db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADMIN required to set authorities"
        )
    intflag = models.ATeamAuthIntFlag.from_enums(data.authorities or [])
    if data.limit_count is not None and data.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give null for unlimited)",
        )

    persistence.expire_ateam_invitations(db)

    del data.authorities
    new_invitation = models.ATeamInvitation(
        ateam_id=str(ateam_id), user_id=current_user.user_id, authority=intflag, **data.model_dump()
    )
    invitation = persistence.create_ateam_invitation(db, new_invitation)
    db.commit()
    db.refresh(invitation)

    return {
        **invitation.__dict__,
        "authorities": models.ATeamAuthIntFlag(invitation.authority).to_enums(),
    }


@router.get("/{ateam_id}/invitation", response_model=List[schemas.ATeamInvitationResponse])
def list_invitation(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List effective invitations.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH

    persistence.expire_ateam_invitations(db)
    # do not commit within GET method

    return [
        {**item.__dict__, "authorities": models.ATeamAuthIntFlag(item.authority).to_enums()}
        for item in ateam.invitations
    ]


@router.delete("/{ateam_id}/invitation/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invitation(
    ateam_id: UUID,
    invitation_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invalidate invitation to ateam.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH
    persistence.expire_ateam_invitations(db)

    # omit validating invitation to avoid raising error if already expired.
    if invitation := persistence.get_ateam_invitation_by_id(db, invitation_id):
        persistence.delete_ateam_invitation(db, invitation)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/invitation/{invitation_id}", response_model=schemas.ATeamInviterResponse)
def invited_ateam(invitation_id: UUID, db: Session = Depends(get_db)):
    """
    Get invited ateam info.
    """
    invitation = persistence.get_ateam_invitation_by_id(db, invitation_id)
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such invitation (or already expired)"
        )
    resp = {
        "ateam_id": invitation.ateam.ateam_id,
        "ateam_name": invitation.ateam.ateam_name,
        "email": invitation.inviter.email,
        "user_id": invitation.user_id,
    }
    return resp


@router.get("/{ateam_id}/watching_pteams", response_model=List[schemas.PTeamEntry])
def get_watching_pteams(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get watching pteams of the ateam.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER
    return ateam.pteams


@router.delete("/{ateam_id}/watching_pteams/{pteam_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watching_pteam(
    ateam_id: UUID,
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove pteam from watching list.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    ateam.pteams = [pteam for pteam in ateam.pteams if pteam.pteam_id != str(pteam_id)]

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{ateam_id}/watching_request", response_model=schemas.ATeamWatchingRequestResponse)
def create_watching_request(
    ateam_id: UUID,
    data: schemas.ATeamWatchingRequestRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new ateam watching request token.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH
    if data.limit_count is not None and data.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give null for unlimited)",
        )

    persistence.expire_ateam_watching_requests(db)

    new_watching_request = models.ATeamWatchingRequest(
        ateam_id=str(ateam_id), user_id=current_user.user_id, **data.model_dump()
    )
    watching_request = persistence.create_ateam_watching_request(db, new_watching_request)
    db.commit()
    db.refresh(watching_request)

    return watching_request


@router.get(
    "/{ateam_id}/watching_request", response_model=List[schemas.ATeamWatchingRequestResponse]
)
def list_watching_request(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List effective watching_request.
    """
    ateam = persistence.get_ateam_by_id(db, ateam_id)
    if ateam is None:
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    persistence.expire_ateam_watching_requests(db)
    db.commit()
    return ateam.watching_requests


@router.delete("/{ateam_id}/watching_request/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watching_request(
    ateam_id: UUID,
    request_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invalidate watching request.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH
    persistence.expire_ateam_watching_requests(db)

    # omit validating request to avoid raising error if already expired.
    if request := persistence.get_ateam_watching_request_by_id(db, request_id):
        persistence.delete_ateam_watching_request(db, request)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/watching_request/{request_id}", response_model=schemas.ATeamRequesterResponse)
def get_requested_ateam(request_id: UUID, db: Session = Depends(get_db)):
    """
    Get ateam info of watching request.
    """
    watching_request = persistence.get_ateam_watching_request_by_id(db, request_id)
    if watching_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such watching request (or already expired)",
        )
    resp = {
        "ateam_id": watching_request.ateam.ateam_id,
        "ateam_name": watching_request.ateam.ateam_name,
        "email": watching_request.requester.email,
        "user_id": watching_request.user_id,
    }
    return resp


@router.get("/{ateam_id}/topicstatus", response_model=schemas.ATeamTopicStatusResponse)
def get_topic_status(
    ateam_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # 10 is default perPage in web/src/pages/Analysis.jsx
    sort_key: schemas.TopicSortKey = Query(schemas.TopicSortKey.THREAT_IMPACT),
    search: Optional[str] = Query(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topic summary list.

    Query Params:
    - **offset** (Optional) says to skip that many entries to return. Default is 0.
    - **limit** (Optional) no more than that many entries will be returned. Default, max is 10, 100.
    - **search** (Optional) filter topics by title with given word. Default is None.
    - **sort_key** (Optional) the primary sort key which should be one of threat_impact,
                   threat_impact_desc, updated_at, updated_at_desc. Default is threat_impact.

    Note:
    - Empty string as **search** will be ignored.
    - The secondary sort key is updated_at_desc or threat_impact.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER
    # ignore empty search.
    search = search if search else None

    rows = command.get_ateam_topic_statuses(db, ateam_id, sort_key, search)

    # Caution:
    #   rows includes completed. (how can i filter by query???)
    #   rows is already sorted by query based on query params. keep the order.

    def _pick_pteam(pteams_, pteam_id_):
        return next(filter(lambda x: x["pteam_id"] == pteam_id_, pteams_), None)

    summary: List[dict] = []
    for row in rows:
        if (
            row.PTeamTopicTagStatus
            and row.PTeamTopicTagStatus.topic_status == models.TopicStatusType.completed
        ):
            continue  # filter completed
        if len(summary) == 0 or summary[-1]["topic_id"] != row.topic_id:
            summary.append(
                {
                    "topic_id": row.topic_id,
                    "title": row.title,
                    "threat_impact": row.threat_impact,
                    "updated_at": row.updated_at,
                    "num_pteams": 0,
                    "pteams": [],
                }
            )
        _topic = summary[-1]
        _pteam = _pick_pteam(_topic["pteams"], row.pteam_id)
        if _pteam is None:
            _topic["pteams"].append(
                {
                    "pteam_id": row.pteam_id,
                    "pteam_name": row.pteam_name,
                    "statuses": [],
                }
            )
            _topic["num_pteams"] += 1
            _pteam = _topic["pteams"][-1]
        _pteam["statuses"].append(
            {
                **(
                    row.PTeamTopicTagStatus.__dict__
                    if row.PTeamTopicTagStatus
                    else {
                        "topic_id": row.topic_id,
                        "pteam_id": row.pteam_id,
                        "topic_status": models.TopicStatusType.alerted,
                    }
                ),
                # extended data not included in PTeamTopicTagStatus
                "tag": row.Tag,
            }
        )

    # Note:
    #   topic_statuses[pteams][0][statuses][0][topic_status] is the worst of the topic.
    #   if the worst is 'scheduled', ...[statuses][0][scheduled_at] is the latest schedule.

    # apply offset & limit
    sliced_summary = summary[offset : offset + limit]

    return {
        "num_topics": len(summary),
        "offset": offset,
        "limit": limit,
        "search": search,
        "sort_key": sort_key,
        "topic_statuses": sliced_summary,
    }


@router.get(
    "/{ateam_id}/topiccomment/{topic_id}", response_model=List[schemas.ATeamTopicCommentResponse]
)
def get_topic_comments(
    ateam_id: UUID,
    topic_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get ateam topic comments.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER
    return command.get_ateam_topic_comments(db, ateam_id, topic_id)


@router.post(
    "/{ateam_id}/topiccomment/{topic_id}", response_model=schemas.ATeamTopicCommentResponse
)
def add_topic_comment(
    ateam_id: UUID,
    topic_id: UUID,
    data: schemas.ATeamTopicCommentRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add ateam topic comment.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    if not check_ateam_membership(ateam, current_user):
        raise NOT_AN_ATEAM_MEMBER
    new_comment = models.ATeamTopicComment(
        topic_id=str(topic_id),
        ateam_id=str(ateam_id),
        user_id=str(current_user.user_id),
        comment=data.comment,
        created_at=datetime.now(),
    )
    comment = persistence.create_ateam_topic_comment(db, new_comment)
    db.commit()
    db.refresh(comment)  # comment.__dict__ has to refresh
    return {**comment.__dict__, "email": current_user.email}


@router.put(
    "/{ateam_id}/topiccomment/{topic_id}/{comment_id}",
    response_model=schemas.ATeamTopicCommentResponse,
)
def update_topic_comment(
    ateam_id: UUID,
    topic_id: UUID,
    comment_id: UUID,
    data: schemas.ATeamTopicCommentRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update ateam topic comment.
    """
    if not persistence.get_ateam_by_id(db, ateam_id):
        raise NO_SUCH_ATEAM
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    comment = persistence.get_ateam_topic_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    if comment.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    comment.comment = data.comment
    comment.updated_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return {**comment.__dict__, "email": current_user.email}


@router.delete(
    "/{ateam_id}/topiccomment/{topic_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_topic_comment(
    ateam_id: UUID,
    topic_id: UUID,
    comment_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete ateam topic comment.
    """
    if not (ateam := persistence.get_ateam_by_id(db, ateam_id)):
        raise NO_SUCH_ATEAM
    if not persistence.get_topic_by_id(db, topic_id):
        raise NO_SUCH_TOPIC
    comment = persistence.get_ateam_topic_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    if comment.user_id != current_user.user_id:
        if not check_ateam_auth(db, ateam, current_user, models.ATeamAuthIntFlag.ADMIN):
            raise NOT_HAVE_AUTH
    persistence.delete_ateam_topic_comment(db, comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
