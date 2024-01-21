from datetime import datetime
from typing import Literal
from uuid import UUID

from app import models
from sqlalchemy import func


class TopicRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self) -> list[models.Topic]:
        return self.db.query(models.Topic).all()

    def get_by_id(self, topic_id: str | UUID) -> models.Topic | None:
        return self.db.query(models.Topic).filter(models.Topic.topic_id == str(topic_id)).one_or_none()

    SORT_KEYS = Literal["created_at", "updated_at"]
    def search(
        self,
        offset: int = 0,
        limit: int = 10,
        threat_impacts: list[int] | None = None,
        title_words: list[str] | None = None,
        abstract_words: list[str] | None = None,
        tag_ids: list[str] | list[UUID] | None = None,
        misp_tag_ids: list[str] | list[UUID]  | None = None,
        zone_names: list[str] | None  = None,
        topic_ids: list[str] | list[UUID]  | None = None,
        creator_ids: list[str] | list[UUID]  | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
        sort_key: SORT_KEYS = "created_at",
        ascending: bool = True
    ) -> list[models.Topic]:
        query = self.db.query(models.Topic)
        if threat_impacts:
            query = query.filter(models.Topic.threat_impact.in_(threat_impacts))
        if title_words:
            query = query.filter(
                models.Topic.title.bool_op("@@")(func.to_tsquery("|".join(title_words)))
            )
        if abstract_words:
            query = query.filter(
                models.Topic.abstract.bool_op("@@")(func.to_tsquery("|".join(abstract_words)))
            )
        if tag_ids:
            query = query.filter(models.Topic.tag_ids.overlap(list(map(str, tag_ids))))
        if misp_tag_ids:
            query = query.filter(models.Topic.misp_tag_ids.overlap(list(map(str, misp_tag_ids))))
        if zone_names:
            query = query.filter(models.Topic.zones.any(models.Zone.name.in_(zone_names)))
        if topic_ids:
            query = query.filter(models.Topic.id.in_(list(map(str, topic_ids))))
        if creator_ids:
            query = query.filter(models.Topic.created_by.in_(list(map(str, creator_ids))))
        if created_after:
            query = query.filter(models.Topic.created_at >= created_after)
        if created_before:
            query = query.filter(models.Topic.created_at <= created_before)
        if updated_after:
            query = query.filter(models.Topic.updated_at >= updated_after)
        if updated_before:
            query = query.filter(models.Topic.updated_at <= updated_before)

        if sort_key == "created_at":
            if ascending:
                query = query.order_by(models.Topic.created_at.asc())
            else:
                query = query.order_by(models.Topic.created_at.desc())
        elif sort_key == "updated_at":
            if ascending:
                query = query.order_by(models.Topic.updated_at.asc())
            else:
                query = query.order_by(models.Topic.updated_at.desc())

        return query.offset(offset).limit(limit).all()
