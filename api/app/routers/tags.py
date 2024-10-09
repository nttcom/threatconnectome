from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query as QueryParameter
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import command, models, persistence, schemas
from app.auth import get_current_user
from app.business.tag_business import get_or_create_topic_tag
from app.database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[schemas.TagResponse])
def get_tags(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all tags sorted by tagName.
    """
    tags = persistence.get_all_tags(db)
    return sorted(tags, key=lambda tag: tag.tag_name)


@router.post("", response_model=schemas.TagResponse)
def create_tag(
    request: schemas.TagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a tag (and parent tag if not exist).
    """
    if persistence.get_tag_by_name(db, request.tag_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")
    tag = get_or_create_topic_tag(db, request.tag_name)

    db.commit()

    return tag


@router.get("/search", response_model=list[schemas.TagResponse])
def search_tags(
    words: list[str] | None = QueryParameter(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search tags.
    If given a list of words, return all tags that match any of the words.
    """
    all_tags = persistence.get_all_tags(db)
    # If no words were provided, return all tags.
    if words is None:
        return all_tags

    # Otherwise, search for tags that match the provided words.
    return filter(lambda x: any(word.lower() in x.tag_name.lower() for word in words), all_tags)


@router.get("/{tag_id}", response_model=schemas.TagResponse)
def get_tag(
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a tag.
    """
    if not (tag := persistence.get_tag_by_id(db, tag_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")

    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tag.
    """
    tag = persistence.get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such tag")
    assert tag

    num_of_child_tags = command.get_num_of_child_tags(db, tag)
    has_child_tags = num_of_child_tags > 0
    if has_child_tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete parent tag while having child tags",
        )

    if (
        command.get_num_of_tags_by_tag_id_of_pteam_tag_reference(db, tag_id) > 0
        or command.get_num_of_tags_by_tag_id_of_topic_tag(db, tag_id) > 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Requested tag is in use"
        )

    persistence.delete_tag(db, tag)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # avoid Content-Length Header
