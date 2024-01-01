from typing import List

from app import models


class AccountRepository:
    def __init__(self, db):
        self.db = db

    def get_all_accounts(self) -> List[models.Account]:
        return self.db.query(models.Account).all()

    def get_account_by_firebase_uid(self, account_id: str) -> models.Account | None:
        return self.db.query(models.Account).filter(models.Account.uid == account_id).one_or_none()

    def get_account_by_userid(self, user_id: str) -> models.Account | None:
        return self.db.query(models.Account).filter(models.Account.user_id == user_id).one_or_none()

    def get_account_by_email(self, account_email: str) -> models.Account | None:
        return self.db.query(models.Account).filter(models.Account.email == account_email).one_or_none()

    def get_accounts_by_team(self, team_id) -> List[models.Account]:
        return self.db.query(models.Account).filter(models.Account.team_id == team_id).all()

    def create_account(self, account) -> models.Account:
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_account(self, account_id, account) -> models.Account | None:
        account_to_update = self.db.query(models.Account).filter(models.Account.id == account_id).first()
        if account_to_update is None:
            return None
        account_to_update.name = account.name
        account_to_update.email = account.email
        account_to_update.team_id = account.team_id
        account_to_update.role = account.role
        account_to_update.status = account.status
        self.db.commit()
        return account_to_update

    def delete_account(self, account_id) -> models.Account | None:
        account_to_delete = self.db.query(models.Account).filter(models.Account.id == account_id).first()
        if account_to_delete is None:
            return None
        self.db.delete(account_to_delete)
        self.db.commit()
        return account_to_delete
