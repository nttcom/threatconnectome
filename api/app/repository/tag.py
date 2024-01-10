from uuid import UUID

from app import models


class TagRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(models.Tag).all()

    def get_by_id(self, tag_id: str | UUID) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.id == tag_id).one_or_none()

    def get_by_name(self, tag_name: str) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.tag_name == tag_name).one_or_none()

    def get_by_names(self, tag_names: list[str]) -> list[models.Tag]:
        return self.db.query(models.Tag).filter(models.Tag.tag_name.in_(tag_names)).all()

    def add(self, tag: models.Tag) -> models.Tag:
        self.db.add(tag)
        return tag

    def delete(self, tag: models.Tag) -> models.Tag:
        self.db.delete(tag)
        return tag

    # def update_tag(self, target_tag_id: str | UUID, tag: models.Tag) -> models.Tag:
    #     tag_to_update = self.db.query(models.Tag).filter(models.Tag.id == str(target_tag_id)).first()
    #     if tag_to_update is None:
    #         return None
    #     tag_to_update.tag_name = tag.tag_name

    #     return tag

    # def get_by_id(self, action_log_id: str | UUID):
    #     return (
    #         self.db.query(models.ActionLog)
    #         .filter(models.ActionLog.id == action_log_id)
    #         .one_or_none()
    #     )

    # def get_by_ids(self, user_ids: list[str] | list[UUID]):
    #     return self.db.query(models.ActionLog).filter(models.ActionLog.id.in_(user_ids)).all()

    # def get_action_logs_by_account_id(self, account_id):
    #     return (
    #         self.db.query(models.ActionLog).filter(models.ActionLog.account_id == account_id).all()
    #     )

    # def get_action_logs_by_pteam_id(self, pteam_id: str | UUID):
    #     # pteam = self.db.query(models.PTeam).filter(models.PTeam.team_id == team_id).one_or_none()
    #     return self.db.query(models.ActionLog).filter(models.ActionLog.pteam_id == pteam_id).all()

    # def search_action_logs(
    #     self,
    #     action_type: str,
    #     action_words: list[str] | None,
    #     action_types: list[str] | None,
    #     user_ids: list[UUID] | None,
    #     pteam_ids: list[UUID] | None,
    #     emails: list[str],
    #     executed_before: datetime,
    #     executed_after: datetime,
    #     created_before: datetime,
    #     created_after: datetime,
    # ) -> list[models.ActionLog]:
    #     query = self.db.query(models.ActionLog)
    #     if action_type:
    #         query = query.filter(models.ActionLog.action_type == action_type)

    #     if action_words:
    #         query = query.filter(
    #             models.ActionLog.action.bool_op("@@")(func.to_tsquery("|".join(action_words)))
    #         )

    #     if action_types:
    #         query = query.filter(models.ActionLog.action_type.in_(action_types))

    #     if user_ids:
    #         query = query.filter(models.ActionLog.user_id.in_(list(map(str, user_ids))))

    #     if pteam_ids:
    #         query = query.filter(models.ActionLog.pteam_id.in_(list(map(str, pteam_ids))))

    #     if emails:
    #         query = query.filter(models.ActionLog.email.in_(emails))

    #     if executed_before:
    #         query = query.filter(models.ActionLog.executed_at < executed_before)

    #     if executed_after:
    #         query = query.filter(models.ActionLog.executed_at >= executed_after)

    #     if created_before:
    #         query = query.filter(models.ActionLog.created_at < created_before)

    #     if created_after:
    #         query = query.filter(models.ActionLog.created_at >= created_after)

    #     return query.all()

    # def create_action_log(self, action_log: models.ActionLog) -> models.ActionLog:
    #     self.db.add(action_log)
    #     # self.db.commit()
    #     # self.db.refresh(action_log)
    #     return action_log

    # def update_action_log(self, action_log: models.ActionLog) -> models.ActionLog:
    #     self.db.commit()
    #     self.db.refresh(action_log)
    #     return action_log

    # def delete_action_log(self, action_log: models.ActionLog):
    #     self.db.delete(action_log)
    #     # self.db.commit()
