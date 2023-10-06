from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.common import (
    check_gteam_membership,
    get_authorized_zones,
    validate_gteam,
    validate_zone,
)
from app.database import get_db

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=List[schemas.ZoneEntry])
def get_zones(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all zones.
    """
    return db.query(models.Zone).all()


def create_zone_internal(
    db: Session,
    request: schemas.ZoneRequest,
    gteam_id: Union[UUID, str],
    user: models.Account,
) -> models.Zone:
    gteam = validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    assert gteam
    check_gteam_membership(db, gteam_id, user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    # TODO: check gteam auth for zone creation

    if db.query(models.Zone).filter(models.Zone.zone_name == request.zone_name).one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")

    zone = models.Zone(
        **request.model_dump(), gteam_id=gteam_id, archived=False, created_by=user.user_id
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)

    return zone


def delete_zone_internal(
    db: Session,
    zone_name: str,
    gteam_id: Union[UUID, str],
    user: models.Account,
):
    validate_gteam(db, gteam_id, on_error=status.HTTP_404_NOT_FOUND)
    check_gteam_membership(db, gteam_id, user.user_id, on_error=status.HTTP_403_FORBIDDEN)
    zone = validate_zone(
        db,
        user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="admin",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone

    if (
        db.query(models.PTeamZone).filter(models.PTeamZone.zone_name == zone_name).count() > 0
        or db.query(models.TopicZone).filter(models.TopicZone.zone_name == zone_name).count() > 0
        or db.query(models.ActionZone).filter(models.ActionZone.zone_name == zone_name).count() > 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Requested zone is in use"
        )

    db.delete(zone)
    db.commit()


@router.get("/authorized_for_me", response_model=schemas.AuthorizedZones)
def get_authorized(
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get authorized zones for current user.
    """
    admin_zones, appliable_zones, readable_zones = get_authorized_zones(db, current_user)
    return {
        "admin": admin_zones,
        "apply": appliable_zones,
        "read": readable_zones,
    }


@router.get("/{zone_name}/teams", response_model=schemas.ZonedTeamsResponse)
def get_zoned_teams(
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get zoned teams.
    """
    zone = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="read",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone

    # To select all accessable ateams, we use join here.
    ateams = (
        db.query(models.ATeam)
        .join(models.ATeamPTeam)
        .join(
            models.PTeamZone,
            and_(
                models.PTeamZone.zone_name == zone_name,
                models.PTeamZone.pteam_id == models.ATeamPTeam.pteam_id,
            ),
        )
        .all()
    )

    # This endpoint return all accessable teams to zone
    return {
        "zone": zone,
        "gteam": zone.gteam,
        "pteams": zone.pteams,
        "ateams": ateams,
    }


@router.get("/{zone_name}/topics", response_model=schemas.ZonedTopicsResponse)
def get_zoned_topics(
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get zoned topics.
    """
    zone = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="read",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone
    return {
        "zone": zone,
        "gteam": zone.gteam,
        "topics": zone.topics,
    }


@router.get("/{zone_name}/actions", response_model=schemas.ZonedActionsResponse)
def get_zoned_actions(
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get zoned actions.
    """
    zone = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="read",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone
    return {
        "zone": zone,
        "gteam": zone.gteam,
        "actions": [
            {**action.__dict__, "zones": action.zones, "topic_title": action.topic.title}
            for action in zone.actions
        ],
    }


@router.get("/{zone_name}/latest_topic", response_model=schemas.ZonedLatestTopicResponse)
def get_zoned_latest_topic(
    zone_name: str,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get latest updated topics of the zone.
    """
    zone = validate_zone(
        db,
        current_user.user_id,
        zone_name,
        on_error=status.HTTP_404_NOT_FOUND,
        auth_mode="read",
        on_auth_error=status.HTTP_403_FORBIDDEN,
    )
    assert zone

    # To avoid load all topics to application server from DB, we use join here.
    latest_topic = (
        db.query(models.Topic)
        .join(
            models.TopicZone,
            and_(
                models.TopicZone.zone_name == zone_name,
                models.TopicZone.topic_id == models.Topic.topic_id,
            ),
        )
        .filter(models.Topic.disabled.is_(False))
        .order_by(models.Topic.updated_at.desc())
        .first()
    )

    return {
        "zone": zone,
        "gteam": zone.gteam,
        "latest_topic": latest_topic,
    }
