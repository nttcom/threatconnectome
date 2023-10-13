import json
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union, cast
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.responses import Response
from sqlalchemy import and_, delete, exists, func, literal, literal_column, or_, select, text
from sqlalchemy.dialects.postgresql import insert as psql_insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from app import models, schemas
from app.constants import MEMBER_UUID, NOT_MEMBER_UUID, SYSTEM_UUID


def get_system_account(db: Session) -> models.Account:
    system_account = (
        db.query(models.Account).filter(models.Account.user_id == str(SYSTEM_UUID)).one_or_none()
    )
    if not system_account:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No such system user",
        )
    return system_account


def validate_secbadge(
    db: Session,
    badge_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> Optional[models.SecBadge]:
    secbadge = (
        db.query(models.SecBadge).filter(models.SecBadge.badge_id == str(badge_id)).one_or_none()
    )
    if secbadge is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such secbadge")
    return secbadge


def validate_actionlog(
    db: Session,
    logging_id: Optional[Union[UUID, str]] = None,
    action_id: Optional[Union[UUID, str]] = None,
    topic_id: Optional[Union[UUID, str]] = None,
    user_id: Optional[Union[UUID, str]] = None,
    pteam_id: Optional[Union[UUID, str]] = None,
    email: Optional[str] = None,
    on_error: Optional[int] = None,
) -> Optional[models.ActionLog]:
    row = (
        db.query(models.ActionLog)
        .filter(
            true() if logging_id is None else models.ActionLog.logging_id == str(logging_id),
            true() if action_id is None else models.ActionLog.action_id == str(action_id),
            true() if topic_id is None else models.ActionLog.topic_id == str(topic_id),
            true() if user_id is None else models.ActionLog.user_id == str(user_id),
            true() if pteam_id is None else models.ActionLog.pteam_id == str(pteam_id),
            true() if email is None else models.ActionLog.email == email,
        )
        .one_or_none()
    )
    if row is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such actionlog")
    return row


def check_zone_accessible(
    db: Session,
    user_id: Union[UUID, str],
    zones: Union[List[str], List[models.Zone]],
    on_error: Optional[int] = None,
) -> bool:
    user_id = str(user_id)
    if zones == [] or user_id == str(SYSTEM_UUID):
        return True
    zone_names = [x if isinstance(x, str) else x.zone_name for x in zones]
    zoned_pteams_accessible = db.query(models.PTeamZone.pteam_id).filter(
        models.PTeamZone.zone_name.in_(zone_names),
        or_(
            models.PTeamZone.pteam_id.in_(
                db.query(models.PTeamAccount.pteam_id).filter(
                    models.PTeamAccount.user_id == user_id
                ),
            ),
            models.PTeamZone.pteam_id.in_(
                db.query(models.ATeamPTeam.pteam_id).join(
                    models.ATeamAccount,
                    and_(
                        models.ATeamAccount.user_id == user_id,
                        models.ATeamAccount.ateam_id == models.ATeamPTeam.ateam_id,
                    ),
                ),
            ),
        ),
    )
    gteam_membership = db.query(models.Zone.gteam_id).join(
        models.GTeamAccount,
        and_(
            models.Zone.zone_name.in_(zone_names),
            models.GTeamAccount.user_id == user_id,
            models.GTeamAccount.gteam_id == models.Zone.gteam_id,
        ),
    )
    ret = (
        db.query(literal(True))
        .filter(
            or_(
                zoned_pteams_accessible.exists(),
                gteam_membership.exists(),
            ),
        )
        .scalar()
    ) or False

    if not ret and on_error:
        raise HTTPException(status_code=on_error, detail="You do not have related zone")
    return ret


def validate_zone(
    db: Session,
    user_id: Union[UUID, str],
    zone_name: str,
    on_error: Optional[int] = None,
    auth_mode: str = "apply",  # read | apply | admin
    on_auth_error: Optional[int] = None,
    on_archived: Optional[int] = None,
) -> Optional[models.Zone]:
    user_id = str(user_id)
    row = db.query(models.Zone).filter(models.Zone.zone_name == zone_name).one_or_none()
    # Note:
    #   validate_zone() should be used to check the zone is valid and specified
    #   user has authority to (read|apply|destroy) the zone itself.
    #   To check the user can access to zoned resources, use check_zone_accessible() instead.
    if row is None:
        if on_error is None:
            return None
        raise HTTPException(status_code=on_error, detail="No such zone")
    # FIXME: need update auth check depends on auth_mode
    if not check_gteam_membership(db, row.gteam_id, user_id):
        if on_auth_error:
            raise HTTPException(
                status_code=on_auth_error,
                detail="You do not have related zone",  # FIXME: correct message?
            )
        return None
    if on_archived and row.archived:
        raise HTTPException(
            status_code=on_archived,
            detail="Cannot apply archived zone",
        )

    return row


def update_zones(
    db: Session,
    user_id: Union[UUID, str],
    is_admin: bool,  # admin can remove any zone without auth
    current_zones: List[models.Zone],
    new_zones: List[str],
) -> List[models.Zone]:
    keeps = {  # not in new_zones or user does not have auth to apply
        zone
        for zone in current_zones
        if zone.zone_name in new_zones
        or (not is_admin and not validate_zone(db, user_id, zone.zone_name, auth_mode="apply"))
    }
    addings: Set[models.Zone] = {
        cast(
            models.Zone,
            validate_zone(
                db,
                user_id,
                zone_str,
                on_error=status.HTTP_400_BAD_REQUEST,
                auth_mode="apply",
                on_auth_error=status.HTTP_400_BAD_REQUEST,
                on_archived=status.HTTP_400_BAD_REQUEST,
            ),
        )
        for zone_str in new_zones
        if zone_str not in {x.zone_name for x in current_zones}
    }
    return list(addings | keeps)


def validate_tag(
    db: Session,
    tag_id: Optional[Union[UUID, str]] = None,
    tag_name: Optional[str] = None,
    on_error: Optional[int] = None,
) -> Optional[models.Tag]:
    row = (
        db.query(models.Tag)
        .filter(
            true() if tag_id is None else models.Tag.tag_id == str(tag_id),
            true() if tag_name is None else models.Tag.tag_name == tag_name,
        )
        .one_or_none()
    )
    if row is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such tag")
    return row


def check_tags_exist(db: Session, tag_names: List[str]):
    _existing_tags = (
        db.query(models.Tag.tag_name).filter(models.Tag.tag_name.in_(tag_names)).all()
    )  # [('tag1',), ('tag2',), ('tag3',)]
    existing_tag_names = set(tag_tuple[0] for tag_tuple in _existing_tags)
    not_existing_tag_names = set(tag_names) - existing_tag_names
    if len(not_existing_tag_names) >= 1:
        # TODO: set max length of not_exist_tag_names
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No such tags: {', '.join(sorted(not_existing_tag_names))}",
        )


def check_tag_is_related_to_topic(
    db: Session,
    tag_id: Union[UUID, str],
    topic_id: Union[UUID, str],
):
    row = (
        db.query(models.Tag, models.TopicTag)
        .filter(
            models.Tag.tag_id == str(tag_id),
        )
        .outerjoin(
            models.TopicTag,
            and_(
                models.TopicTag.topic_id == str(topic_id),
                models.TopicTag.tag_id.in_([models.Tag.tag_id, models.Tag.parent_id]),
            ),
        )
        .first()
    )
    if row is None or row.TopicTag is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag mismatch")


