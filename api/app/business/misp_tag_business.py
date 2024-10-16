from sqlalchemy.orm import Session

from app import models, persistence


def get_or_create_misp_tag(db: Session, tag_name: str) -> models.MispTag:
    if misp_tag := persistence.get_misp_tag_by_name(db, tag_name):
        return misp_tag

    misp_tag = models.MispTag(tag_name=tag_name)
    persistence.create_misp_tag(db, misp_tag)
    return misp_tag
