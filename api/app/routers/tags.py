from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query as QueryParameter
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.common import get_or_create_topic_tag, validate_tag
from app.database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[schemas.TagResponse])
def get_tags(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all tags sorted by tagName.
    """
    # Get scalar value because converting python object is slow
    # TODO: add pagination
    select_statement = select(models.Tag).order_by(models.Tag.tag_name)
    return db.scalars(select_statement).all()


@router.post("", response_model=schemas.TagResponse)
def create_tag(
    request: schemas.TagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a tag (and parent tag if not exist).
    """
    if db.query(models.Tag).filter(models.Tag.tag_name == request.tag_name).one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")
    return get_or_create_topic_tag(db, request.tag_name)


@router.get("/search", response_model=List[schemas.TagResponse])
def search_tags(
    words: Optional[List[str]] = QueryParameter(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search tags.
    If given a list of words, return all tags that match any of the words.
    """
    # If no words were provided, return all tags.
    if words is None:
        return db.query(models.Tag).all()

    # Otherwise, search for tags that match the provided words.
    query = db.query(models.Tag).filter(
        models.Tag.tag_name.bool_op("@@")(func.to_tsquery("|".join(words)))
    )
    return query.all()


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tag.
    """
    tag = validate_tag(db, tag_id=tag_id, on_error=status.HTTP_404_NOT_FOUND)
    assert tag

    num_of_child_tags = (
        db.query(models.Tag)
        .filter(
            models.Tag.parent_id == tag.tag_id,
            models.Tag.tag_id != tag.tag_id,
        )
        .count()
    )
    has_child_tags = num_of_child_tags > 0
    if has_child_tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete parent tag while having child tags",
        )

    if (
        db.query(models.PTeamTag).filter(models.PTeamTag.tag_id == str(tag_id)).count() > 0
        or db.query(models.TopicTag).filter(models.TopicTag.tag_id == str(tag_id)).count() > 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Requested tag is in use"
        )

    db.delete(tag)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header
