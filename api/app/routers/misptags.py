from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query as QueryParameter
from sqlalchemy.orm import Session

from app import models, persistence, schemas
from app.auth.account import get_current_user
from app.database import get_db

router = APIRouter(prefix="/misp_tags", tags=["misp_tags"])


@router.get("", response_model=list[schemas.MispTagResponse])
def get_misp_tags(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all misp tags.
    """
    return persistence.get_all_misp_tags(db)


@router.post("", response_model=schemas.MispTagResponse)
def create_misp_tag(
    request: schemas.MispTagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a misp tag.
    """
    if persistence.get_misp_tag_by_name(db, request.tag_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")

    misp_tag = models.MispTag(tag_name=request.tag_name)
    persistence.create_misp_tag(db, misp_tag)

    db.commit()

    return misp_tag


@router.get("/search", response_model=list[schemas.MispTagResponse])
def search_misp_tags(
    words: list[str] | None = QueryParameter(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search misp tags.
    If given a list of words, return all misp tags that match any of the words.
    """
    all_misp_tags = persistence.get_all_misp_tags(db)
    # If no words were provided, return all misp tags.
    if words is None:
        return all_misp_tags

    # Otherwise, search for tags that match the provided words.
    return filter(
        lambda x: any(word.lower() in x.tag_name.lower() for word in words), all_misp_tags
    )
