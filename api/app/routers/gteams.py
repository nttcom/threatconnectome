from datetime import datetime
from typing import List, Sequence, Tuple, Union, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    check_gteam_auth,
    check_gteam_membership,
    validate_gteam,
    validate_zone,
)
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID
from app.database import get_db
from app.routers.zones import create_zone_internal, delete_zone_internal

router = APIRouter(prefix="/gteams", tags=["gteams"])


def _modify_gteam_auth(
    db: Session,
    gteam_id: Union[UUID, str],
    authes: List[
        Tuple[
            Union[UUID, str],  # user_id
            Union[models.GTeamAuthIntFlag, int],  # auth. 0 for delete
        ]
    ],
):
    for user_id, auth in authes:
        if str(user_id) in map(str, [MEMBER_UUID, NOT_MEMBER_UUID]):
            if auth & models.GTeamAuthIntFlag.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot give ADMIN to pseudo account",
                )
        else:
            check_gteam_membership(db, gteam_id, user_id, on_error=status.HTTP_400_BAD_REQUEST)

    for user_id, auth in authes:
        row = (
            db.query(models.GTeamAuthority)
            .filter(
                models.GTeamAuthority.gteam_id == str(gteam_id),
                models.GTeamAuthority.user_id == str(user_id),
            )
            .one_or_none()
        )
        if row is None:
            if not auth:
                continue  # nothing to remove
            row = models.GTeamAuthority(gteam_id=str(gteam_id), user_id=str(user_id))
        if auth:
            row.authority = int(auth)
            db.add(row)
        else:
            db.delete(row)
    db.commit()


@router.get("", response_model=List[schemas.GTeamEntry])
def get_gteams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all gteam entries.
    """
    return db.query(models.GTeam).all()


@router.post("", response_model=schemas.GTeamInfo)
def create_gteam(
    data: schemas.GTeamCreateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a gteam.
    """
    gteam = models.GTeam(gteam_name=data.gteam_name.strip(), contact_info=data.contact_info.strip())
    current_user.gteams.append(gteam)
    db.add(current_user)
    db.commit()
    db.refresh(gteam)

    _modify_gteam_auth(
        db,
        gteam.gteam_id,
        [
            (current_user.user_id, models.GTeamAuthIntFlag.GTEAM_MASTER),
            (MEMBER_UUID, models.GTeamAuthIntFlag.GTEAM_MEMBER),
            (NOT_MEMBER_UUID, models.GTeamAuthIntFlag.FREE_TEMPLATE),
        ],
    )

    return gteam


@router.get("/auth_info", response_model=schemas.GTeamAuthInfo)
def get_auth_info(current_user: models.Account = Depends(get_current_user)):
    """
    Get gteam authority information.
    """
    return schemas.GTeamAuthInfo(
        authorities=[
            schemas.GTeamAuthInfo.GTeamAuthEntry(
                enum=key, name=str(value["name"]), desc=str(value["desc"])
            )
            for key, value in models.GTeamAuthEnum.info().items()
        ],
        pseudo_uuids=[
            schemas.GTeamAuthInfo.PseudoUUID(name="member", uuid=MEMBER_UUID),
            schemas.GTeamAuthInfo.PseudoUUID(name="others", uuid=NOT_MEMBER_UUID),
        ],
    )


