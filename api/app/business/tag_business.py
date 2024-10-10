from typing import Sequence

from sqlalchemy.orm import Session

from app import models, persistence, schemas


def _pick_parent_tag(tag_name: str) -> str | None:
    if len(tag_name.split(":", 2)) == 3:  # supported format
        return tag_name.rsplit(":", 1)[0] + ":"  # trim the right most field
    return None


def check_topic_action_tags_integrity(
    topic_tags: Sequence[str] | Sequence[models.Tag],  # tag_name list or topic.tags
    action_tags: Sequence[str] | None,  # action.ext.get("tags")
) -> bool:
    if not action_tags:
        return True

    topic_tag_strs = {x if isinstance(x, str) else x.tag_name for x in topic_tags}
    for action_tag in action_tags:
        if action_tag not in topic_tag_strs and _pick_parent_tag(action_tag) not in topic_tag_strs:
            return False
    return True


def get_or_create_topic_tag(db: Session, tag_name: str) -> models.Tag:
    if tag := persistence.get_tag_by_name(db, tag_name):  # already exists
        return tag

    return create_topic_tag(db, tag_name)


def create_topic_tag(db: Session, tag_name: str) -> models.Tag:
    tag = models.Tag(tag_name=tag_name, parent_id=None, parent_name=None)
    if not (parent_name := _pick_parent_tag(tag_name)):  # no parent: e.g. "tag1"
        persistence.create_tag(db, tag)
        return tag

    if parent_name == tag_name:  # parent is myself
        tag.parent_id = tag.tag_id
        tag.parent_name = tag_name
    else:
        parent = persistence.get_tag_by_name(db, parent_name)
        if not parent:
            parent = create_topic_tag(db, parent_name)
        tag.parent_id = parent.tag_id
        tag.parent_name = parent.tag_name

    persistence.create_tag(db, tag)

    return tag


def get_pteam_ext_tags(pteam: models.PTeam) -> Sequence[schemas.ExtTagResponse]:
    ext_tags_dict: dict[str, schemas.ExtTagResponse] = {}
    for service in pteam.services:
        for dependency in service.dependencies:
            ext_tag = ext_tags_dict.get(
                dependency.tag_id,
                schemas.ExtTagResponse(
                    tag_id=dependency.tag_id,
                    tag_name=dependency.tag.tag_name,
                    parent_id=dependency.tag.parent_id,
                    parent_name=dependency.tag.parent_name,
                    references=[],
                ),
            )
            ext_tag.references.append(
                {
                    "service": service.service_name,
                    "target": dependency.target,
                    "version": dependency.version,
                }
            )
            ext_tags_dict[dependency.tag_id] = ext_tag

    return sorted(ext_tags_dict.values(), key=lambda x: x.tag_name)