def validate_pteamtag(
    db: Session,
    pteam_id: Union[UUID, str],
    tag_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> Optional[models.PTeamTag]:
    pteamtag = (
        db.query(models.PTeamTag)
        .filter(models.PTeamTag.pteam_id == str(pteam_id), models.PTeamTag.tag_id == str(tag_id))
        .one_or_none()
    )
    if pteamtag is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such pteam tag")
    return pteamtag


def validate_pteam(
    db: Session,
    pteam_id: Union[UUID, str],
    on_error: Optional[int] = None,
    ignore_disabled: bool = False,
) -> Optional[models.PTeam]:
    pteam = (
        db.query(models.PTeam)
        .filter(
            models.PTeam.pteam_id == str(pteam_id),
            true() if ignore_disabled else models.PTeam.disabled.is_(False),
        )
        .one_or_none()
    )
    if pteam is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such pteam")
    return pteam


def check_pteam_membership(
    db: Session,
    pteam_id: Union[UUID, str],
    user_id: Union[UUID, str],
    on_error: Optional[int] = None,
    ignore_ateam: bool = False,
) -> bool:
    if str(user_id) == str(SYSTEM_UUID):
        return True
    if (
        not ignore_ateam
        and db.query(models.ATeamAccount)
        .filter(
            models.ATeamAccount.user_id == str(user_id),
            models.ATeamAccount.ateam_id.in_(
                db.query(models.ATeamPTeam.ateam_id).filter(
                    models.ATeamPTeam.pteam_id == str(pteam_id)
                )
            ),
        )
        .first()
        is not None
    ):
        return True
    row = (
        db.query(models.PTeamAccount)
        .filter(
            models.PTeamAccount.pteam_id == str(pteam_id),
            models.PTeamAccount.user_id == str(user_id),
        )
        .one_or_none()
    )
    if row is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="Not a pteam member")
    return row is not None


def check_pteam_auth(
    db: Session,
    pteam_id: Union[UUID, str],
    user_id: Optional[Union[UUID, str]],
    required: models.PTeamAuthIntFlag,
    on_error: Optional[int] = None,
) -> bool:
    if user_id and str(user_id) == str(SYSTEM_UUID):
        return True
    str_user_ids = [str(NOT_MEMBER_UUID)]
    if user_id and (
        str(user_id) == str(MEMBER_UUID)
        or check_pteam_membership(db, pteam_id, user_id, ignore_ateam=True)
    ):
        str_user_ids += [str(user_id), str(MEMBER_UUID)]  # apply only if member

    rows = (
        db.query(models.PTeamAuthority.authority)
        .filter(
            models.PTeamAuthority.pteam_id == str(pteam_id),
            models.PTeamAuthority.user_id.in_(str_user_ids),
        )
        .all()
    )
    auth = 0
    for row in rows:
        auth |= row.authority
    if auth & required == required:  # OK
        return True
    if on_error is None:
        return False
    raise HTTPException(status_code=on_error, detail="You do not have authority")


