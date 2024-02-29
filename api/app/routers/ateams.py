from datetime import datetime
from typing import List, Optional, Sequence, Tuple, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import and_, nullsfirst, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    check_ateam_auth,
    check_ateam_membership,
    check_pteam_auth,
    sortkey2orderby,
    validate_ateam,
    validate_pteam,
    validate_topic,
)
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.database import get_db
from app.slack import validate_slack_webhook_url

router = APIRouter(prefix="/ateams", tags=["ateams"])


def _make_ateam_info(ateam: models.ATeam) -> schemas.ATeamInfo:
    return schemas.ATeamInfo(
        ateam_id=UUID(ateam.ateam_id),
        ateam_name=ateam.ateam_name,
        contact_info=ateam.contact_info,
        alert_slack=schemas.Slack(**ateam.alert_slack.__dict__),
        alert_mail=schemas.Mail(**ateam.alert_mail.__dict__),
        pteams=ateam.pteams,
        zones=list({zone for pteam in ateam.pteams for zone in pteam.zones}),
    )


def _modify_ateam_auth(
    db: Session,
    ateam_id: Union[UUID, str],
    authes: List[
        Tuple[
            Union[UUID, str],  # user_id
            Union[models.ATeamAuthIntFlag, int],  # auth. 0 for delete
        ]
    ],
):
    for user_id, auth in authes:
        if str(user_id) in map(str, [MEMBER_UUID, NOT_MEMBER_UUID]):
            if auth & models.ATeamAuthIntFlag.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot give ADMIN to pseudo account",
                )
        else:
            check_ateam_membership(db, ateam_id, user_id, on_error=status.HTTP_400_BAD_REQUEST)

    for user_id, auth in authes:
        row = (
            db.query(models.ATeamAuthority)
            .filter(
                models.ATeamAuthority.ateam_id == str(ateam_id),
                models.ATeamAuthority.user_id == str(user_id),
            )
            .one_or_none()
        )
        if row is None:
            if not auth:
                continue  # nothing to remove
            row = models.ATeamAuthority(ateam_id=str(ateam_id), user_id=str(user_id))
        if auth:
            row.authority = int(auth)
            db.add(row)
        else:
            db.delete(row)
    db.commit()


