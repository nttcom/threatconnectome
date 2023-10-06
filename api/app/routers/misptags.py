from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query as QueryParameter
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/misp_tags", tags=["misp_tags"])


@router.get("", response_model=List[schemas.MispTagResponse])
def get_misp_tags(
    current_user: models.Account = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all misp tags.
    """
    return db.query(models.MispTag).all()


@router.post("", response_model=schemas.MispTagResponse)
def create_misp_tag(
    request: schemas.MispTagRequest,
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a misp tag.
    """
    if db.query(models.MispTag).filter(models.MispTag.tag_name == request.tag_name).one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists")
    misptag = models.MispTag(tag_name=request.tag_name)
    db.add(misptag)
    db.commit()
    db.refresh(misptag)
    return misptag


@router.get("/search", response_model=List[schemas.MispTagResponse])
def search_misp_tags(
    words: Optional[List[str]] = QueryParameter(None),
    current_user: models.Account = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search misp tags.
    If given a list of words, return all misp tags that match any of the words.
    """
    # If no words were provided, return all misp tags.
    if words is None:
        return db.query(models.MispTag).all()

    # Otherwise, search for tags that match the provided words.
    return (
        db.query(models.MispTag)
        .filter(models.MispTag.tag_name.bool_op("@@")(func.to_tsquery("|".join(words))))
        .all()
    )