def validate_ateam(
    db: Session,
    ateam_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> Optional[models.ATeam]:
    ateam = (
        db.query(models.ATeam)
        .filter(
            models.ATeam.ateam_id == str(ateam_id),
        )
        .one_or_none()
    )
    if ateam is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such ateam")
    return ateam


def check_ateam_membership(
    db: Session,
    ateam_id: Union[UUID, str],
    user_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> bool:
    if str(user_id) == str(SYSTEM_UUID):
        return True
    row = (
        db.query(models.ATeamAccount)
        .filter(
            models.ATeamAccount.ateam_id == str(ateam_id),
            models.ATeamAccount.user_id == str(user_id),
        )
        .one_or_none()
    )
    if row is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="Not an ateam member")
    return row is not None


def check_ateam_auth(
    db: Session,
    ateam_id: Union[UUID, str],
    user_id: Optional[Union[UUID, str]],
    required: models.ATeamAuthIntFlag,
    on_error: Optional[int] = None,
) -> bool:
    if user_id and str(user_id) == str(SYSTEM_UUID):
        return True
    str_user_ids = [str(NOT_MEMBER_UUID)]
    if user_id and (
        str(user_id) == str(MEMBER_UUID) or check_ateam_membership(db, ateam_id, user_id)
    ):
        str_user_ids += [str(user_id), str(MEMBER_UUID)]  # apply only if member

    rows = (
        db.query(models.ATeamAuthority.authority)
        .filter(
            models.ATeamAuthority.ateam_id == str(ateam_id),
            models.ATeamAuthority.user_id.in_(str_user_ids),
        )
        .all()
    )
    auth = 0
    for row in rows:
        auth |= row.authority
    if auth & required == required:  # OK
        return True
    if on_error is None:
        return False
    raise HTTPException(status_code=on_error, detail="You do not have authority")


def validate_gteam(
    db: Session,
    gteam_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> Optional[models.GTeam]:
    gteam = (
        db.query(models.GTeam)
        .filter(
            models.GTeam.gteam_id == str(gteam_id),
        )
        .one_or_none()
    )
    if gteam is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such gteam")
    return gteam


def check_gteam_membership(
    db: Session,
    gteam_id: Union[UUID, str],
    user_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> bool:
    if str(user_id) == str(SYSTEM_UUID):
        return True
    row = (
        db.query(models.GTeamAccount)
        .filter(
            models.GTeamAccount.gteam_id == str(gteam_id),
            models.GTeamAccount.user_id == str(user_id),
        )
        .one_or_none()
    )
    if row is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="Not a gteam member")
    return row is not None


def check_gteam_auth(
    db: Session,
    gteam_id: Union[UUID, str],
    user_id: Optional[Union[UUID, str]],
    required: models.GTeamAuthIntFlag,
    on_error: Optional[int] = None,
) -> bool:
    if user_id and str(user_id) == str(SYSTEM_UUID):
        return True
    str_user_ids = [str(NOT_MEMBER_UUID)]
    if user_id and (
        str(user_id) == str(MEMBER_UUID) or check_gteam_membership(db, gteam_id, user_id)
    ):
        str_user_ids += [str(user_id), str(MEMBER_UUID)]  # apply only if member

    rows = (
        db.query(models.GTeamAuthority.authority)
        .filter(
            models.GTeamAuthority.gteam_id == str(gteam_id),
            models.GTeamAuthority.user_id.in_(str_user_ids),
        )
        .all()
    )
    auth = 0
    for row in rows:
        auth |= row.authority
    if auth & required == required:  # OK
        return True
    if on_error is None:
        return False
    raise HTTPException(status_code=on_error, detail="You do not have authority")


def validate_topic(
    db: Session,
    topic_id: Union[UUID, str],
    on_error: Optional[int] = None,
    ignore_disabled: bool = False,
) -> Optional[models.Topic]:
    topic = (
        db.query(models.Topic)
        .filter(
            models.Topic.topic_id == str(topic_id),
            true() if ignore_disabled else models.Topic.disabled.is_(False),
        )
        .one_or_none()
    )
    if topic is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such topic")
    return topic


def search_topics(
    db: Session,
    user_id: Union[UUID, str],
    zones: Optional[List[str]] = None,
    title_words: Optional[List[str]] = None,
    abstract_words: Optional[List[str]] = None,
    threat_impacts: Optional[List[int]] = None,
    misp_tag_ids: Optional[List[UUID]] = None,
    # TODO created_by: Optional[UUID] = None,
    # TODO created_before: Optional[datetime] = None,
    # TODO created_after: Optional[datetime] = None,
    # TODO updated_before: Optional[datetime] = None,
    # TODO updated_after: Optional[datetime] = None,
    tag_ids: Optional[List[UUID]] = None,
) -> List[models.Topic]:
    user_id = str(user_id)
    pteam_zones = db.query(models.PTeamZone.zone_name).filter(
        or_(
            models.PTeamZone.pteam_id.in_(
                db.query(models.PTeamAccount.pteam_id).filter(
                    models.PTeamAccount.user_id == user_id
                ),
            ),
            models.PTeamZone.pteam_id.in_(
                db.query(models.ATeamPTeam.pteam_id).join(
                    models.ATeamAccount,
                    and_(
                        models.ATeamAccount.user_id == user_id,
                        models.ATeamAccount.ateam_id == models.ATeamPTeam.ateam_id,
                    ),
                ),
            ),
        ),
    )
    gteam_zones = db.query(models.Zone.zone_name).join(
        models.GTeamAccount,
        and_(
            models.GTeamAccount.user_id == user_id,
            models.GTeamAccount.gteam_id == models.Zone.gteam_id,
        ),
    )

    return (
        db.query(models.Topic)
        .outerjoin(models.TopicZone)
        .filter(
            or_(
                models.TopicZone.zone_name.is_(None),
                models.TopicZone.zone_name.in_(pteam_zones),
                models.TopicZone.zone_name.in_(gteam_zones),
            ),
        )
        .distinct()
        .filter(
            true()
            if title_words is None
            else models.Topic.title.bool_op("@@")(
                func.to_tsquery("|".join("(" + "&".join(t.split()) + ")" for t in title_words))
            ),
            true()
            if abstract_words is None
            else models.Topic.abstract.bool_op("@@")(
                func.to_tsquery("|".join("(" + "&".join(a.split()) + ")" for a in abstract_words))
            ),
            true() if threat_impacts is None else models.Topic.threat_impact.in_(threat_impacts),
            true()
            if misp_tag_ids is None
            else models.Topic.topic_id.in_(
                db.query(models.TopicMispTag.topic_id).filter(
                    models.TopicMispTag.tag_id.in_(map(str, misp_tag_ids))
                )
            ),
            true()
            if tag_ids is None
            else models.Topic.topic_id.in_(
                db.query(models.TopicTag.topic_id).filter(
                    models.TopicTag.tag_id.in_(map(str, tag_ids))
                )
            ),
            models.Topic.disabled.is_(False),
        )
        .order_by(models.Topic.threat_impact, models.Topic.updated_at.desc())
        .all()
    )


def create_action_internal(
    db: Session,
    current_user: models.Account,
    action: schemas.ActionCreateRequest,
) -> models.TopicAction:
    if action.topic_id:
        topic = validate_topic(
            db,
            action.topic_id,
            on_error=status.HTTP_400_BAD_REQUEST,
            ignore_disabled=True,
        )
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_403_FORBIDDEN)
    check_topic_action_tags_integrity(
        topic.tags,
        action.ext.get("tags"),
        on_error=status.HTTP_400_BAD_REQUEST,
    )
    action_zones = update_zones(db, current_user.user_id, False, [], action.zone_names)

    action_id = str(action.action_id) if action.action_id else None
    del action.zone_names
    del action.action_id
    row = models.TopicAction(
        **action.model_dump(),
        zones=action_zones,
        action_id=action_id,
        created_by=current_user.user_id,
        created_at=datetime.now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return row


def validate_action(
    db: Session,
    action_id: Union[UUID, str],
    on_error: Optional[int] = None,
) -> Optional[models.TopicAction]:
    action = (
        db.query(models.TopicAction)
        .filter(models.TopicAction.action_id == str(action_id))
        .one_or_none()
    )
    if action is None and on_error is not None:
        raise HTTPException(status_code=on_error, detail="No such topic action")
    return action


def check_topic_action_tags_integrity(
    topic_tags: Union[Sequence[str], Sequence[models.Tag]],  # tag_name list or topic.tags
    action_tags: Optional[List[str]],  # action.ext.get("tags")
    on_error: Optional[int] = None,
) -> bool:
    if not action_tags:
        return True

    topic_tag_strs = {x if isinstance(x, str) else x.tag_name for x in topic_tags}
    for action_tag in action_tags:
        if action_tag not in topic_tag_strs and _pick_parent_tag(action_tag) not in topic_tag_strs:
            if on_error is None:
                return False
            raise HTTPException(
                status_code=on_error,
                detail="Action Tag mismatch with Topic Tag",
            )
    return True


def get_misp_tag(db: Session, tag_name: str):
    row = db.query(models.MispTag).filter(models.MispTag.tag_name == tag_name).one_or_none()
    if row is None:
        row = models.MispTag(tag_name=tag_name)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _pick_parent_tag(tag_name: str) -> Optional[str]:
    if len(tag_name.split(":", 2)) == 3:  # supported format
        return tag_name.rsplit(":", 1)[0] + ":"  # trim the right most field
    return None


def get_or_create_topic_tag(db: Session, tag_name: str) -> models.Tag:
    row = db.query(models.Tag).filter(models.Tag.tag_name == tag_name).one_or_none()
    if row is not None:
        return row

    row = models.Tag(tag_name=tag_name, parent_id=None, parent_name=None)
    db.add(row)
    db.commit()
    db.refresh(row)

    if parent_name := _pick_parent_tag(tag_name):
        parent_id = (
            row.tag_id
            if parent_name == tag_name
            else get_or_create_topic_tag(db, parent_name).tag_id
        )

        row.parent_name = parent_name
        row.parent_id = parent_id
        db.add(row)
        db.commit()
        db.refresh(row)

    return row


def fix_current_status_by_pteam(db: Session, pteam: models.PTeam):
    if pteam.disabled:
        db.query(models.CurrentPTeamTopicTagStatus).filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id
        ).delete()
        db.commit()
        return

    pteam_zones = db.query(models.PTeamZone.zone_name).filter(
        models.PTeamZone.pteam_id == pteam.pteam_id,
    )

    # remove untagged
    db.execute(
        delete(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
            models.CurrentPTeamTopicTagStatus.tag_id.not_in(
                db.query(models.PTeamTag.tag_id).filter(models.PTeamTag.pteam_id == pteam.pteam_id)
            ),
        )
    )

    # remove hidden topics
    zoned_topics = (
        db.query(
            models.TopicZone.zone_name,
            models.CurrentPTeamTopicTagStatus.topic_id,
        )
        .join(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
                models.CurrentPTeamTopicTagStatus.topic_id == models.TopicZone.topic_id,
            ),
        )
        .distinct()
        .subquery()
    )
    hidden_topics = (
        db.query(zoned_topics.c.topic_id)  # public topics are already excluded
        .filter(
            ~exists().where(zoned_topics.c.zone_name.in_(pteam_zones)),  # not having matched zone
        )
        .distinct()
    )
    db.execute(
        delete(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
            models.CurrentPTeamTopicTagStatus.topic_id.in_(hidden_topics),
        )
    )

    # insert missings or updated with latest
    tagged_topics = (
        db.query(models.TopicTag.topic_id, models.Tag.tag_id)  # tag_id is pteam tag (not topic tag)
        .join(
            models.Tag,
            and_(
                models.Tag.tag_id.in_(
                    db.query(models.PTeamTag.tag_id).filter(
                        models.PTeamTag.pteam_id == pteam.pteam_id
                    )
                ),
                or_(
                    models.TopicTag.tag_id == models.Tag.tag_id,
                    models.TopicTag.tag_id == models.Tag.parent_id,
                ),
            ),
        )
        .join(
            models.Topic,
            and_(
                models.Topic.topic_id == models.TopicTag.topic_id,
                models.Topic.disabled.is_(False),
            ),
        )
        .outerjoin(
            models.TopicZone,
            models.TopicZone.topic_id == models.TopicTag.topic_id,
        )
        .filter(
            or_(
                models.TopicZone.zone_name.is_(None),
                models.TopicZone.zone_name.in_(pteam_zones),
            ),
        )
        .distinct()
        .subquery()
    )
    latests = (
        db.query(
            models.PTeamTopicTagStatus.pteam_id,
            models.PTeamTopicTagStatus.topic_id,
            models.PTeamTopicTagStatus.tag_id,
            func.max(models.PTeamTopicTagStatus.created_at).label("latest"),
        )
        .filter(
            models.PTeamTopicTagStatus.pteam_id == pteam.pteam_id,
        )
        .group_by(
            models.PTeamTopicTagStatus.pteam_id,
            models.PTeamTopicTagStatus.topic_id,
            models.PTeamTopicTagStatus.tag_id,
        )
        .subquery()
    )
    new_currents = (
        db.query(
            literal_column(f"'{pteam.pteam_id}'").label("pteam_id"),
            tagged_topics.c.topic_id,
            tagged_topics.c.tag_id,
            models.PTeamTopicTagStatus.status_id,
            func.coalesce(models.PTeamTopicTagStatus.topic_status, models.TopicStatusType.alerted),
            models.Topic.threat_impact,
            models.Topic.updated_at,
        )
        .join(
            models.Topic,
            models.Topic.topic_id == tagged_topics.c.topic_id,
        )
        .outerjoin(
            latests,
            and_(
                latests.c.pteam_id == pteam.pteam_id,
                latests.c.topic_id == tagged_topics.c.topic_id,
                latests.c.tag_id == tagged_topics.c.tag_id,
            ),
        )
        .outerjoin(
            models.PTeamTopicTagStatus,
            and_(
                models.PTeamTopicTagStatus.pteam_id == pteam.pteam_id,
                models.PTeamTopicTagStatus.topic_id == latests.c.topic_id,
                models.PTeamTopicTagStatus.tag_id == latests.c.tag_id,
                models.PTeamTopicTagStatus.created_at == latests.c.latest,  # use as uniq key
            ),
        )
    )
    insert_stmt = psql_insert(models.CurrentPTeamTopicTagStatus).from_select(
        [
            "pteam_id",
            "topic_id",
            "tag_id",
            "status_id",
            "topic_status",
            "threat_impact",
            "updated_at",
        ],
        new_currents,
    )
    db.execute(
        insert_stmt.on_conflict_do_update(
            index_elements=["pteam_id", "topic_id", "tag_id"],
            set_={
                "status_id": insert_stmt.excluded.status_id,
                "threat_impact": insert_stmt.excluded.threat_impact,
                "updated_at": insert_stmt.excluded.updated_at,
            },
        )
    )

    db.commit()