@router.get("", response_model=List[schemas.ATeamEntry])
def get_ateams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all ateam entries.
    """
    return db.query(models.ATeam).all()


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
        slack_webhook_url=(
            data.alert_slack.webhook_url.strip() if data.alert_slack else ""
        ),  # deprecated
    )
    ateam.alert_slack = models.AteamSlack(
        ateam_id=ateam.ateam_id,
        enable=data.alert_slack.enable if data.alert_slack else True,
        webhook_url=data.alert_slack.webhook_url if data.alert_slack else "",
    )
    ateam.alert_mail = models.ATeamMail(
        ateam_id=ateam.ateam_id,
        enable=data.alert_mail.enable if data.alert_mail else True,
        address=data.alert_mail.address if data.alert_mail else "",
    )
    current_user.ateams.append(ateam)
    db.add(current_user)
    db.commit()
    db.refresh(ateam)

    _modify_ateam_auth(
        db,
        ateam.ateam_id,
        [
            (current_user.user_id, models.ATeamAuthIntFlag.ATEAM_MASTER),
            (MEMBER_UUID, models.ATeamAuthIntFlag.ATEAM_MEMBER),
            (NOT_MEMBER_UUID, models.ATeamAuthIntFlag.FREE_TEMPLATE),
        ],
    )

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
    _expire_invitations(db)

    invitation = (
        db.query(models.ATeamInvitation)
        .filter(
            models.ATeamInvitation.invitation_id == str(data.invitation_id),
            or_(
                models.ATeamInvitation.limit_count.is_(None),
                models.ATeamInvitation.limit_count > models.ATeamInvitation.used_count,
            ),
        )
        .with_for_update()
        .one_or_none()
    )  # lock and block!
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) invitation id"
        )
    if current_user in invitation.ateam.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined to the ateam"
        )

    invitation.ateam.members.append(current_user)
    invitation.used_count += 1
    if invitation.authority > 0:
        ateam_auth = db.query(models.ATeamAuthority).filter(
            models.ATeamAuthority.ateam_id == invitation.ateam_id,
            models.ATeamAuthority.user_id == current_user.user_id,
        ).one_or_none() or models.ATeamAuthority(
            ateam_id=invitation.ateam_id, user_id=current_user.user_id, authority=0
        )
        ateam_auth.authority |= invitation.authority
        db.add(ateam_auth)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

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
    _expire_watching_requests(db)

    watching_request = (
        db.query(models.ATeamWatchingRequest)
        .filter(
            models.ATeamWatchingRequest.request_id == str(data.request_id),
            or_(
                models.ATeamWatchingRequest.limit_count.is_(None),
                models.ATeamWatchingRequest.limit_count > models.ATeamWatchingRequest.used_count,
            ),
        )
        .with_for_update()
        .one_or_none()
    )  # lock and block!
    if watching_request is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) request id"
        )
    check_pteam_auth(
        db,
        data.pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    if str(data.pteam_id) in [pteam.pteam_id for pteam in watching_request.ateam.pteams]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already connect to the ateam"
        )

    pteam = validate_pteam(db, str(data.pteam_id), on_error=status.HTTP_400_BAD_REQUEST)
    assert pteam
    watching_request.ateam.pteams.append(pteam)

    watching_request.used_count += 1

    db.add(watching_request)
    db.commit()
    db.refresh(watching_request)

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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
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

    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    for key, value in data:
        if value is None:
            continue
        if key == "alert_slack":
            setattr(ateam, key, models.AteamSlack(**value.__dict__))
            continue
        if key == "alert_mail":
            setattr(ateam, key, models.ATeamMail(**value.__dict__))
            continue
        setattr(ateam, key, value)
    db.add(ateam)
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    str_ids = [str(x.user_id) for x in requests]
    if len(set(str_ids)) != len(str_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous request")
    for str_id in str_ids:
        if str_id == str(SYSTEM_UUID):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
        if str_id in {str(MEMBER_UUID), str(NOT_MEMBER_UUID)}:
            continue
        check_ateam_membership(db, ateam_id, str_id, on_error=status.HTTP_400_BAD_REQUEST)

    if not any(models.ATeamAuthEnum.ADMIN in x.authorities for x in requests):
        _guard_last_admin(db, ateam_id, str_ids)

    _modify_ateam_auth(
        db,
        ateam_id,
        [(x.user_id, models.ATeamAuthIntFlag.from_enums(x.authorities)) for x in requests],
    )

    authes = (
        db.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam_id),
            models.ATeamAuthority.user_id.in_(str_ids),
        )
        .all()
    )
    auth_map = {x.user_id: models.ATeamAuthIntFlag(x.authority).to_enums() for x in authes}
    response = [
        {"user_id": user_id, "authorities": auth_map.get(user_id) or []} for user_id in str_ids
    ]
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    rows = (
        db.query(models.ATeamAuthority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam_id),
            (
                true()
                if check_ateam_membership(db, ateam_id, current_user.user_id)
                else models.ATeamAuthority.user_id == str(NOT_MEMBER_UUID)
            ),  # limit if not a member
        )
        .all()
    )
    return [
        {"user_id": row.user_id, "authorities": models.ATeamAuthIntFlag(row.authority).to_enums()}
        for row in rows
    ]


@router.get("/{ateam_id}/members", response_model=List[schemas.UserResponse])
def get_ateam_members(
    ateam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get members of the ateam.
    """
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    return ateam.members


