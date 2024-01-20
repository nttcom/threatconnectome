from datetime import datetime
from uuid import UUID

from app import models
from sqlalchemy import func


class ActionLogRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.query(models.ActionLog).all()

    def get_by_id(self, action_log_id: str | UUID):
        return (
            self.db.query(models.ActionLog)
            .filter(models.ActionLog.logging_id == str(action_log_id))
            .one_or_none()
        )

    def get_by_ids(self, action_log_ids: list[str] | list[UUID]):
        action_log_ids = list(map(str, action_log_ids))
        return self.db.query(models.ActionLog).filter(models.ActionLog.logging_id.in_(action_log_ids)).all()

    def get_by_account_id(self, account_id):
        return (
            self.db.query(models.ActionLog).filter(models.ActionLog.account_id == account_id).all()
        )

    def get_by_pteam_id(self, pteam_id: str | UUID):
        # pteam = self.db.query(models.PTeam).filter(models.PTeam.team_id == team_id).one_or_none()
        return self.db.query(models.ActionLog).filter(models.ActionLog.pteam_id == pteam_id).all()

    def search(
        self,
        topic_ids: list[UUID] | list[str] | None = None,
        action_words: list[str] | None = None,
        action_types: list[str] | None = None,
        user_ids: list[UUID] | list[str] | None = None,
        pteam_ids: list[UUID] | list[str] | None = None,
        emails: list[str] | None = None,
        executed_before: datetime | None = None,
        executed_after: datetime | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
    ) -> list[models.ActionLog]:
        query = self.db.query(models.ActionLog)

        if topic_ids is not None:
            query = query.filter(models.ActionLog.topic_id.in_(list(map(str, topic_ids))))

        if action_words is not None:
            query = query.filter(
                models.ActionLog.action.bool_op("@@")(func.to_tsquery("|".join(action_words)))
            )

        if action_types is not None:
            query = query.filter(models.ActionLog.action_type.in_(action_types))

        if user_ids is not None:
            query = query.filter(models.ActionLog.user_id.in_(list(map(str, user_ids))))

        if pteam_ids is not None:
            query = query.filter(models.ActionLog.pteam_id.in_(list(map(str, pteam_ids))))

        if emails is not None:
            query = query.filter(models.ActionLog.email.in_(emails))

        if executed_before:
            query = query.filter(models.ActionLog.executed_at < executed_before)

        if executed_after:
            query = query.filter(models.ActionLog.executed_at >= executed_after)

        if created_before:
            query = query.filter(models.ActionLog.created_at < created_before)

        if created_after:
            query = query.filter(models.ActionLog.created_at >= created_after)

        return query.all()

    def add(self, action_log: models.ActionLog) -> models.ActionLog:
        self.db.add(action_log)

    def delete(self, action_log: models.ActionLog):
        self.db.delete(action_log)

# def usecase():
#     actionlogs = []
#     # Create
#     log = ActionLog()
#     repository.add(log)

#     session.commit()

#     # Read
#     log = repository.findById(id: logId)

#     # Update
#     actionlog = repository.find()
#     actionlog.description = ""

#     session.commit()

#     # Delete
#     actionlog = repository.find()
#     repository.delete(actionlog)

#     repository.deleteById(actionlogId)

#     session.commit()