def fix_current_status_by_deleted_topic(db: Session, topic_id: Union[UUID, str]):
    db.query(models.CurrentPTeamTopicTagStatus).filter(
        models.CurrentPTeamTopicTagStatus.topic_id == str(topic_id)
    ).delete()
    db.commit()


def fix_current_status_by_topic(db: Session, topic: models.Topic):
    if topic.disabled:
        db.query(models.CurrentPTeamTopicTagStatus).filter(
            models.CurrentPTeamTopicTagStatus.topic_id == topic.topic_id
        ).delete()
        db.commit()
        return

    # remove untagged
    current_related_tags = (
        db.query(models.Tag.tag_id)
        .join(
            models.TopicTag,
            and_(
                models.TopicTag.topic_id == topic.topic_id,
                or_(
                    models.TopicTag.tag_id == models.Tag.tag_id,
                    models.TopicTag.tag_id == models.Tag.parent_id,
                ),
            ),
        )
        .distinct()
    )
    db.execute(
        delete(models.CurrentPTeamTopicTagStatus).where(
            models.CurrentPTeamTopicTagStatus.topic_id == topic.topic_id,
            models.CurrentPTeamTopicTagStatus.tag_id.not_in(current_related_tags),
        )
    )

    if topic.zones:  # not a public topic
        # remove from kicked out pteams
        allowed_pteams = (
            db.query(
                models.PTeamZone.pteam_id,
            )
            .join(
                models.TopicZone,
                and_(
                    models.TopicZone.topic_id == topic.topic_id,
                    models.TopicZone.zone_name == models.PTeamZone.zone_name,
                ),
            )
            .distinct()
        )
        db.execute(
            delete(models.CurrentPTeamTopicTagStatus).where(
                models.CurrentPTeamTopicTagStatus.topic_id == topic.topic_id,
                models.CurrentPTeamTopicTagStatus.pteam_id.not_in(allowed_pteams),
            )
        )

    # fill missings or update -- at least updated_at is modified
    _pteam_tags = (
        db.query(
            models.Tag.tag_id,
            models.PTeamTag.pteam_id,
        )
        .join(
            models.TopicTag,
            and_(
                models.TopicTag.topic_id == topic.topic_id,
                or_(
                    models.TopicTag.tag_id == models.Tag.tag_id,
                    models.TopicTag.tag_id == models.Tag.parent_id,
                ),
            ),
        )
        .join(
            models.PTeamTag,
            models.PTeamTag.tag_id == models.Tag.tag_id,
        )
        .join(
            models.PTeam,
            and_(
                models.PTeam.pteam_id == models.PTeamTag.pteam_id,
                models.PTeam.disabled.is_(False),
            ),
        )
    )
    pteam_tags = (  # filter by zone only if not a public topic
        (
            _pteam_tags.join(
                models.TopicZone,
                models.TopicZone.topic_id == models.TopicTag.topic_id,
            ).join(
                models.PTeamZone,
                and_(
                    models.PTeamZone.pteam_id == models.PTeamTag.pteam_id,
                    models.PTeamZone.zone_name == models.TopicZone.zone_name,
                ),
            )
            if topic.zones
            else _pteam_tags
        )
        .distinct()
        .subquery()
    )
    latests = (
        db.query(
            models.PTeamTopicTagStatus.pteam_id,
            models.PTeamTopicTagStatus.topic_id,
            models.PTeamTopicTagStatus.tag_id,
            func.max(models.PTeamTopicTagStatus.created_at).label("latest"),
        )
        .filter(
            models.PTeamTopicTagStatus.topic_id == topic.topic_id,
        )
        .group_by(
            models.PTeamTopicTagStatus.pteam_id,
            models.PTeamTopicTagStatus.topic_id,
            models.PTeamTopicTagStatus.tag_id,
        )
        .subquery()
    )
    new_currents = (
        db.query(
            pteam_tags.c.pteam_id,
            literal_column(f"'{topic.topic_id}'"),
            pteam_tags.c.tag_id,
            models.PTeamTopicTagStatus.status_id,
            func.coalesce(models.PTeamTopicTagStatus.topic_status, models.TopicStatusType.alerted),
            literal_column(f"'{topic.threat_impact}'"),
            literal_column(f"'{topic.updated_at}'"),
        )
        .outerjoin(
            latests,
            and_(
                latests.c.pteam_id == pteam_tags.c.pteam_id,
                latests.c.topic_id == topic.topic_id,
                latests.c.tag_id == pteam_tags.c.tag_id,
            ),
        )
        .outerjoin(
            models.PTeamTopicTagStatus,
            and_(
                models.PTeamTopicTagStatus.pteam_id == latests.c.pteam_id,
                models.PTeamTopicTagStatus.topic_id == topic.topic_id,
                models.PTeamTopicTagStatus.tag_id == latests.c.tag_id,
                models.PTeamTopicTagStatus.created_at == latests.c.latest,
            ),
        )
    )
    insert_stmt = psql_insert(models.CurrentPTeamTopicTagStatus).from_select(
        [
            "pteam_id",
            "topic_id",
            "tag_id",
            "status_id",
            "topic_status",
            "threat_impact",
            "updated_at",
        ],
        new_currents,
    )
    db.execute(
        insert_stmt.on_conflict_do_update(
            index_elements=["pteam_id", "topic_id", "tag_id"],
            set_={
                "status_id": insert_stmt.excluded.status_id,
                "threat_impact": insert_stmt.excluded.threat_impact,
                "updated_at": insert_stmt.excluded.updated_at,
            },
        )
    )

    db.commit()


def get_pteamtags_summary(db: Session, pteam: models.PTeam) -> dict:
    _counts = (
        db.query(
            models.CurrentPTeamTopicTagStatus.tag_id,
            models.CurrentPTeamTopicTagStatus.topic_status,
            func.count(models.CurrentPTeamTopicTagStatus.topic_status).label("status_count"),
        )
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
        )
        .group_by(
            models.CurrentPTeamTopicTagStatus.tag_id,
            models.CurrentPTeamTopicTagStatus.topic_status,
        )
        .all()
    )
    counts_map: Dict[str, int] = {}
    for item in _counts:
        str_status = (item.topic_status or models.TopicStatusType.alerted).value
        counts_map[item.tag_id + str_status] = item.status_count

    subq_topic = (
        db.query(
            models.CurrentPTeamTopicTagStatus.tag_id,  # tag_id is pteamtag, not topictag
            func.coalesce(
                func.min(models.CurrentPTeamTopicTagStatus.threat_impact),
                text("4"),
            ).label("threat_impact"),
            func.max(models.CurrentPTeamTopicTagStatus.updated_at).label("updated_at"),
        )
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == pteam.pteam_id,
            models.CurrentPTeamTopicTagStatus.topic_status != models.TopicStatusType.completed,
        )
        .group_by(models.CurrentPTeamTopicTagStatus.tag_id)
        .subquery()
    )
    rows = (
        db.query(
            models.PTeamTag.tag_id,
            models.PTeamTag.references,
            models.PTeamTag.text,
            models.Tag.tag_name,
            models.Tag.parent_name,
            models.Tag.parent_id,
            subq_topic.c.threat_impact,
            subq_topic.c.updated_at,
        )
        .join(
            models.Tag,
            and_(
                models.PTeamTag.pteam_id == pteam.pteam_id,
                models.Tag.tag_id == models.PTeamTag.tag_id,
            ),
        )
        .outerjoin(
            subq_topic,
            subq_topic.c.tag_id == models.PTeamTag.tag_id,
        )
        .order_by(
            subq_topic.c.threat_impact,
            subq_topic.c.updated_at.desc(),
            models.Tag.tag_name,
        )
        .all()
    )

    _status_count_keys = {
        models.TopicStatusType.alerted.value,
        models.TopicStatusType.acknowledged.value,
        models.TopicStatusType.scheduled.value,
        models.TopicStatusType.completed.value,
    }
    threat_impact_count = {"1": 0, "2": 0, "3": 0, "4": 0}
    tags = []
    for row in rows:
        tag = {
            "tag_name": row.tag_name,
            "tag_id": row.tag_id,
            "parent_name": row.parent_name,
            "parent_id": row.parent_id,
            "references": row.references or [],
            "text": row.text or "",
            "threat_impact": row.threat_impact,
            "updated_at": row.updated_at if row.updated_at else None,
            "status_count": {
                key: counts_map.get(row.tag_id + key, 0) for key in _status_count_keys
            },
        }
        threat_impact_count[str(row.threat_impact or 4)] += 1
        tags.append(tag)
    summary = {
        "threat_impact_count": threat_impact_count,
        "tags": tags,
    }

    return summary