@router.post("/apply_invitation", response_model=schemas.GTeamInfo)
def apply_invitation(
    data: schemas.ApplyInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply invitation to gteam.
    """
    _expire_invitations(db)

    invitation = (
        db.query(models.GTeamInvitation)
        .filter(
            models.GTeamInvitation.invitation_id == str(data.invitation_id),
            or_(
                models.GTeamInvitation.limit_count.is_(None),
                models.GTeamInvitation.limit_count > models.GTeamInvitation.used_count,
            ),
        )
        .with_for_update()
        .one_or_none()
    )  # lock and block!
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) invitation id"
        )
    if current_user in invitation.gteam.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined to the gteam"
        )

    invitation.gteam.members.append(current_user)
    invitation.used_count += 1
    if invitation.authority > 0:
        gteam_auth = db.query(models.GTeamAuthority).filter(
            models.GTeamAuthority.gteam_id == invitation.gteam_id,
            models.GTeamAuthority.user_id == current_user.user_id,
        ).one_or_none() or models.GTeamAuthority(
            gteam_id=invitation.gteam_id, user_id=current_user.user_id, authority=0
        )
        gteam_auth.authority |= invitation.authority
        db.add(gteam_auth)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation.gteam


@router.get("/{gteam_id}", response_model=schemas.GTeamInfo)
def get_gteam(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get gteam details. members only.
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_membership(db, gteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    return gteam


@router.put("/{gteam_id}", response_model=schemas.GTeamInfo)
def update_gteam(
    gteam_id: UUID,
    data: schemas.GTeamUpdateRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a gteam.
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_auth(
        db,
        gteam_id,
        current_user.user_id,
        models.GTeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    for key, value in data:
        if value is None:
            continue
        setattr(gteam, key, value)
    db.add(gteam)
    db.commit()
    db.refresh(gteam)

    return gteam


@router.post("/{gteam_id}/authority", response_model=List[schemas.GTeamAuthResponse])
def update_gteam_auth(
    gteam_id: UUID,
    requests: List[schemas.GTeamAuthRequest],
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update gteam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : gteam member
      - 00000000-0000-0000-0000-0000cafe0002 : not gteam member
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_auth(
        db,
        gteam_id,
        current_user.user_id,
        models.GTeamAuthIntFlag.ADMIN,
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
        check_gteam_membership(db, gteam_id, str_id, on_error=status.HTTP_400_BAD_REQUEST)

    if not any(models.GTeamAuthEnum.ADMIN in x.authorities for x in requests):
        _guard_last_admin(db, gteam_id, str_ids)

    _modify_gteam_auth(
        db,
        gteam_id,
        [(x.user_id, models.GTeamAuthIntFlag.from_enums(x.authorities)) for x in requests],
    )

    authes = (
        db.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam_id),
            models.GTeamAuthority.user_id.in_(str_ids),
        )
        .all()
    )
    auth_map = {x.user_id: models.GTeamAuthIntFlag(x.authority).to_enums() for x in authes}
    response = [
        {"user_id": user_id, "authorities": auth_map.get(user_id) or []} for user_id in str_ids
    ]
    return response


@router.get("/{gteam_id}/authority", response_model=List[schemas.GTeamAuthResponse])
def get_gteam_auth(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get gteam authority.

    Pseudo UUIDs:
      - 00000000-0000-0000-0000-0000cafe0001 : gteam member
      - 00000000-0000-0000-0000-0000cafe0002 : not gteam member
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    rows = (
        db.query(models.GTeamAuthority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam_id),
            (
                true()
                if check_gteam_membership(db, gteam_id, current_user.user_id)
                else models.GTeamAuthority.user_id == str(NOT_MEMBER_UUID)
            ),  # limit if not a member
        )
        .all()
    )
    return [
        {"user_id": row.user_id, "authorities": models.GTeamAuthIntFlag(row.authority).to_enums()}
        for row in rows
    ]


@router.get("/{gteam_id}/members", response_model=List[schemas.UserResponse])
def get_gteam_members(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get members of the gteam.
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_membership(db, gteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    return gteam.members


def _guard_last_admin(db: Session, gteam_id: UUID, excludes: Sequence[Union[UUID, str]]):
    if (
        db.query(models.GTeamAuthority.user_id)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam_id),
            models.GTeamAuthority.authority.op("&")(models.GTeamAuthIntFlag.ADMIN) > 0,
            models.GTeamAuthority.user_id.not_in(list(map(str, excludes))),
        )
        .count()
        == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )


@router.delete("/{gteam_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    gteam_id: UUID,
    user_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    User leaves the gteam.
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    if user_id in {MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove pseudo account"
        )
    if current_user.user_id != str(user_id):
        check_gteam_auth(
            db,
            gteam_id,
            current_user.user_id,
            models.GTeamAuthIntFlag.ADMIN,
            on_error=status.HTTP_403_FORBIDDEN,
        )
    check_gteam_membership(db, gteam_id, user_id, on_error=status.HTTP_404_NOT_FOUND)
    _guard_last_admin(db, gteam_id, [user_id])
    _modify_gteam_auth(db, gteam_id, [(user_id, 0)])

    gteam.members = [user for user in gteam.members if user.user_id != str(user_id)]
    db.add(gteam)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _expire_invitations(db: Session):
    db.query(models.GTeamInvitation).filter(
        or_(
            models.GTeamInvitation.expiration < datetime.now(),
            and_(
                models.GTeamInvitation.limit_count.is_not(None),
                models.GTeamInvitation.used_count >= models.GTeamInvitation.limit_count,
            ),
        )
    ).delete()
    db.commit()


@router.post("/{gteam_id}/invitation", response_model=schemas.GTeamInvitationResponse)
def create_invitation(
    gteam_id: UUID,
    data: schemas.GTeamInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new gteam invitation token.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_auth(
        db,
        gteam_id,
        current_user.user_id,
        models.GTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    if data.authorities is not None and not check_gteam_auth(
        db, gteam_id, current_user.user_id, models.GTeamAuthIntFlag.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADMIN required to set authorities"
        )
    intflag = models.GTeamAuthIntFlag.from_enums(data.authorities or [])
    if data.limit_count is not None and data.limit_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unwise limit_count (give null for unlimited)",
        )

    _expire_invitations(db)

    del data.authorities
    invitation = models.GTeamInvitation(
        gteam_id=str(gteam_id), user_id=current_user.user_id, authority=intflag, **data.model_dump()
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return {
        **invitation.__dict__,
        "authorities": models.GTeamAuthIntFlag(invitation.authority).to_enums(),
    }


@router.get("/{gteam_id}/invitation", response_model=List[schemas.GTeamInvitationResponse])
def list_invitation(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List effective invitations.
    """
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_auth(
        db,
        gteam_id,
        current_user.user_id,
        models.GTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    _expire_invitations(db)

    return [
        {**item.__dict__, "authorities": models.GTeamAuthIntFlag(item.authority).to_enums()}
        for item in gteam.invitations
    ]


@router.delete("/{gteam_id}/invitation/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invitation(
    gteam_id: UUID,
    invitation_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invalidate invitation to gteam.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_auth(
        db,
        gteam_id,
        current_user.user_id,
        models.GTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    _expire_invitations(db)

    # omit validating invitation to avoid raising error if already expired.
    db.query(models.GTeamInvitation).filter(
        models.GTeamInvitation.invitation_id == str(invitation_id)
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/invitation/{invitation_id}", response_model=schemas.GTeamInviterResponse)
def invited_gteam(invitation_id: UUID, db: Session = Depends(get_db)):
    """
    Get invited gteam info.
    """
    invitation = (
        db.query(models.GTeamInvitation)
        .filter(models.GTeamInvitation.invitation_id == str(invitation_id))
        .one_or_none()
    )
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such invitation (or already expired)"
        )
    resp = {
        "gteam_id": invitation.gteam.gteam_id,
        "gteam_name": invitation.gteam.gteam_name,
        "email": invitation.inviter.email,
        "user_id": invitation.user_id,
    }
    return resp


@router.get("/{gteam_id}/zones/summary", response_model=schemas.GTeamZonesSummary)
def get_gteam_zones_summary(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get gteam zone summary to make zone page.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_membership(db, gteam_id, current_user.user_id, on_error=status.HTTP_404_NOT_FOUND)

    db_zones = db.query(models.Zone).filter(models.Zone.gteam_id == str(gteam_id)).all()

    zone_names = [zone.zone_name for zone in db_zones]

    zones_pteams = (
        db.query(models.PTeam)
        .join(
            models.PTeamZone,
            and_(
                models.PTeamZone.zone_name.in_(zone_names),
                models.PTeamZone.pteam_id == models.PTeam.pteam_id,
            ),
        )
        .all()
    )

    topics = (
        db.query(models.Topic)
        .join(
            models.TopicZone,
            and_(
                models.TopicZone.zone_name.in_(zone_names),
                models.TopicZone.topic_id == models.Topic.topic_id,
            ),
        )
        .order_by(models.Topic.updated_at.desc())
        .all()
    )

    actions = (
        db.query(models.TopicAction)
        .join(
            models.ActionZone,
            and_(
                models.ActionZone.zone_name.in_(zone_names),
                models.ActionZone.action_id == models.TopicAction.action_id,
            ),
        )
        .all()
    )

    unarchived_zones = []
    archived_zones = []
    for zone in db_zones:
        z_pteams = [
            pteam
            for pteam in zones_pteams
            if (zone.zone_name in [z.zone_name for z in pteam.zones])
        ]
        z_topics = [
            topic for topic in topics if (zone.zone_name in [z.zone_name for z in topic.zones])
        ]
        z_actions = [
            action for action in actions if (zone.zone_name in [z.zone_name for z in action.zones])
        ]
        result = {
            **zone.__dict__,
            "pteams": z_pteams,
            "topics": z_topics,  # ordered by updated_at
            "actions": z_actions,
        }
        if zone.archived is True:
            archived_zones.append(result)
        else:
            unarchived_zones.append(result)

    return {"unarchived_zones": unarchived_zones, "archived_zones": archived_zones}


@router.get("/{gteam_id}/zones", response_model=List[schemas.ZoneEntry])
def list_gteam_zones(
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List zones bound with a gteam.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_membership(db, gteam_id, current_user.user_id, on_error=status.HTTP_404_NOT_FOUND)

    return db.query(models.Zone).filter(models.Zone.gteam_id == str(gteam_id)).all()


@router.get("/{gteam_id}/zones/{zone_name}", response_model=schemas.ZoneInfo)
def get_gteam_zone(
    gteam_id: UUID,
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get zone info.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_membership(db, gteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    return cast(
        models.Zone,
        validate_zone(
            db,
            current_user.user_id,
            zone_name,
            on_error=status.HTTP_404_NOT_FOUND,
            auth_mode="read",
            on_auth_error=status.HTTP_403_FORBIDDEN,
        ),
    )


@router.post("/{gteam_id}/zones", response_model=schemas.ZoneInfo)
def create_zone(
    request: schemas.ZoneRequest,
    gteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a zone bound with a gteam.
    """
    return create_zone_internal(db, request, gteam_id, current_user)


@router.put("/{gteam_id}/zones/{zone_name}", response_model=schemas.ZoneInfo)
def update_zone_info(
    request: schemas.ZoneUpdateRequest,
    gteam_id: UUID,
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update zone info.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    row = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="admin",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert row
    for key, value in request:
        if value is not None:
            setattr(row, key, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{gteam_id}/zones/{zone_name}/archived", response_model=schemas.ZoneInfo)
def update_zone_archived(
    request: schemas.ZoneUpdateArchivedRequest,
    gteam_id: UUID,
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update zone archived.
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    row = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="admin",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert row
    row.archived = request.archived
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{gteam_id}/zones/{zone_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    gteam_id: UUID,
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a zone.
    """
    delete_zone_internal(db, zone_name, gteam_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{gteam_id}/zones/{zone_name}/pteams/{pteam_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_zone_from_pteam(
    gteam_id: UUID,
    zone_name: str,
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove zone from pteam with the authority of gteam
    """
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    zone_row = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="admin",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone_row
    pteam_zone_row = (
        db.query(models.PTeamZone)
        .filter(models.PTeamZone.zone_name == zone_name, models.PTeamZone.pteam_id == str(pteam_id))
        .one_or_none()
    )
    if pteam_zone_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such relationship between pteam and zone",
        )
    db.delete(pteam_zone_row)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
