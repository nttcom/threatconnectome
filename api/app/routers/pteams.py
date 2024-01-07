import json
from datetime import datetime
from typing import Any, Dict, List, Sequence, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func, true

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    auto_close_by_pteamtags,
    check_pteam_auth,
    check_pteam_membership,
    check_tags_exist,
    check_zone_accessible,
    fix_current_status_by_pteam,
    get_current_pteam_topic_tag_status,
    get_or_create_topic_tag,
    get_pteam_topic_status_history,
    get_pteamtags_summary,
    get_topics_internal,
    pteam_topic_tag_status_to_response,
    set_pteam_topic_status_internal,
    update_zones,
    validate_pteam,
    validate_pteamtag,
    validate_topic,
)
from app.constants import (
    DEFAULT_ALERT_THREAT_IMPACT,
    MEMBER_UUID,
    NOT_MEMBER_UUID,
)
from app.database import get_db
from app.repository.account import AccountRepository
from app.repository.tag import TagRepository
from app.slack import validate_slack_webhook_url

router = APIRouter(prefix="/pteams", tags=["pteams"])


def _modify_pteam_auth(
    db: Session,
    pteam_id: Union[UUID, str],
    user_id: Union[UUID, str],  # user_id
    auth: Union[models.PTeamAuthIntFlag, int],  # auth, 0 for delete
):
    """
    Set PteamAuthority (privilege in pteam) as auth.
    auth is integer representing authority.
    if auth = 0, delete PteamAuthority.
    """

    is_pseudo_user = str(user_id) in map(str, [MEMBER_UUID, NOT_MEMBER_UUID])
    if is_pseudo_user:
        if auth & models.PTeamAuthIntFlag.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot give ADMIN to pseudo account",
            )
        else:
            pass  # skip check_pteam_membership for system user
    else:
        check_pteam_membership(db, pteam_id, user_id, on_error=status.HTTP_400_BAD_REQUEST)

    current_auth = (
        db.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            models.PTeamAuthority.user_id == str(user_id),
        )
        .one_or_none()
    )

    # Note: 0 is not valid as PTeamAuthIntFlag, 0 represents deletion operation here.
    is_delete = auth == 0
    if is_delete:
        if current_auth:  # 1. delete
            db.delete(current_auth)
        else:  # 2. nothing to do
            pass
    else:
        if current_auth:  # 3. update
            current_auth.authority = int(auth)
        else:  # 4. create
            current_auth = models.PTeamAuthority(
                pteam_id=str(pteam_id), user_id=str(user_id), authority=int(auth)
            )
        db.add(current_auth)


def _extend_pteam_tags(pteam: models.PTeam):
    # FIXME: tags should be purged from pteam. it's too heavy to create & read(on UI).
    setattr(
        pteam,
        "tags",
        [
            {
                "tag_name": pteamtag.tag.tag_name,
                "tag_id": pteamtag.tag.tag_id,
                "parent_name": pteamtag.tag.parent_name,
                "parent_id": pteamtag.tag.parent_id,
                "references": pteamtag.references or [],
                "text": pteamtag.text,
            }
            for pteamtag in pteam.pteamtags
        ],
    )
    return pteam