def get_authorized_zones(
    db: Session, user: models.Account
) -> Tuple[Sequence[models.Zone], Sequence[models.Zone], Sequence[models.Zone]]:  # admin,apply,read
    # FIXME:
    #   this is temporal implementation.
    #
    select_stmt = select(models.Zone).join(
        models.GTeamAccount,
        and_(
            models.GTeamAccount.user_id == user.user_id,
            models.GTeamAccount.gteam_id == models.Zone.gteam_id,
        ),
    )
    rows = db.scalars(select_stmt).all()
    return rows, rows, rows


def calculate_topic_content_fingerprint(
    title: str,
    abstract: str,
    threat_impact: int,
    tag_names: List[str],
) -> str:
    data = {
        "title": title,
        "abstract": abstract,
        "threat_impact": threat_impact,
        "tag_names": sorted(set(tag_names)),
    }
    return md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def get_pteam_topic_status_history(
    db: Session,
    status_id: Optional[Union[UUID, str]] = None,
    pteam_id: Optional[Union[UUID, str]] = None,
    topic_id: Optional[Union[UUID, str]] = None,
    tag_id: Optional[Union[UUID, str]] = None,
    topic_status: Optional[models.TopicStatusType] = None,
):
    rows = (
        db.query(models.PTeamTopicTagStatus, models.ActionLog)
        .filter(
            true() if status_id is None else models.PTeamTopicTagStatus.status_id == str(status_id),
            true() if pteam_id is None else models.PTeamTopicTagStatus.pteam_id == str(pteam_id),
            true() if topic_id is None else models.PTeamTopicTagStatus.topic_id == str(topic_id),
            true() if tag_id is None else models.PTeamTopicTagStatus.tag_id == str(tag_id),
            true()
            if topic_status is None
            else models.PTeamTopicTagStatus.topic_status == topic_status,
        )
        .outerjoin(
            models.ActionLog,
            func.array_position(
                models.PTeamTopicTagStatus.logging_ids, models.ActionLog.logging_id
            ).is_not(None),
        )
        .all()
    )

    ret_dict: Dict[str, schemas.TopicStatusResponse] = {}
    for topictagstatus, actionlog in rows:
        ret = ret_dict.get(
            topictagstatus.status_id,
            schemas.TopicStatusResponse(**topictagstatus.__dict__, action_logs=[]),
        )
        if actionlog is not None:
            ret.action_logs.append(schemas.ActionLogResponse(**actionlog.__dict__))
        ret_dict[topictagstatus.status_id] = ret
    for val in ret_dict.values():
        val.action_logs.sort(key=lambda x: x.executed_at, reverse=True)

    return sorted(ret_dict.values(), key=lambda x: x.created_at, reverse=True)


def get_metadata_internal(logging_id: Union[UUID, str], current_user: models.Account, db: Session):
    actionlog = validate_actionlog(db, logging_id=logging_id, on_error=status.HTTP_404_NOT_FOUND)
    assert actionlog
    if current_user.user_id != str(SYSTEM_UUID):
        check_pteam_membership(
            db, actionlog.pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN
        )
    if not actionlog.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The recipient account no longer exists"
        )
    accept_action_types = ["elimination", "mitigation"]
    if actionlog.action_type not in accept_action_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Secbadge can only be issued with actionlog"
            " that have action_type of elimination or mitigation.",
        )

    topic = (
        db.query(models.Topic)
        .filter(models.Topic.topic_id == actionlog.topic_id, models.Topic.disabled.is_(False))
        .one_or_none()
    )
    if not topic:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled topic")

    if current_user.user_id == str(SYSTEM_UUID):
        certifier_type = models.CertifierType.system
    elif actionlog.user_id == current_user.user_id:
        certifier_type = models.CertifierType.myself
    else:
        certifier_type = models.CertifierType.coworker

    metadata: Dict[str, Any] = {
        "description": f"{topic.title} has been solved by doing {actionlog.action}",
        "external_url": "https://www.metemcyber.ntt.com/",
        "image": "",
        "name": f"{topic.title} has been solved!",
        "logging_id": str(logging_id),
    }
    result = {
        "recipient": actionlog.user_id,
        "metadata": metadata,
        "priority": 100,
        "difficulty": models.Difficulty.low,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": certifier_type,
        "pteam_id": actionlog.pteam_id,
    }
    return result


def validate_secbadge_metadata_internal(metadata: Dict[str, Any], db: Session):
    def _raise_400(keyname: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metadata: parameter '{keyname}' is wrong or missing",
        )

    required_keys = ["name"]
    for key in required_keys:
        if len(metadata.get(key, "")) == 0:
            _raise_400(key)

    logging_id = metadata.get("logging_id")
    if logging_id:
        actionlog = (
            db.query(models.ActionLog)
            .filter(models.ActionLog.logging_id == logging_id)
            .one_or_none()
        )
        if not actionlog or actionlog.logging_id != logging_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Logging_id is wrong"
            )

    status_id = metadata.get("status_id")
    if status_id:
        topic_status = (
            db.query(models.PTeamTopicTagStatus)
            .filter(models.PTeamTopicTagStatus.status_id == status_id)
            .one_or_none()
        )
        if not topic_status or topic_status.status_id != status_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="PTeam topic status id is wrong"
            )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_topic_status_metadata(
    pteam_id: Union[UUID, str], topic_id: Union[UUID, str], tag_id: Union[UUID, str], db: Session
) -> schemas.BadgeRequest:
    """
    Get metadata from the specified topic_status to create secbadge.
    Secbadge can only be issued with topic status that is scheduled or completed.
    """
    current_topic_status = get_current_pteam_topic_tag_status(db, pteam_id, topic_id, tag_id)
    assert current_topic_status

    topic = (
        db.query(models.Topic)
        .filter(models.Topic.topic_id == topic_id, models.Topic.disabled.is_(False))
        .one_or_none()
    )
    if not topic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a valid topic")

    metadata: Dict[str, Any] = {
        "description": f"The reason of {topic.title} has been found!",
        "external_url": "https://www.metemcyber.ntt.com/",
        "image": "",
        "name": f"The reason of {topic.title} has been found!",
        "status_id": current_topic_status.status_id,
    }
    result = schemas.BadgeRequest(
        recipient=UUID(current_topic_status.user_id),
        metadata=metadata,
        priority=100,
        difficulty=models.Difficulty.low,
        badge_type=[models.BadgeType.performance],
        certifier_type=models.CertifierType.system,
        pteam_id=UUID(current_topic_status.pteam_id),
    )
    return result


def create_secbadge_from_topic_status(
    pteam_id: Union[UUID, str],
    topic_id: Union[UUID, str],
    tag_id: Union[UUID, str],
    current_user: models.Account,
    db: Session,
):
    data = _get_topic_status_metadata(pteam_id, topic_id, tag_id, db)
    create_secbadge_internal(data, current_user, db)


