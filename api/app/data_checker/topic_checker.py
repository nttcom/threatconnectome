from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, persistence


def check_and_get_topic(
    db: Session,
    topic_id: UUID,
) -> models.Topic:
    if not (topic := persistence.get_topic_by_id(db, topic_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such topic")
    return topic
