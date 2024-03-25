import json
from datetime import datetime
from typing import Dict, List, Set
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.common import (
    auto_close_by_pteamtags,
    check_pteam_auth,
    check_pteam_membership,
    check_tags_exist,
    fix_current_status_by_pteam,
    get_current_pteam_topic_tag_status,
    get_or_create_topic_tag,
    get_pteam_topic_status_history,
    get_topics_internal,
    pteam_topic_tag_status_to_response,
    pteamtag_try_auto_close_topic,
    set_pteam_topic_status_internal,
    validate_actionlog,
    validate_topic,
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
NO_SUCH_PTEAM = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam")
NO_SUCH_TAG = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")


@router.get("", response_model=List[schemas.PTeamEntry])
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
    persistence.expire_pteam_invitations(db)

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

    invitation.used_count += 1

    db.commit()

    return invitation.pteam


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


@router.get("/{pteam_id}/groups", response_model=schemas.PTeamGroupResponse)
def get_pteam_groups(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get groups of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    groups = persistence.get_pteam_groups(db, pteam_id)

    return {"groups": groups}


@router.get("/{pteam_id}/tags", response_model=List[schemas.ExtTagResponse])
def get_pteam_tags(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tags of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return command.get_pteam_ext_tags(db, pteam)


@router.get("/{pteam_id}/tags/summary", response_model=schemas.PTeamTagsSummary)
def get_pteam_tags_summary(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary of the pteam tags.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    return command.get_pteamtags_summary(db, pteam)


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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    topic_ids = command.get_topic_ids_by_pteam_id_and_tag_id(db, pteam_id, tag_id, True)
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    topic_ids = command.get_topic_ids_by_pteam_id_and_tag_id(db, pteam_id, tag_id, False)
    threat_impact_count = command.count_pteam_topics_per_threat_impact(db, pteam_id, tag_id, False)

    return {
        "pteam_id": pteam_id,
        "tag_id": tag_id,
        "threat_impact_count": threat_impact_count,
        "topic_ids": topic_ids,
    }


@router.get("/{pteam_id}/topics", response_model=List[schemas.TopicResponse])
def get_pteam_topics(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topics of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    tag_ids = command.get_pteam_tag_ids(db, pteam_id)
    if not tag_ids:
        return []
    return get_topics_internal(db, current_user.user_id, tag_ids=tag_ids)


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
    pteam = persistence.create_pteam(db, pteam)

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


@router.post("/{pteam_id}/authority", response_model=List[schemas.PTeamAuthResponse])
def update_pteam_auth(
    pteam_id: UUID,
    requests: List[schemas.PTeamAuthRequest],
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
                authority=0,
            )
            auth = persistence.create_pteam_authority(db, auth)
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


@router.get("/{pteam_id}/authority", response_model=List[schemas.PTeamAuthResponse])
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
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


# FIXME!
# following get_pteamtag() has no tests!!!
#
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    ptrs = persistence.get_pteam_tag_references_by_tag_id(db, pteam_id, tag_id)
    references = [
        {
            "group": ptr.group,
            "target": ptr.target,
            "version": ptr.version,
        }
        for ptr in ptrs
    ]

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


def remove_specified_group_references_from_pteamtag(db, pteamtag, group):
    """
    Delete specified group's references from pteamtag
    """
    pteamtag.references = [
        reference for reference in pteamtag.references if reference["group"] != group
    ]
    # Note: This fuc deletes pteamtag when reference become empty.
    #       This specification is different from update_pteamtag.
    # If reference become empty, delete pteamtag
    if len(pteamtag.references) == 0:
        db.delete(pteamtag)
    # If reference remains, update pteamtag
    else:
        db.add(pteamtag)


@router.post("/{pteam_id}/upload_sbom_file", response_model=List[schemas.ExtTagResponse])
def upload_pteam_sbom_file(
    pteam_id: UUID,
    file: UploadFile,
    group: str = Query("", description="name of group(repository or product)"),
    force_mode: bool = Query(False, description="if true, create unexist tags"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    upload sbom file
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing group")
    _check_file_extention(file, ".json")
    _check_empty_file(file)
    try:
        jdata = json.load(file.file)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Wrong file content"),
        ) from error

    try:
        json_lines = sbom_json_to_artifact_json_lines(jdata)
        return apply_group_tags(
            db,
            pteam,
            group,
            json_lines,
            auto_create_tags=force_mode,
            auto_close=False,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/{pteam_id}/upload_tags_file", response_model=List[schemas.ExtTagResponse])
def upload_pteam_tags_file(
    pteam_id: UUID,
    file: UploadFile,
    group: str = Query("", description="name of group(repository or product)"),
    force_mode: bool = Query(False, description="if true, create unexist tags"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update pteam tags by uploading a .jsonl file.

    Format of file content must be JSON Lines.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing group")
    _check_file_extention(file, ".jsonl")
    _check_empty_file(file)

    # Read from file
    json_lines = []
    for bline in file.file:
        json_lines.append(_json_loads(bline))

    try:
        return apply_group_tags(
            db, pteam, group, json_lines, auto_create_tags=force_mode, auto_close=True
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


def apply_group_tags(
    db: Session,
    pteam: models.PTeam,
    group: str,
    json_lines: List[dict],
    auto_create_tags=False,
    auto_close=False,
) -> List[schemas.ExtTagResponse]:
    # Check file format and get tag_names
    tag_names_in_file: Set[str] = set()
    for line in json_lines:
        if not (_tag_name := line.get("tag_name")):
            raise ValueError("Missing tag_name")
        if not (_refs := line.get("references")):
            raise ValueError("Missing references")
        if any(None in {_ref.get("target"), _ref.get("version")} for _ref in _refs):
            raise ValueError("Missing target and|or version")
        tag_names_in_file.add(_tag_name)

    # If force_mode is False, check whether tag_names exist in DB
    if auto_create_tags is False:
        check_tags_exist(db, list(tag_names_in_file))
    tag_name_to_id: Dict[str, str] = {
        tag_name: get_or_create_topic_tag(db, tag_name).tag_id for tag_name in tag_names_in_file
    }
    if auto_close:
        get_versions_query = (
            select(
                models.PTeamTagReference.tag_id,
                func.array_agg(models.PTeamTagReference.version).label("versions"),
            )
            .where(models.PTeamTagReference.pteam_id == pteam.pteam_id)
            .group_by(models.PTeamTagReference.tag_id)
        )
        old_version_rows = db.execute(get_versions_query).all()
        old_versions: Dict[str, Set[str]] = {
            row_.tag_id: set(row_.versions) for row_ in old_version_rows
        }

    db.execute(
        delete(models.PTeamTagReference).where(
            models.PTeamTagReference.pteam_id == pteam.pteam_id,
            models.PTeamTagReference.group == group,
        )
    )
    new_params = {
        (tag_name_to_id[json_line["tag_name"]], refs.get("target", ""), refs.get("version", ""))
        for json_line in json_lines
        for refs in json_line.get("references", [{"target": "", "version": ""}])
    }
    db.add_all(
        [
            models.PTeamTagReference(
                pteam_id=pteam.pteam_id,
                group=group,
                tag_id=new_param[0],
                target=new_param[1],
                version=new_param[2],
            )
            for new_param in new_params
        ]
    )

    # try auto close if make sense
    if auto_close:
        db.flush()
        new_version_rows = db.execute(get_versions_query).all()
        new_versions: Dict[str, Set[str]] = {
            row_.tag_id: set(row_.versions) for row_ in new_version_rows
        }

        ptrs = db.scalars(
            select(models.PTeamTagReference)
            .options(joinedload(models.PTeamTagReference.tag, innerjoin=True))
            .where(models.PTeamTagReference.pteam_id == pteam.pteam_id)
        ).all()
        if ptrs_for_auto_close := [
            ptr
            for ptr in ptrs
            if new_versions.get(ptr.tag_id, set()) != old_versions.get(ptr.tag_id, set())
        ]:
            auto_close_by_pteamtags(db, [(pteam, ptr.tag) for ptr in ptrs_for_auto_close])

    db.flush()
    db.refresh(pteam)
    fix_current_status_by_pteam(db, pteam)

    db.commit()
    return command.get_pteam_ext_tags(db, pteam)


@router.delete("/{pteam_id}/tags", status_code=status.HTTP_204_NO_CONTENT)
def remove_pteamtags_by_group(
    pteam_id: UUID,
    group: str = Query("", description="name of group(repository or product)"),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove pteam tags filtered by group.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    db.execute(
        delete(models.PTeamTagReference).where(
            models.PTeamTagReference.pteam_id == str(pteam_id),
            models.PTeamTagReference.group == group,
        )
    )
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

    need_auto_close = data.disabled is False and pteam.disabled is True

    if data.pteam_name is not None:
        pteam.pteam_name = data.pteam_name
    if data.contact_info is not None:
        pteam.contact_info = data.contact_info
    if data.alert_threat_impact is not None:
        pteam.alert_threat_impact = data.alert_threat_impact
    if data.disabled is not None:
        pteam.disabled = data.disabled
    if data.alert_mail is not None:
        pteam.alert_mail = models.PTeamMail(**data.alert_mail.__dict__)

    db.add(pteam)

    if pteam.disabled:
        db.query(models.PTeamInvitation).filter(
            models.PTeamInvitation.pteam_id == str(pteam_id)
        ).delete()
    elif need_auto_close:
        db.flush()
        pteamtags = db.execute(
            select(
                models.PTeamTagReference.tag_id.distinct(),
                models.PTeam,
                models.Tag,
            )
            .join(
                models.PTeam,
                and_(
                    models.PTeam.pteam_id == pteam.pteam_id,
                    models.PTeamTagReference.pteam_id == pteam.pteam_id,
                ),
            )
            .join(models.Tag)
        ).all()
        auto_close_by_pteamtags(db, [(pteamtag.PTeam, pteamtag.Tag) for pteamtag in pteamtags])

    db.flush()
    db.refresh(pteam)
    fix_current_status_by_pteam(db, pteam)

    db.commit()
    db.refresh(pteam)
    return pteam


def _get_pteam_topic_statuses_summary(db: Session, pteam: models.PTeam, tag: models.Tag) -> dict:
    rows = (
        db.query(
            models.Tag,
            models.Topic,
            models.PTeamTopicTagStatus.created_at.label("executed_at"),
            models.PTeamTopicTagStatus.topic_status,
        )
        .filter(
            models.Tag.tag_id == tag.tag_id,
        )
        .join(
            models.TopicTag, models.TopicTag.tag_id.in_([models.Tag.tag_id, models.Tag.parent_id])
        )
        .join(
            models.Topic,
            and_(
                models.Topic.disabled.is_(False),
                models.Topic.topic_id == models.TopicTag.topic_id,
            ),
        )
        .outerjoin(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
                models.CurrentPTeamTopicTagStatus.tag_id == models.Tag.tag_id,
                models.CurrentPTeamTopicTagStatus.topic_id == models.TopicTag.topic_id,
            ),
        )
        .outerjoin(
            models.PTeamTopicTagStatus,
        )
        .order_by(
            models.Topic.threat_impact,
            models.Topic.updated_at.desc(),
        )
        .all()
    )

    return {
        "tag_id": tag.tag_id,
        "topics": [
            {
                **row.Topic.__dict__,
                "topic_status": row.topic_status or models.TopicStatusType.alerted,
                "executed_at": row.executed_at,
            }
            for row in rows
        ],
    }


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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")
    return _get_pteam_topic_statuses_summary(db, pteam, tag)


@router.get("/{pteam_id}/topicstatus", response_model=List[schemas.TopicStatusResponse])
def get_pteam_topic_status_list(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topic status list of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    return get_pteam_topic_status_history(db, pteam_id=pteam_id)


@router.post(
    "/{pteam_id}/topicstatus/{topic_id}/{tag_id}", response_model=schemas.TopicStatusResponse
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    # TODO: should check pteam auth: topic_status

    if not (topic := validate_topic(db, topic_id)):  # FIXME: use get_topic_by_id
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
    # TODO: should check pteam topic???
    # TODO: should check topic tag?? -- should care about parent&child

    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    if not command.check_tag_is_related_to_topic(db, tag, topic):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag mismatch")

    if data.topic_status not in {
        models.TopicStatusType.acknowledged,
        models.TopicStatusType.scheduled,
        models.TopicStatusType.completed,
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")

    for logging_id_ in data.logging_ids:
        validate_actionlog(
            db,
            logging_id=logging_id_,
            pteam_id=pteam_id,
            topic_id=topic_id,
            on_error=status.HTTP_400_BAD_REQUEST,
        )
    for assignee in data.assignees:
        if not check_pteam_membership(db, pteam, persistence.get_account_by_id(db, assignee)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a pteam member",
            )

    ret = set_pteam_topic_status_internal(db, current_user, pteam, topic_id, tag, data)
    assert ret
    return ret


@router.get(
    "/{pteam_id}/topicstatus/{topic_id}/{tag_id}", response_model=schemas.TopicStatusResponse
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    assert topic
    # TODO: should check pteam topic???
    # TODO: should check topic tag?? -- should care about parent&child

    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    current_row = get_current_pteam_topic_tag_status(db, pteam, topic_id, tag)
    if current_row is None or current_row.status_id is None:
        return {
            "pteam_id": pteam_id,
            "topic_id": topic_id,
            "tag_id": tag_id,
        }
    return pteam_topic_tag_status_to_response(db, current_row)


@router.get("/{pteam_id}/members", response_model=List[schemas.UserResponse])
def get_pteam_members(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get members of the pteam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if current_user.user_id != str(user_id) and not check_pteam_auth(
        db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN
    ):
        raise NOT_HAVE_AUTH

    target_users = [x for x in pteam.members if x.user_id == str(user_id)]
    if len(target_users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam member")

    # remove all extra authorities  # FIXME: should be deleted on cascade
    db.execute(
        delete(models.PTeamAuthority).where(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            models.PTeamAuthority.user_id == str(user_id),
        )
    )

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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
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

    persistence.expire_pteam_invitations(db)

    del request.authorities
    token = models.PTeamInvitation(
        pteam_id=str(pteam_id),
        user_id=current_user.user_id,
        authority=intflag,
        **request.model_dump(),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    return schemas.PTeamInvitationResponse(
        **token.__dict__, authorities=models.PTeamAuthIntFlag(token.authority).to_enums()
    )


@router.get("/{pteam_id}/invitation", response_model=List[schemas.PTeamInvitationResponse])
def list_invitations(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List effective invitations.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH

    persistence.expire_pteam_invitations(db)

    return [
        schemas.PTeamInvitationResponse(
            **row.__dict__, authorities=models.PTeamAuthIntFlag(row.authority).to_enums()
        )
        for row in db.query(models.PTeamInvitation)
        .filter(models.PTeamInvitation.pteam_id == str(pteam_id))
        .all()
    ]


@router.delete("/{pteam_id}/invitation/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invitation(
    pteam_id: UUID,
    invitation_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.INVITE):
        raise NOT_HAVE_AUTH

    persistence.expire_pteam_invitations(db)

    db.query(models.PTeamInvitation).filter(
        models.PTeamInvitation.invitation_id == str(invitation_id)
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.get("/{pteam_id}/watchers", response_model=List[schemas.ATeamEntry])
def get_pteam_watchers(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get watching pteams of the ateam.
    """
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
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
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_auth(db, pteam, current_user, models.PTeamAuthIntFlag.ADMIN):
        raise NOT_HAVE_AUTH

    pteam.ateams = [ateams for ateams in pteam.ateams if ateams.ateam_id != str(ateam_id)]
    db.add(pteam)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{pteam_id}/fix_status_mismatch")
def fix_status_mismatch(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER

    select_stmt = (
        select(models.CurrentPTeamTopicTagStatus)
        .options(
            joinedload(models.CurrentPTeamTopicTagStatus.pteam, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.tag, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.topic, innerjoin=True),
        )
        .outerjoin(models.PTeamTopicTagStatus)
        .where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            or_(
                models.CurrentPTeamTopicTagStatus.topic_status.in_(
                    [
                        models.TopicStatusType.alerted,
                        models.TopicStatusType.acknowledged,
                    ]
                ),
                and_(
                    models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.scheduled,
                    models.PTeamTopicTagStatus.scheduled_at < datetime.now(),
                ),
            ),
        )
    )

    rows = db.scalars(select_stmt).all()
    for row in rows:
        pteamtag_try_auto_close_topic(db, row.pteam, row.tag, row.topic)

    return Response(status_code=status.HTTP_200_OK)


@router.post("/{pteam_id}/tags/{tag_id}/fix_status_mismatch")
def fix_status_mismatch_tag(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (pteam := persistence.get_pteam_by_id(db, pteam_id)) or pteam.disabled:
        raise NO_SUCH_PTEAM
    if not check_pteam_membership(db, pteam, current_user):
        raise NOT_A_PTEAM_MEMBER
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise NO_SUCH_TAG
    if tag not in {ref.tag for ref in pteam.references}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    select_stmt = (
        select(models.CurrentPTeamTopicTagStatus)
        .options(
            joinedload(models.CurrentPTeamTopicTagStatus.pteam, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.tag, innerjoin=True),
            joinedload(models.CurrentPTeamTopicTagStatus.topic, innerjoin=True),
        )
        .outerjoin(models.PTeamTopicTagStatus)
        .where(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
            or_(
                models.CurrentPTeamTopicTagStatus.topic_status.in_(
                    [
                        models.TopicStatusType.alerted,
                        models.TopicStatusType.acknowledged,
                    ]
                ),
                and_(
                    models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.scheduled,
                    models.PTeamTopicTagStatus.scheduled_at < datetime.now(),
                ),
            ),
        )
    )

    rows = db.scalars(select_stmt).all()

    for row in rows:
        pteamtag_try_auto_close_topic(db, row.pteam, row.tag, row.topic)

    return Response(status_code=status.HTTP_200_OK)