def create_secbadge_internal(
    data: schemas.BadgeRequest,
    current_user: models.Account,
    db: Session,
) -> models.SecBadge:
    account = (
        db.query(models.Account).filter(models.Account.user_id == str(data.recipient)).one_or_none()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipient userID"
        )
    if data.priority and (data.priority > 65535 or data.priority < 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority must be in the range of 0 to 65535.",
        )
    validate_secbadge_metadata_internal(data.metadata, db)
    validate_pteam(db, data.pteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_pteam_membership(db, data.pteam_id, data.recipient, on_error=status.HTTP_400_BAD_REQUEST)

    if current_user.user_id != str(SYSTEM_UUID):
        check_pteam_membership(
            db, data.pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN
        )

    attributes = data.metadata.get("attributes", [])
    obtained_at = [attr for attr in attributes if attr.get("trait_type") == "obtained"]
    expired_at = [attr for attr in attributes if attr.get("trait_type") == "expired"]
    now_timestamp = datetime.now()
    badge = models.SecBadge(
        badge_name=data.metadata["name"],
        image_url=data.metadata.get("image", ""),
        user_id=data.recipient,
        email=account.email or "",
        created_by=current_user.user_id,
        obtained_at=datetime.fromtimestamp(obtained_at[0]["value"])
        if obtained_at
        else now_timestamp,
        created_at=now_timestamp,
        expired_at=datetime.fromtimestamp(expired_at[0]["value"]) if expired_at else None,
        metadata_json=json.dumps(data.metadata, sort_keys=True, indent=2),
        priority=data.priority,
        difficulty=data.difficulty,
        badge_type=list(set(data.badge_type)),
        certifier_type=data.certifier_type,
        pteam_id=data.pteam_id,
    )

    db.add(badge)
    db.commit()
    db.refresh(badge)

    return badge


def _get_metadata_for_completeing_topic_within_1h(
    status_id: Union[UUID, str], db: Session
) -> schemas.BadgeRequest:
    topic_status = (
        db.query(models.PTeamTopicTagStatus)
        .filter(models.PTeamTopicTagStatus.status_id == str(status_id))
        .one_or_none()
    )
    if not topic_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status id")

    topic = (
        db.query(models.Topic)
        .filter(
            models.Topic.topic_id == topic_status.topic_id,
            models.Topic.disabled.is_(False),
        )
        .one_or_none()
    )
    if not topic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a valid topic")

    metadata: Dict[str, Any] = {
        "description": f"{topic.title} has been completed within 1h!",
        "external_url": "https://www.metemcyber.ntt.com/",
        "image": "",
        "name": f"{topic.title} has been completed within 1h!",
        "status_id": topic_status.status_id,
    }
    result = schemas.BadgeRequest(
        recipient=UUID(topic_status.user_id),
        metadata=metadata,
        priority=100,
        difficulty=models.Difficulty.low,
        badge_type=[models.BadgeType.performance],
        certifier_type=models.CertifierType.system,
        pteam_id=UUID(topic_status.pteam_id),
    )
    return result


def create_secbadge_from_actionlog_internal(
    logging_id: Union[UUID, str], current_user: models.Account, db: Session
):
    data = get_metadata_internal(logging_id, current_user, db)
    return create_secbadge_internal(schemas.BadgeRequest(**data), current_user, db)


def create_actionlog_internal(
    data: schemas.ActionLogRequest,
    current_user: models.Account,
    db: Session,
):
    pteam = validate_pteam(db, data.pteam_id, on_error=status.HTTP_400_BAD_REQUEST)
    assert pteam
    check_pteam_membership(
        db, data.pteam_id, current_user.user_id, on_error=status.HTTP_403_FORBIDDEN
    )
    user = (
        db.query(models.Account).filter(models.Account.user_id == str(data.user_id)).one_or_none()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    check_pteam_membership(db, data.pteam_id, data.user_id, on_error=status.HTTP_400_BAD_REQUEST)
    topic = validate_topic(db, data.topic_id, on_error=status.HTTP_400_BAD_REQUEST)
    assert topic
    check_zone_accessible(db, current_user.user_id, topic.zones, on_error=status.HTTP_404_NOT_FOUND)

    if (
        db.query(
            models.TopicTag,
        )
        .filter(
            models.TopicTag.topic_id == str(data.topic_id),
        )
        .outerjoin(
            models.Tag,
            or_(
                models.Tag.tag_id == models.TopicTag.tag_id,
                models.Tag.parent_id == models.TopicTag.tag_id,
            ),
        )
        .join(
            models.PTeamTag,
            and_(
                models.PTeamTag.pteam_id == str(data.pteam_id),
                models.PTeamTag.tag_id == models.Tag.tag_id,
            ),
        )
        .all()
        == []
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a pteam topic")
    topic_action = (
        db.query(models.TopicAction)
        .filter(
            models.TopicAction.topic_id == str(data.topic_id),
            models.TopicAction.action_id == str(data.action_id),
        )
        .one_or_none()
    )
    if not topic_action:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action id")
    if len(topic_action.zones) > 0 and not set(topic_action.zones) & set(pteam.zones):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Zone mismatch between action and pteam"
        )

    result = data.model_dump()
    result["action"] = topic_action.action
    result["action_type"] = topic_action.action_type
    result["recommended"] = topic_action.recommended
    result["pteam_id"] = data.pteam_id
    result["email"] = user.email or ""
    now = datetime.now()
    result["executed_at"] = data.executed_at or now
    result["created_at"] = now
    log = models.ActionLog(**result)
    db.add(log)
    db.commit()
    db.refresh(log)

    if topic_action.action_type == "elimination":
        create_secbadge_from_actionlog_internal(log.logging_id, get_system_account(db), db)

    return log


def pteam_topic_tag_status_to_response(
    db: Session,
    status_row: models.PTeamTopicTagStatus,
) -> schemas.TopicStatusResponse:
    actionlogs = (
        db.query(models.ActionLog)
        .filter(
            func.array_position(status_row.logging_ids, models.ActionLog.logging_id).is_not(None)
        )
        .order_by(models.ActionLog.executed_at.desc())
        .all()
    )
    return schemas.TopicStatusResponse(
        status_id=UUID(status_row.status_id),
        topic_id=UUID(status_row.topic_id),
        pteam_id=UUID(status_row.pteam_id),
        tag_id=UUID(status_row.tag_id),
        user_id=UUID(status_row.user_id),
        topic_status=status_row.topic_status,
        created_at=status_row.created_at,
        assignees=list(map(UUID, status_row.assignees)),
        note=status_row.note,
        scheduled_at=status_row.scheduled_at,
        action_logs=[schemas.ActionLogResponse(**log.__dict__) for log in actionlogs],
    )


def get_current_pteam_topic_tag_status(
    db: Session,
    pteam_id: Union[UUID, str],
    topic_id: Union[UUID, str],
    tag_id: Union[UUID, str],
) -> Optional[models.PTeamTopicTagStatus]:
    return (
        db.query(models.PTeamTopicTagStatus)
        .join(
            models.CurrentPTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam_id),
                models.CurrentPTeamTopicTagStatus.topic_id == str(topic_id),
                models.CurrentPTeamTopicTagStatus.tag_id == str(tag_id),
                models.CurrentPTeamTopicTagStatus.status_id == models.PTeamTopicTagStatus.status_id,
            ),
        )
        .one_or_none()
    )