@router.get("", response_model=List[schemas.PTeamEntry])
def get_pteams(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all pteams list.
    """
    return db.query(models.PTeam).all()


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


@router.get("/{pteam_id}", response_model=schemas.PTeamInfo)
def get_pteam(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pteam details. members only.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND, ignore_disabled=True)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    return _extend_pteam_tags(pteam)


@router.get("/{pteam_id}/groups", response_model=schemas.PTeamGroupResponse)
def get_pteam_groups(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get groups of the pteam.
    """
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    unique_groups = set()
    pteam = (
        db.query(models.PTeam)
        .options(joinedload(models.PTeam.pteamtags))
        .filter(models.PTeam.pteam_id == str(pteam_id))
        .one_or_none()
    )
    assert pteam
    for pteamtag in pteam.pteamtags:
        for reference in pteamtag.references:
            group = reference.get("group", None)
            if group is not None:
                unique_groups.add(reference["group"])

    return schemas.PTeamGroupResponse(groups=list(unique_groups))


@router.get("/{pteam_id}/tags", response_model=List[schemas.ExtTagResponse])
def get_pteam_tags(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tags of the pteam.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    return sorted(
        [
            schemas.ExtTagResponse(
                **pteamtag.tag.__dict__, references=pteamtag.references, text=pteamtag.text
            )
            for pteamtag in pteam.pteamtags
        ],
        key=lambda x: x.tag_name,
    )


def _counts_topic_per_threat_impact(
    db: Session,
    pteam_id: Union[UUID, str],
    tag_id: Union[UUID, str],
    is_solved: bool,
) -> Dict[str, int]:
    threat_counts_rows = (
        db.query(
            models.CurrentPTeamTopicTagStatus.threat_impact,
            func.count(models.CurrentPTeamTopicTagStatus.threat_impact).label("num_rows"),
        )
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
            models.CurrentPTeamTopicTagStatus.topic_status == models.TopicStatusType.completed
            if is_solved
            else models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed,
        )
        .group_by(models.CurrentPTeamTopicTagStatus.threat_impact)
        .all()
    )
    return {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        **{str(row.threat_impact): row.num_rows for row in threat_counts_rows},
    }


def _get_tagged_topic_ids_by_pteam_id_and_status(
    db: Session,
    pteam_id: Union[UUID, str],
    tag_id: Union[UUID, str],
    is_solved: bool,
) -> List[UUID]:
    topic_ids_rows = (
        db.query(models.CurrentPTeamTopicTagStatus.topic_id)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
            models.CurrentPTeamTopicTagStatus.topic_status == models.TopicStatusType.completed
            if is_solved
            else models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed,
        )
        .order_by(
            models.CurrentPTeamTopicTagStatus.threat_impact,
            models.CurrentPTeamTopicTagStatus.updated_at.desc(),
        )
        .all()
    )

    return [row.topic_id for row in topic_ids_rows]


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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    tag_repository = TagRepository(db)
    tag = tag_repository.get_tag_by_id(tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    requested_pteamtag = (
        db.query(models.PTeamTag)
        .filter(
            models.PTeamTag.pteam_id == str(pteam_id),
            models.PTeamTag.tag_id == str(tag_id),
        )
        .one_or_none()
    )
    if requested_pteamtag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")
    topic_ids = _get_tagged_topic_ids_by_pteam_id_and_status(db, pteam_id, tag_id, True)
    threat_impact_count = _counts_topic_per_threat_impact(db, pteam_id, tag_id, True)

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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    tag_repository = TagRepository(db)
    tag = tag_repository.get_tag_by_id(tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    requested_pteamtag = (
        db.query(models.PTeamTag)
        .filter(
            models.PTeamTag.pteam_id == str(pteam_id),
            models.PTeamTag.tag_id == str(tag_id),
        )
        .one_or_none()
    )
    if requested_pteamtag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    topic_ids = _get_tagged_topic_ids_by_pteam_id_and_status(db, pteam_id, tag_id, False)
    threat_impact_count = _counts_topic_per_threat_impact(db, pteam_id, tag_id, False)

    return {
        "pteam_id": pteam_id,
        "tag_id": tag_id,
        "threat_impact_count": threat_impact_count,
        "topic_ids": topic_ids,
    }


@router.get("/{pteam_id}/tags/summary", response_model=schemas.PTeamTagsSummary)
def get_pteam_tags_summary(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary of the pteam tags.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    return get_pteamtags_summary(db, pteam)


@router.get("/{pteam_id}/topics", response_model=List[schemas.TopicResponse])
def get_pteam_topics(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topics of the pteam.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    rows = (
        db.query(models.Tag.tag_id)
        .filter(
            models.Tag.tag_id.in_(
                db.query(models.PTeamTag.tag_id).filter(models.PTeamTag.pteam_id == str(pteam_id))
            )
        )
        .all()
    )
    tag_ids = [row.tag_id for row in rows]
    #
    # FIXME:
    #   should fix the case current_user has more zones than this pteam.
    #
    return get_topics_internal(db, current_user.user_id, tag_ids=tag_ids)


def _db_update_pteamtags(
    db: Session,
    pteam: models.PTeam,
    tags: List[schemas.ExtTagRequest],
) -> models.PTeam:
    new_pteamtags = []
    for etag in tags:
        tag = get_or_create_topic_tag(db, etag.tag_name)
        states = [x for x in tag.pteamtags if x.pteam_id == pteam.pteam_id]
        if len(states) > 0:
            pteamtag = states[0]

            has_update = False
            if etag.references is not None and pteamtag.references != etag.references:
                pteamtag.references = etag.references
                has_update = True
            if etag.text is not None and pteamtag.text != etag.text:
                pteamtag.text = etag.text
                has_update = True

            if has_update:
                db.add(pteamtag)
        else:
            pteamtag = models.PTeamTag(references=etag.references, text=etag.text)
            tag.pteamtags.append(pteamtag)
            pteamtag.pteam = pteam
            db.add(pteamtag)
        new_pteamtags.append(pteamtag)
    pteam.pteamtags = new_pteamtags
    db.add(pteam)
    db.commit()
    db.refresh(pteam)
    return pteam


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
    if data.slack_webhook_url:
        validate_slack_webhook_url(data.slack_webhook_url)
    pteam = models.PTeam(
        pteam_name=data.pteam_name.strip(),
        contact_info=data.contact_info.strip(),
        slack_webhook_url=data.slack_webhook_url.strip(),
        alert_threat_impact=data.alert_threat_impact or DEFAULT_ALERT_THREAT_IMPACT,
    )
    db.add(pteam)
    pteam = _db_update_pteamtags(db, pteam, data.tags)
    pteam.zones = update_zones(db, current_user.user_id, True, [], data.zone_names)
    db.add(pteam)
    db.commit()
    db.refresh(pteam)

    if pteam.pteamtags:
        auto_close_by_pteamtags(db, pteam.pteamtags)
        fix_current_status_by_pteam(db, pteam)

    # join to the created pteam
    pteamaccount = models.PTeamAccount(pteam_id=pteam.pteam_id, user_id=current_user.user_id)
    db.add(pteamaccount)
    db.commit()
    db.refresh(pteamaccount)

    # set default authority
    _modify_pteam_auth(
        db, pteam.pteam_id, current_user.user_id, models.PTeamAuthIntFlag.PTEAM_MASTER
    )
    _modify_pteam_auth(db, pteam.pteam_id, MEMBER_UUID, models.PTeamAuthIntFlag.PTEAM_MEMBER)
    _modify_pteam_auth(db, pteam.pteam_id, NOT_MEMBER_UUID, models.PTeamAuthIntFlag.FREE_TEMPLATE)
    db.commit()

    return _extend_pteam_tags(pteam)


def _guard_last_admin(db: Session, pteam_id: UUID, excludes: Sequence[Union[str, UUID]]):
    left_admins = (
        db.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            models.PTeamAuthority.user_id.not_in(list(map(str, excludes))),
            models.PTeamAuthority.authority.op("&")(models.PTeamAuthIntFlag.ADMIN) != 0,
        )
        .all()
    )
    if len(left_admins) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Removing last ADMIN is not allowed"
        )


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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    str_ids = [str(request.user_id) for request in requests]
    account_repository = AccountRepository(db)
    if len(set(str_ids)) != len(str_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous request")
    for str_id in str_ids:
        if str_id not in [
            str(MEMBER_UUID),
            str(NOT_MEMBER_UUID),
        ] and not account_repository.get_account_by_userid(str_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    if len([x for x in requests if "admin" in x.authorities]) == 0:  # no admin in requests
        _guard_last_admin(db, pteam_id, str_ids)

    for x in requests:
        _modify_pteam_auth(
            db, pteam_id, x.user_id, models.PTeamAuthIntFlag.from_enums(x.authorities)
        )
    # TODO: Committ should be done in all it once for atomicity.
    db.commit()

    response = []
    for request in requests:
        auth = (
            db.query(models.PTeamAuthority)
            .filter(
                models.PTeamAuthority.pteam_id == str(pteam_id),
                models.PTeamAuthority.user_id == str(request.user_id),
            )
            .one_or_none()
        )
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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    rows = (
        db.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            (
                true()
                if check_pteam_membership(db, pteam_id, current_user.user_id)
                else models.PTeamAuthority.user_id == str(NOT_MEMBER_UUID)
            ),  # limit if not a member
        )
        .all()
    )
    response = []
    for row in rows:
        enums = models.PTeamAuthIntFlag(row.authority).to_enums()
        response.append({"user_id": row.user_id, "authorities": enums})
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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    tag_repository = TagRepository(db)
    tag = tag_repository.get_tag_by_id(tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    pteamtag = (
        db.query(models.PTeamTag)
        .filter(
            models.PTeamTag.pteam_id == str(pteam_id),
            models.PTeamTag.tag_id == str(tag_id),
        )
        .one_or_none()
    )
    if pteamtag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam tag")

    last_updated_at = (
        db.query(func.max(models.CurrentPTeamTopicTagStatus.updated_at))
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
            models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed,
        )
        .scalar()
    )
    setattr(pteamtag, "last_updated_at", last_updated_at)

    return pteamtag


@router.post("/{pteam_id}/tags/{tag_id}", response_model=schemas.PTeamtagResponse)
def add_pteamtag(
    pteam_id: UUID,
    tag_id: UUID,
    data: schemas.PTeamtagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add tag to pteamtag list.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    tag_repository = TagRepository(db)
    tag = tag_repository.get_tag_by_id(tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if tag.tag_id in [pteamtag.tag.tag_id for pteamtag in pteam.pteamtags]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")
    pteamtag = models.PTeamTag(
        pteam_id=str(pteam_id),
        tag_id=str(tag_id),
        references=data.references if data.references is not None else [],
        text=data.text if data.text is not None else "",
    )
    db.add(pteamtag)
    db.commit()
    db.refresh(pteamtag)

    auto_close_by_pteamtags(db, [pteamtag])
    fix_current_status_by_pteam(db, pteam)

    updated_pteamtag = validate_pteamtag(
        db, pteam_id, tag_id, on_error=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return updated_pteamtag


@router.put("/{pteam_id}/tags/{tag_id}", response_model=schemas.PTeamtagResponse)
def update_pteamtag(
    pteam_id: UUID,
    tag_id: UUID,
    data: schemas.PTeamtagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update text or references of a pteam tag.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    pteamtag = validate_pteamtag(db, pteam_id, tag_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteamtag

    if data.references is not None:
        pteamtag.references = data.references
    if data.text is not None:
        pteamtag.text = data.text
    db.add(pteamtag)
    db.commit()
    db.refresh(pteamtag)

    auto_close_by_pteamtags(db, [pteamtag])

    updated_pteamtag = validate_pteamtag(
        db, pteam_id, tag_id, on_error=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return updated_pteamtag


@router.delete("/{pteam_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pteamtag(
    pteam_id: UUID,
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a specified pteam tag. Not delete record on Tag table.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

    pteamtag = validate_pteamtag(db, pteam_id, tag_id, on_error=status.HTTP_404_NOT_FOUND)
    db.delete(pteamtag)
    db.commit()

    fix_current_status_by_pteam(db, pteam)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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


def _make_current_tags_dict(pteam: models.PTeam) -> dict[Any, dict[str, Any]]:
    return {
        pteamtag.tag.tag_name: {
            "pteamtag": pteamtag,
            "text": pteamtag.text or "",
            "versions": {ref.get("version", "") for ref in pteamtag.references},
        }
        for pteamtag in pteam.pteamtags
    }


def _json_load(s: str | bytes | bytearray):
    try:
        return json.loads(s)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Wrong file content: " + f'{s[:32]!s}{"..." if len(s) > 32 else ""}'),
        ) from error


def _merge_pteam_tags(
    db: Session,
    pteam: models.PTeam,
    group: str,
    currents: Dict[str, Dict[str, models.PTeamTag]],
    targets: Dict[str, Dict[str, models.PTeamTag]],
):
    for tag in currents:
        if tag in targets["keeps"] or tag in targets["ver_changed"] or tag in targets["infos"]:
            # already processed
            continue
        # not included in uploaded file.
        pteamtag = currents[tag]["pteamtag"]
        if len([ref for ref in pteamtag.references if ref.get("group", "") == group]) == 0:
            # group does not watching the tag from the beginning. do not touch about this.
            # Note:
            #   pteamtag.references can be empty. check it out to implement AUTO-PURGE.
            targets["keeps"][tag] = pteamtag
            continue
        # purge group
        new_refs = [ref for ref in pteamtag.references if (ref.get("group") or "") != group]
        if len(new_refs) == 0:  # no group watching anymore
            # will be deleted by updating pteam.pteamtags. nothing to do here.
            pass
        else:  # some other group still watching
            pteamtag.references = new_refs
            db.add(pteamtag)
            db.commit()
            db.refresh(pteamtag)
            targets["inuse"][tag] = pteamtag

    pteam.pteamtags = (
        list(targets["addings"].values())
        + list(targets["keeps"].values())
        + list(targets["ver_changed"].values())
        + list(targets["infos"].values())
        + list(targets["inuse"].values())
    )
    db.add(pteam)
    db.commit()
    db.refresh(pteam)

    if targets["addings"] or targets["ver_changed"]:
        pteamtags = list(targets["addings"].values()) + list(targets["ver_changed"].values())
        auto_close_by_pteamtags(db, pteamtags)

    if targets["addings"] or len(targets["keeps"]) != len(currents):
        # something added, modified or deleted.
        fix_current_status_by_pteam(db, pteam)


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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    _check_file_extention(file, ".jsonl")
    _check_empty_file(file)

    # Read from file
    json_lines = []
    for bline in file.file:
        json_lines.append(_json_load(bline))

    # Check file format and get tag_names
    tag_names_in_file = set()
    for line in json_lines:
        if not line.get("tag_name"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tag_name missing")
        tag_names_in_file.add(line.get("tag_name"))

    # If force_mode is False, check whether tag_names exist in DB
    if force_mode is False:
        check_tags_exist(db, list(tag_names_in_file))

    # Create data structure for merging
    # dict_of_references: {tag_name: references}
    # references: [{target: target_text, version: [version text], group: [group]}]
    dict_of_references: Dict[str, List[Dict[str, str]]] = dict()
    # dict_of_text: {tag_name: text}
    dict_of_text: Dict[str, str] = dict()
    for line in json_lines:
        tag_name = line.get("tag_name")
        # Save references from each line
        for reference_form_file in line.get("references", [{"target": "", "version": ""}]):
            reference = {
                "target": reference_form_file.get("target", ""),
                "version": reference_form_file.get("version", ""),
                "group": group,
            }

            if tag_name in dict_of_references:
                dict_of_references[tag_name].append(reference)
            else:
                dict_of_references[tag_name] = [reference]
        # Save text from each line
        dict_of_text[tag_name] = line.get("text") or ""

    # First, delete group's references not specified in uploaded file
    for pteamtag in pteam.pteamtags:
        tag_name = pteamtag.tag.tag_name
        if tag_name not in dict_of_references:
            remove_specified_group_references_from_pteamtag(db, pteamtag, group)

    # Second, update/create references specified in upload file
    # Save pteamtag which version has changed
    pteamtags_for_auto_close = []
    for tag_name, references in dict_of_references.items():
        # Get pteamtag which has tag_name
        # pteamtags_with_given_tag_name should be only one pteamtag (or empty)
        pteamtags_with_given_tag_name = [
            pteamtag for pteamtag in pteam.pteamtags if pteamtag.tag.tag_name == tag_name
        ]

        # When there is pteamtag which has tag_name, update references of pteamtag
        if pteamtags_with_given_tag_name:
            for pteamtag in pteamtags_with_given_tag_name:
                # Check version will be changed
                is_version_update = set(
                    [reference["version"] for reference in pteamtag.references]
                ) != set([reference["version"] for reference in references])

                referenes_without_specified_group = [
                    reference for reference in pteamtag.references if reference["group"] != group
                ]
                referenes_without_specified_group.extend(references)
                # Set new references
                pteamtag.references = referenes_without_specified_group

                # Update text
                pteamtag.text = dict_of_text[tag_name]

                if is_version_update:
                    pteamtags_for_auto_close.append(pteamtag)
        # When there is no pteamtag which has tag_name, create new pteamtag
        else:
            pteamtag = models.PTeamTag(
                pteam_id=str(pteam_id),
                tag_id=get_or_create_topic_tag(db, tag_name).tag_id,
                references=references,
                text=dict_of_text[tag_name],
            )
            db.add(pteamtag)
            pteamtags_for_auto_close.append(pteamtag)
    db.commit()
    db.refresh(pteam)

    # Execute batch processing, auto close and update PTeamTopicTagStatus
    auto_close_by_pteamtags(db, pteamtags_for_auto_close)
    fix_current_status_by_pteam(db, pteam)

    return sorted(
        [
            schemas.ExtTagResponse(
                tag_name=pteamtag.tag.tag_name,
                tag_id=pteamtag.tag.tag_id,
                parent_name=pteamtag.tag.parent_name,
                parent_id=pteamtag.tag.parent_id,
                references=pteamtag.references,
                text=pteamtag.text,
            )
            for pteamtag in pteam.pteamtags
        ],
        key=lambda x: x.tag_name,
    )


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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    currents = _make_current_tags_dict(pteam)
    targets: Dict[str, Dict[str, models.PTeamTag]] = {  # {type: {tag: PTeamTag}}
        "addings": {},
        "keeps": {},
        "ver_changed": {},
        "infos": {},
        "inuse": {},
    }

    _merge_pteam_tags(db, pteam, group, currents, targets)

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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND, ignore_disabled=True)
    assert pteam
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    if data.slack_webhook_url:
        validate_slack_webhook_url(data.slack_webhook_url)
        pteam.slack_webhook_url = data.slack_webhook_url

    need_auto_close = (data.disabled is False and pteam.disabled is True) or (
        data.zone_names and set(data.zone_names) - {z.zone_name for z in pteam.zones}
    )

    if data.pteam_name is not None:
        pteam.pteam_name = data.pteam_name
    if data.contact_info is not None:
        pteam.contact_info = data.contact_info
    if data.alert_threat_impact is not None:
        pteam.alert_threat_impact = data.alert_threat_impact
    if data.disabled is not None:
        pteam.disabled = data.disabled

    # Zone updating process
    if data.zone_names is not None:
        pteam.zones = update_zones(
            db,
            current_user.user_id,
            True,
            pteam.zones,
            data.zone_names,
        )

    db.add(pteam)
    db.commit()
    db.refresh(pteam)

    if pteam.disabled:
        db.query(models.PTeamInvitation).filter(
            models.PTeamInvitation.pteam_id == str(pteam_id)
        ).delete()
        db.commit()
    elif need_auto_close:
        auto_close_by_pteamtags(db, pteam.pteamtags)

    fix_current_status_by_pteam(db, pteam)

    return _extend_pteam_tags(pteam)


def _get_pteam_topic_statuses_summary(
    db: Session, pteam: models.PTeam, tag_id: str, on_error: int = status.HTTP_400_BAD_REQUEST
):
    if (
        db.query(models.PTeamTag)
        .filter(
            models.PTeamTag.tag_id == tag_id,
            models.PTeamTag.pteam_id == pteam.pteam_id,
        )
        .first()
        is None
    ):
        raise HTTPException(status_code=on_error, detail="No such pteam tag")

    pteam_zones = db.query(
        models.PTeamZone.zone_name,
    ).filter(
        models.PTeamZone.pteam_id == str(pteam.pteam_id),
    )

    rows = (
        db.query(
            models.Tag,
            models.Topic,
            models.PTeamTopicTagStatus.created_at.label("executed_at"),
            models.PTeamTopicTagStatus.topic_status,
        )
        .filter(
            models.Tag.tag_id == tag_id,
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
        .outerjoin(models.TopicZone)
        .filter(
            or_(
                models.TopicZone.zone_name.is_(None),
                models.TopicZone.zone_name.in_(pteam_zones),
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
        "tag_id": tag_id,
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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    return _get_pteam_topic_statuses_summary(
        db, pteam, str(tag_id), on_error=status.HTTP_404_NOT_FOUND
    )


@router.get("/{pteam_id}/topicstatus", response_model=List[schemas.TopicStatusResponse])
def get_pteam_topic_status_list(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topic status list of the pteam.
    """
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
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
    return set_pteam_topic_status_internal(pteam_id, topic_id, tag_id, data, current_user, db)


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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    topic = validate_topic(db, topic_id, on_error=status.HTTP_404_NOT_FOUND)
    assert topic
    validate_pteamtag(db, pteam_id, tag_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)
    if len(topic.zones) > 0 and not set(topic.zones) & set(pteam.zones):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You do not have related zone"
        )

    current_row = get_current_pteam_topic_tag_status(db, pteam_id, topic_id, tag_id)
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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)
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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    if current_user.user_id != str(user_id):
        check_pteam_auth(
            db,
            pteam_id,
            current_user.user_id,
            models.PTeamAuthIntFlag.ADMIN,
            on_error=status.HTTP_403_FORBIDDEN,
        )

    target_users = [x for x in pteam.members if x.user_id == str(user_id)]
    if len(target_users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such pteam member")
    _guard_last_admin(db, pteam_id, [user_id])

    # remove all extra authorities
    _modify_pteam_auth(db, pteam_id, user_id, 0)

    # remove from members
    pteam.members.remove(target_users[0])
    db.add(pteam)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.get("/{pteam_id}/achievements", response_model=List[schemas.SecBadgeBody])
def get_pteam_achievements(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pteam members' achievements.
    """
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    required_auth = models.PTeamAuthIntFlag.PTEAMBADGE_APPLY
    return (
        db.query(models.SecBadge)
        .filter(
            models.SecBadge.user_id.in_(
                db.query(models.PTeamAccount.user_id).filter(
                    models.PTeamAccount.pteam_id == str(pteam_id)
                )
            ),  # pteam member
            (
                true()
                if check_pteam_auth(
                    db,
                    pteam_id,
                    MEMBER_UUID,
                    required_auth,  # all members are allowed
                )
                else models.SecBadge.user_id.in_(
                    db.query(models.PTeamAuthority.user_id).filter(  # individually allowed users
                        models.PTeamAuthority.pteam_id == str(pteam_id),
                        models.PTeamAuthority.authority.op("&")(required_auth) == required_auth,
                    )
                )
            ),
        )
        .order_by(models.SecBadge.created_at.desc())
        .all()
    )


def _expire_tokens(db: Session):
    db.query(models.PTeamInvitation).filter(
        or_(
            models.PTeamInvitation.expiration < datetime.now(),
            and_(
                models.PTeamInvitation.limit_count.is_not(None),
                models.PTeamInvitation.used_count >= models.PTeamInvitation.limit_count,
            ),
        )
    ).delete()
    db.commit()


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
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    if request.authorities is not None and not check_pteam_auth(
        db, pteam_id, current_user.user_id, models.PTeamAuthIntFlag.ADMIN
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

    _expire_tokens(db)

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
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    _expire_tokens(db)

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
    validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.INVITE,
        on_error=status.HTTP_403_FORBIDDEN,
    )
    _expire_tokens(db)

    db.query(models.PTeamInvitation).filter(
        models.PTeamInvitation.invitation_id == str(invitation_id)
    ).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header


@router.get("/invitation/{invitation_id}", response_model=schemas.PTeamInviterResponse)
def invited_pteam(
    invitation_id: UUID, db: Session = Depends(get_db)
) -> schemas.PTeamInviterResponse:
    invitation = (
        db.query(models.PTeamInvitation)
        .filter(models.PTeamInvitation.invitation_id == str(invitation_id))
        .one_or_none()
    )
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invitation id")

    invitation_detail = {
        "pteam_id": invitation.pteam_id,
        "pteam_name": invitation.pteam.pteam_name,
        "email": invitation.inviter.email,
        "user_id": invitation.user_id,
    }
    return schemas.PTeamInviterResponse(**invitation_detail)


@router.post("/apply_invitation", response_model=schemas.PTeamInfo)
def apply_invitation(
    request: schemas.ApplyInvitationRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply invitation to pteam.
    """
    _expire_tokens(db)

    invitation = (
        db.query(models.PTeamInvitation)
        .filter(
            models.PTeamInvitation.invitation_id == str(request.invitation_id),
            or_(
                models.PTeamInvitation.limit_count.is_(None),
                models.PTeamInvitation.limit_count > models.PTeamInvitation.used_count,
            ),
        )
        .with_for_update()
        .one_or_none()
    )  # lock and block!
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid (or expired) invitation id"
        )
    pteam = db.query(models.PTeam).filter(models.PTeam.pteam_id == invitation.pteam_id).one()
    if current_user in pteam.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined to the pteam"
        )

    pteam_auth = (
        db.query(models.PTeamAuthority)
        .filter(
            models.PTeamAuthority.pteam_id == invitation.pteam_id,
            models.PTeamAuthority.user_id == current_user.user_id,
        )
        .one_or_none()
    )
    if pteam_auth is None:
        pteam_auth = models.PTeamAuthority(
            pteam_id=invitation.pteam_id, user_id=current_user.user_id, authority=0
        )
    pteam_auth.authority |= invitation.authority

    pteam.members.append(current_user)
    invitation.used_count += 1
    db.add(pteam)
    if pteam_auth.authority > 0:
        db.add(pteam_auth)
    db.add(invitation)
    db.commit()
    db.refresh(pteam)

    return pteam


@router.get("/{pteam_id}/watchers", response_model=List[schemas.ATeamEntry])
def get_pteam_watchers(
    pteam_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get watching pteams of the ateam.
    """
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_membership(db, pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN)

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
    pteam = validate_pteam(db, pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert pteam
    check_pteam_auth(
        db,
        pteam_id,
        current_user.user_id,
        models.PTeamAuthIntFlag.ADMIN,
        on_error=status.HTTP_403_FORBIDDEN,
    )

    pteam.ateams = [ateams for ateams in pteam.ateams if ateams.ateam_id != str(ateam_id)]
    db.add(pteam)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
