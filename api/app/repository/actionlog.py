from uuid import UUID

from app import models


class ActionLogRepository:
    def __init__(self, db):
        self.db = db

    def get_all_action_logs(self):
        return self.db.query(models.ActionLog).all()

    def get_action_log_by_id(self, action_log_id: str | UUID):
        return self.db.query(models.ActionLog).filter(models.ActionLog.id == action_log_id).one_or_none()

    def get_action_logs_by_account_id(self, account_id):
        return self.db.query(models.ActionLog).filter(models.ActionLog.account_id == account_id).all()

    def get_action_logs_by_team_id(self, team_id: str | UUID):
        #pteam = self.db.query(models.PTeam).filter(models.PTeam.team_id == team_id).one_or_none()
        #return self.db.query(models.ActionLog).filter(models.ActionLog.PTeam.team_id == team_id).all()
        pass

    def search_action_logs(self, action_type: str, action_words: str, user_id: str, pteam_id: str, email: str, executed_before: datetime, executed_after: datetime, created_before: datetime, created_after: datetime) -> list[models.ActionLog]:
        query = self.db.query(models.ActionLog)
        if action_type:
            query = query.filter(models.ActionLog.action_type == action_type)

        if action_words:
            query = query.filter(models.ActionLog.action.like(f"%{action_words}%"))

        return query.all()

    def create_action_log(self, action_log: models.ActionLog) -> models.ActionLog:
        self.db.add(action_log)
        #self.db.commit()
        #self.db.refresh(action_log)
        return action_log

    def update_action_log(self, action_log: models.ActionLog) -> models.ActionLog:
        self.db.commit()
        self.db.refresh(action_log)
        return action_log

    def delete_action_log(self, action_log: models.ActionLog):
        self.db.delete(action_log)
        #self.db.commit()