def set_pteam_topic_status_internal(
    pteam_id: Union[UUID, str],
    topic_id: Union[UUID, str],
    tag_id: Union[UUID, str],
    data: schemas.TopicStatusRequest,
    current_user: models.Account,
    db: Session,
) -> schemas.TopicStatusResponse:
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
    if data.topic_status not in {
        models.TopicStatusType.acknowledged,
        models.TopicStatusType.scheduled,
        models.TopicStatusType.completed,
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong topic status")
    check_tag_is_related_to_topic(db, tag_id, topic_id)
    for logging_id_ in data.logging_ids:
        validate_actionlog(
            db,
            logging_id=logging_id_,
            pteam_id=pteam_id,
            topic_id=topic_id,
            on_error=status.HTTP_400_BAD_REQUEST,
        )
    for assignee in data.assignees:
        check_pteam_membership(db, pteam_id, assignee, on_error=status.HTTP_400_BAD_REQUEST)

    current_status = get_current_pteam_topic_tag_status(db, pteam_id, topic_id, tag_id)
    new_status = models.PTeamTopicTagStatus(
        pteam_id=str(pteam_id),
        topic_id=str(topic_id),
        tag_id=str(tag_id),
        topic_status=data.topic_status,
        user_id=current_user.user_id,
        note=data.note,
        logging_ids=list(set(data.logging_ids)),
        assignees=(
            [current_user.user_id]
            if (
                current_status is None
                and data.assignees == []
                and data.topic_status == models.TopicStatusType.acknowledged
            )
            else list(set(data.assignees))
        ),
        scheduled_at=data.scheduled_at,
        created_at=datetime.now(),
    )
    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    row = db.query(models.CurrentPTeamTopicTagStatus).filter(
        models.CurrentPTeamTopicTagStatus.pteam_id == new_status.pteam_id,
        models.CurrentPTeamTopicTagStatus.topic_id == new_status.topic_id,
        models.CurrentPTeamTopicTagStatus.tag_id == new_status.tag_id,
    ).one_or_none() or models.CurrentPTeamTopicTagStatus(  # be None at auto-closing
        pteam_id=str(pteam_id),
        topic_id=str(topic_id),
        tag_id=str(tag_id),
        status_id=None,
        threat_impact=None,  # not fixed at this time,
        updated_at=None,  # and should be fixed by calling fix_current_status_by_...
    )
    row.status_id = new_status.status_id
    row.topic_status = new_status.topic_status
    db.add(row)
    db.commit()

    # issue badge for change topic_status to scheduled or completed
    if new_status.topic_status in {"scheduled", "completed"}:
        create_secbadge_from_topic_status(
            new_status.pteam_id, new_status.topic_id, new_status.tag_id, get_system_account(db), db
        )

    # issue badge for solving topic within 1h
    if new_status.topic_status == models.TopicStatusType.completed:
        acknowledged_status = get_pteam_topic_status_history(
            db,
            pteam_id=str(pteam_id),
            topic_id=str(topic_id),
            tag_id=str(tag_id),
            topic_status=models.TopicStatusType.acknowledged,
        )
        if (
            acknowledged_status
            and (new_status.created_at - acknowledged_status[0].created_at).total_seconds() <= 3600
        ):
            create_secbadge_internal(
                _get_metadata_for_completeing_topic_within_1h(new_status.status_id, db),
                get_system_account(db),
                db,
            )

    return pteam_topic_tag_status_to_response(db, new_status)


def _pick_actions_related_to_pteamtag_from_topic(
    db: Session,
    pteamtag: models.PTeamTag,
    topic: models.Topic,
) -> Sequence[models.TopicAction]:
    _pteam_zone_names_stmt = select(models.PTeamZone.zone_name).where(
        models.PTeamZone.pteam_id == pteamtag.pteam_id
    )
    _is_accessible_stmt = or_(  # filter by zones
        ~exists().where(models.ActionZone.action_id == models.TopicAction.action_id),  # public
        exists().where(  # zone matched
            models.ActionZone.action_id == models.TopicAction.action_id,
            models.ActionZone.zone_name.in_(_pteam_zone_names_stmt),
        ),
    )
    _tag_matched_stmt = or_(
        func.json_array_length(  # len(ext["vulnerable_versions"][tag_name])
            models.TopicAction.ext.op("->")("vulnerable_versions").op("->")(pteamtag.tag.tag_name)
        )
        > 0,
        and_(
            pteamtag.tag.tag_name != pteamtag.tag.parent_name,  # this line is processed on python
            func.json_array_length(
                models.TopicAction.ext.op("->")("vulnerable_versions").op("->")(
                    pteamtag.tag.parent_name
                )
            )
            > 0,
        ),
    )
    # Note:
    #   We should find INVALID or EMPTY vulnerables to abort auto-close, but could not. :(
    #   SQL will skip the row caused error, e.g. KeyError on JSON. thus,
    #   "WHERE NOT json_array_length(...) > 0" does not make sense.
    #
    #   Therefore, we check having at least 1 valid and accessible action, and abort if not.

    select_actions_stmt = select(models.TopicAction).where(
        models.TopicAction.topic_id == topic.topic_id,
        _is_accessible_stmt,
        _tag_matched_stmt,  # having vulnerable_version, but empty or invalid might be included
    )

    actions = db.scalars(select_actions_stmt).all()
    return actions


@dataclass(frozen=True, kw_only=True)  # frozen makes me hashable
class VulnerableVersion:
    ge: str = ""
    gt: str = ""
    le: str = ""
    lt: str = ""
    eq: str = ""

    def __post_init__(self):
        if (
            not any([self.eq, self.ge, self.gt, self.le, self.lt])
            or (self.ge and self.gt)
            or (self.le and self.lt)
            or (self.eq and any([self.ge, self.gt, self.le, self.lt]))
        ):
            raise ValueError(f"Ambiguous {self}")

    @classmethod
    def from_strings(cls, version_strings: List[str]) -> List["VulnerableVersion"]:
        # TODO: should fix func name.
        #   on current implement, we expect strings generated by Trivy as input.
        #   if Threatconnectome decided input spec, the func should be named based on it.
        if not version_strings:
            return []

        def _pick_heading_version(vstr: str) -> str:
            if not vstr:
                return ""
            tmp = re.split(r"[<>= ,]", vstr, maxsplit=1)[0]
            return tmp if len(tmp) > 0 else ""

        ret = set()
        for version_string in version_strings:
            for vstr in version_string.split("||"):
                kwargs = {}
                if len(tmp := re.split(r">= *", vstr, maxsplit=1)) > 1:
                    kwargs["ge"] = _pick_heading_version(tmp[1])
                if len(tmp := re.split(r"> *", vstr, maxsplit=1)) > 1:
                    kwargs["gt"] = _pick_heading_version(tmp[1])
                if len(tmp := re.split(r"<= *", vstr, maxsplit=1)) > 1:
                    kwargs["le"] = _pick_heading_version(tmp[1])
                if len(tmp := re.split(r"< *", vstr, maxsplit=1)) > 1:
                    kwargs["lt"] = _pick_heading_version(tmp[1])
                if len(tmp := re.split(r"(?<![<>])= *", vstr, maxsplit=1)) > 1:
                    kwargs["eq"] = _pick_heading_version(tmp[1])
                vulnVer = VulnerableVersion(**kwargs)
                ret.add(vulnVer)
        return list(ret)

    @staticmethod
    def _compare_versions(
        ver_a: Optional[str],
        ver_b: Optional[str],
    ) -> int:
        """
        returns 1 if ver_a > ver_b, -1 if if ver_a < ver_b, 0 otherwise.
        ValueError will be throws if cannot compare ver_a and ver_b.
        """
        re_number = re.compile(r"^[0-9]+")
        re_not_number = re.compile(r"^[^0-9]+")
        valError = ValueError(f"Cannot compare '{ver_a}' and '{ver_b}'")
        result: Optional[int] = None

        if (
            not ver_a
            or not ver_b
            or bool(re_number.match(ver_a)) != bool(re_number.match(ver_b))
            # compare startswith(number), no complement for the first token: ex) 1.0 - v1.0
        ):
            raise valError

        def pick_num(n_str: str) -> Tuple[int, str]:  # int, left string
            if not n_str:
                return (0, "")
            match = re_number.match(n_str)
            if not match:
                return (0, n_str)
            return (int(match[0]), n_str[len(match[0]) :])

        def pick_not_num(x_str: str) -> Tuple[str, str]:  # not-number, left string starts with num
            if not x_str:
                return ("", "")
            match = re_not_number.match(x_str)
            if not match:
                return ("", x_str)
            return (match[0], x_str[len(match[0]) :])

        while True:
            [num_a, ver_a] = pick_num(ver_a)
            [num_b, ver_b] = pick_num(ver_b)
            if num_a != num_b:
                result = result or (1 if num_a > num_b else -1)  # keep result if already judged
                # keep on comparing to detect format difference
            [not_num_a, ver_a] = pick_not_num(ver_a)
            [not_num_b, ver_b] = pick_not_num(ver_b)
            if not_num_a != not_num_b:
                if not not_num_a:
                    ver_a = "0"
                    continue
                if not not_num_b:
                    ver_b = "0"
                    continue
                raise valError
            if ver_a == "":
                break
        return result or 0

    def match(self, versions: List[str], on_error: Optional[bool] = None) -> bool:
        try:
            if self.eq:
                return any(self._compare_versions(self.eq, v) == 0 for v in versions)
            if all(
                any(
                    [  # detect NOT vulnerable
                        (self.lt and self._compare_versions(v, self.lt) >= 0),
                        (self.le and self._compare_versions(v, self.le) > 0),
                        (self.gt and self._compare_versions(v, self.gt) <= 0),
                        (self.ge and self._compare_versions(v, self.ge) < 0),
                    ]
                )
                for v in versions
            ):
                return False  # each version has at least 1 NOT matched rule
            return True
        except ValueError as err:  # found uncomparable
            if on_error is None:
                raise err
            return on_error


def _pick_vulnerable_versions(
    pteamtag: models.PTeamTag,
    actions: Sequence[models.TopicAction],
) -> List[VulnerableVersion]:
    version_strings = set()
    for action in actions:
        version_strings |= set(
            action.ext.get("vulnerable_versions", {}).get(pteamtag.tag.tag_name, [])
        )
    if pteamtag.tag.parent_name != pteamtag.tag.tag_name:
        for action in actions:
            version_strings |= set(
                action.ext.get("vulnerable_versions", {}).get(pteamtag.tag.parent_name, [])
            )

    vulnerable_versions = set(VulnerableVersion.from_strings(list(version_strings)))
    return list(vulnerable_versions)


def _complete_topic(db: Session, pteamtag: models.PTeamTag, actions: Sequence[models.TopicAction]):
    if not actions:
        return
    topic_id = actions[0].topic_id
    system_account = get_system_account(db)

    logging_ids = []
    for action in actions:
        action_log = create_actionlog_internal(
            schemas.ActionLogRequest(
                action_id=UUID(action.action_id),
                topic_id=UUID(topic_id),
                user_id=SYSTEM_UUID,
                pteam_id=UUID(pteamtag.pteam_id),
            ),
            system_account,
            db,
        )
        logging_ids.append(action_log.logging_id)

    set_pteam_topic_status_internal(
        pteamtag.pteam_id,
        topic_id,
        pteamtag.tag_id,
        schemas.TopicStatusRequest(
            topic_status=models.TopicStatusType.completed,
            logging_ids=logging_ids,
            note="auto closed by system",
        ),
        system_account,
        db,
    )


def pteamtag_try_auto_close_topic(db: Session, pteamtag: models.PTeamTag, topic: models.Topic):
    if topic.disabled:
        return
    if pteamtag.pteam.disabled:
        return
    if len(topic.zones) > 0 and not set(topic.zones) & set(pteamtag.pteam.zones):
        return  # this topic is unvisible from the pteam

    # pick unique reference versions to compare. (omit empty -- maybe added on WebUI)
    reference_versions = list(
        {ref_ver for ref in pteamtag.references if (ref_ver := ref.get("version"))}
    )
    if not reference_versions:
        return  # no versions to compare
    # pick all actions which matched on tags and zones
    actions = _pick_actions_related_to_pteamtag_from_topic(db, pteamtag, topic)
    if not actions:  # this topic does not have actions for this pteamtag
        return
    # pick unique vulnerable_versions from all actions
    try:
        vulnerable_versions = _pick_vulnerable_versions(pteamtag, actions)
    except ValueError:  # found empty or ambiguous, e.g. ">2.0 >=2.0"
        return

    # compare vulnerable_versions and reference_versions
    if any(vuln_ver.match(reference_versions, on_error=True) for vuln_ver in vulnerable_versions):
        return  # found vulnerable or uncomparable

    # you have valid actions and all reference versions are already cleared them.
    _complete_topic(db, pteamtag, actions)


def _pick_topics_related_to_pteamtag(
    db: Session,
    pteamtag: models.PTeamTag,
) -> Sequence[models.Topic]:
    now = datetime.now()
    already_completed_or_scheduled_stmt = (
        select(models.CurrentPTeamTopicTagStatus)
        .join(
            models.PTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.pteam_id == pteamtag.pteam_id,
                models.CurrentPTeamTopicTagStatus.tag_id == pteamtag.tag_id,
                models.CurrentPTeamTopicTagStatus.topic_id == models.Topic.topic_id,
                models.PTeamTopicTagStatus.status_id == models.CurrentPTeamTopicTagStatus.status_id,
                or_(
                    models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.completed,
                    and_(
                        models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.scheduled,
                        models.PTeamTopicTagStatus.scheduled_at > now,
                    ),
                ),
            ),
        )
        .exists()
    )
    accessible_topics_from_pteam_stmt = or_(
        ~exists().where(models.TopicZone.topic_id == models.Topic.topic_id),
        select(models.TopicZone)
        .join(
            models.PTeamZone,
            and_(
                models.PTeamZone.pteam_id == pteamtag.pteam_id,
                models.PTeamZone.zone_name == models.TopicZone.zone_name,
            ),
        )
        .exists(),
    )
    select_topic_stmt = select(models.Topic).join(
        models.TopicTag,
        and_(
            models.Topic.disabled.is_(False),
            models.TopicTag.tag_id.in_([pteamtag.tag_id, pteamtag.tag.parent_id]),
            models.TopicTag.topic_id == models.Topic.topic_id,
            accessible_topics_from_pteam_stmt,
            ~already_completed_or_scheduled_stmt,
        ),
    )

    topics = db.scalars(select_topic_stmt).all()
    return topics