def _guard_last_admin(db: Session, ateam_id: UUID, excludes: Sequence[Union[UUID, str]]):
    if (
        db.query(models.ATeamAuthority.user_id)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam_id),
            models.ATeamAuthority.authority.op("&")(models.ATeamAuthIntFlag.ADMIN) > 0,
            models.ATeamAuthority.user_id.not_in(list(map(str, excludes))),
        )
        .count()
        == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )


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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    if user_id in {MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove pseudo account"
        )
    if current_user.user_id != str(user_id):
        check_ateam_auth(
            db,
            ateam_id,
            current_user.user_id,
            models.ATeamAuthIntFlag.ADMIN,
            on_error=status.HTTP_403_FORBIDDEN,
        )
    check_ateam_membership(db, ateam_id, user_id, on_error=status.HTTP_404_NOT_FOUND)
    _guard_last_admin(db, ateam_id, [user_id])
    _modify_ateam_auth(db, ateam_id, [(user_id, 0)])

    ateam.members = [user for user in ateam.members if user.user_id != str(user_id)]
    db.add(ateam)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _expire_invitations(db: Session):
    db.query(models.ATeamInvitation).filter(
        or_(
            models.ATeamInvitation.expiration < datetime.now(),
            and_(
                models.ATeamInvitation.limit_count.is_not(None),
                models.ATeamInvitation.used_count >= models.ATeamInvitation.limit_count,
            ),
        )
    ).delete()
    db.commit()


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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    if data.authorities is not None and not check_ateam_auth(
        db, ateam_id, current_user.user_id, models.ATeamAuthIntFlag.ADMIN
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

    _expire_invitations(db)

    del data.authorities
    invitation = models.ATeamInvitation(
        ateam_id=str(ateam_id), user_id=current_user.user_id, authority=intflag, **data.model_dump()
    )
    db.add(invitation)
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    _expire_invitations(db)

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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    _expire_invitations(db)

    # omit validating invitation to avoid raising error if already expired.
    db.query(models.ATeamInvitation).filter(
        models.ATeamInvitation.invitation_id == str(invitation_id)
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/invitation/{invitation_id}", response_model=schemas.ATeamInviterResponse)
def invited_ateam(invitation_id: UUID, db: Session = Depends(get_db)):
    """
    Get invited ateam info.
    """
    invitation = (
        db.query(models.ATeamInvitation)
        .filter(models.ATeamInvitation.invitation_id == str(invitation_id))
        .one_or_none()
    )
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    ateam.pteams = [pteam for pteam in ateam.pteams if pteam.pteam_id != str(pteam_id)]
    db.add(ateam)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _expire_watching_requests(db: Session):
    db.query(models.ATeamWatchingRequest).filter(
        or_(
            models.ATeamWatchingRequest.expiration < datetime.now(),
            and_(
                models.ATeamWatchingRequest.limit_count.is_not(None),
                models.ATeamWatchingRequest.used_count >= models.ATeamWatchingRequest.limit_count,
            ),
        )
    ).delete()
    db.commit()


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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    if data.limit_count is not None and data.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give null for unlimited)",
        )

    _expire_watching_requests(db)

    watching_request = models.ATeamWatchingRequest(
        ateam_id=str(ateam_id), user_id=current_user.user_id, **data.model_dump()
    )
    db.add(watching_request)
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    _expire_watching_requests(db)

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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_auth(
        db,
        ateam_id,
        current_user.user_id,
        models.ATeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    _expire_watching_requests(db)

    # omit validating request to avoid raising error if already expired.
    db.query(models.ATeamWatchingRequest).filter(
        models.ATeamWatchingRequest.request_id == str(request_id)
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/watching_request/{request_id}", response_model=schemas.ATeamRequesterResponse)
def get_requested_ateam(request_id: UUID, db: Session = Depends(get_db)):
    """
    Get ateam info of watching request.
    """
    watching_request = (
        db.query(models.ATeamWatchingRequest)
        .filter(models.ATeamWatchingRequest.request_id == str(request_id))
        .one_or_none()
    )
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
    ateam = validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert ateam
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    # ignore empty search.
    search = search if search else None

    subq = (
        select(
            models.ATeamPTeam.pteam_id.label("pteam_id"),
            models.PTeam.pteam_name.label("pteam_name"),
            models.PTeamTagReference.tag_id.label("tag_id"),
        )
        .distinct()
        .join(
            models.PTeam,
            and_(
                models.PTeam.pteam_id == models.ATeamPTeam.pteam_id,
                models.ATeamPTeam.ateam_id == str(ateam_id),
            ),
        )
        .join(
            models.PTeamTagReference,
            models.PTeamTagReference.pteam_id == models.ATeamPTeam.pteam_id,
        )
        .subquery()
    )

    sort_rules = sortkey2orderby[sort_key] + [
        models.TopicTag.topic_id,  # group by topic
        nullsfirst(models.PTeamTopicTagStatus.topic_status),  # worst state on array[0]
        models.PTeamTopicTagStatus.scheduled_at.desc(),  # latest on array[0] if worst is scheduled
        subq.c.pteam_name,
        models.Tag.tag_name,
    ]

    select_stmt = (
        select(
            subq.c.pteam_id,
            subq.c.pteam_name,
            models.Tag,
            models.TopicTag.topic_id,
            models.Topic.title,
            models.Topic.updated_at,
            models.Topic.threat_impact,
            models.PTeamTopicTagStatus,
        )
        .join(
            models.Tag,
            models.Tag.tag_id == subq.c.tag_id,
        )
        .join(
            models.TopicTag,
            models.TopicTag.tag_id.in_([models.Tag.tag_id, models.Tag.parent_id]),
        )
        .outerjoin(
            models.PTeamZone,
            models.PTeamZone.pteam_id == subq.c.pteam_id,
        )
        .outerjoin(
            models.TopicZone,
            models.TopicZone.topic_id == models.TopicTag.topic_id,
        )
        .join(
            models.Topic,
            and_(
                or_(
                    models.TopicZone.zone_name.is_(None),
                    models.TopicZone.zone_name == models.PTeamZone.zone_name,
                ),
                models.Topic.title.icontains(search, autoescape=True) if search else true(),
                models.Topic.disabled.is_(False),
                models.Topic.topic_id == models.TopicTag.topic_id,
            ),
        )
        .outerjoin(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == subq.c.pteam_id,
                models.CurrentPTeamTopicTagStatus.tag_id == subq.c.tag_id,
                models.CurrentPTeamTopicTagStatus.topic_id == models.TopicTag.topic_id,
            ),
        )
        .outerjoin(
            models.PTeamTopicTagStatus,
        )
        .order_by(*sort_rules)
        .distinct()
    )

    rows = db.execute(select_stmt).all()

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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    return (
        db.query(
            models.ATeamTopicComment.comment_id,
            models.ATeamTopicComment.topic_id,
            models.ATeamTopicComment.ateam_id,
            models.ATeamTopicComment.user_id,
            models.ATeamTopicComment.created_at,
            models.ATeamTopicComment.updated_at,
            models.ATeamTopicComment.comment,
            models.Account.email,
        )
        .join(
            models.Account,
            models.Account.user_id == models.ATeamTopicComment.user_id,
        )
        .filter(
            models.ATeamTopicComment.ateam_id == str(ateam_id),
            models.ATeamTopicComment.topic_id == str(topic_id),
        )
        .order_by(
            models.ATeamTopicComment.created_at.desc(),
        )
        .all()
    )


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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    check_ateam_membership(db, ateam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    comment = models.ATeamTopicComment(
        topic_id=str(topic_id),
        ateam_id=str(ateam_id),
        user_id=str(current_user.user_id),
        comment=data.comment,
        created_at=datetime.now(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    comment = (
        db.query(models.ATeamTopicComment)
        .filter(
            models.ATeamTopicComment.comment_id == str(comment_id),
        )
        .one_or_none()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    if comment.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    comment.comment = data.comment
    comment.updated_at = datetime.now()
    db.add(comment)
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
    validate_ateam(db, ateam_id, on_error=status.HTTP_404_NOT_FOUND)
    validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    comment = (
        db.query(models.ATeamTopicComment)
        .filter(
            models.ATeamTopicComment.comment_id == str(comment_id),
        )
        .one_or_none()
    )
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    if comment.user_id != current_user.user_id:
        check_ateam_auth(
            db,
            ateam_id,
            current_user.user_id,
            models.ATeamAuthIntFlag.ADMIN,
            on_error=status.HTTP_403_FORBIDDEN,
        )
    db.delete(comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