def auto_close_by_pteamtags(db: Session, pteamtags: List[models.PTeamTag]):
    for pteamtag in pteamtags:
        if pteamtag.pteam.disabled:
            continue
        for topic in _pick_topics_related_to_pteamtag(db, pteamtag):
            pteamtag_try_auto_close_topic(db, pteamtag, topic)


def _pick_pteamtags_related_to_topic(
    db: Session,
    topic: models.Topic,
) -> Sequence[models.PTeamTag]:
    assert topic.disabled is False
    now = datetime.now()
    already_completed_or_scheduled_stmt = (
        select(models.CurrentPTeamTopicTagStatus)
        .join(
            models.PTeamTopicTagStatus,
            and_(
                models.CurrentPTeamTopicTagStatus.topic_id == topic.topic_id,
                models.PTeamTopicTagStatus.status_id == models.CurrentPTeamTopicTagStatus.status_id,
                or_(
                    models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.completed,
                    and_(
                        models.PTeamTopicTagStatus.topic_status == models.TopicStatusType.scheduled,
                        models.PTeamTopicTagStatus.scheduled_at > now,
                    ),
                ),
            ),
        )
        .exists()
    )
    accessible_topics_from_pteam_stmt = or_(
        ~exists().where(models.TopicZone.topic_id == topic.topic_id),  # public
        select(models.PTeamZone)
        .join(
            models.TopicZone,
            and_(
                models.TopicZone.topic_id == topic.topic_id,
                models.TopicZone.zone_name == models.PTeamZone.zone_name,
            ),
        )
        .exists(),
    )
    select_pteamtag_stmt = (
        select(models.PTeamTag)
        .join(models.Tag)
        .join(
            models.TopicTag,
            and_(
                models.TopicTag.topic_id == topic.topic_id,
                or_(
                    models.TopicTag.tag_id == models.Tag.tag_id,
                    models.TopicTag.tag_id == models.Tag.parent_id,
                ),
                accessible_topics_from_pteam_stmt,
                ~already_completed_or_scheduled_stmt,
            ),
        )
        .join(
            models.PTeam,
            and_(
                models.PTeam.disabled.is_(False),
                models.PTeamTag.pteam_id == models.PTeam.pteam_id,
            ),
        )
    )

    pteamtags = db.scalars(select_pteamtag_stmt).all()
    return pteamtags


def auto_close_by_topic(db: Session, topic: models.Topic):
    if topic.disabled:
        return
    for pteamtag in _pick_pteamtags_related_to_topic(db, topic):
        pteamtag_try_auto_close_topic(db, pteamtag, topic)
