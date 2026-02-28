from sqlalchemy.orm import Session
from lib.repo.accounts_repository import get_all_accounts as repo_get_all_accounts

def get_all_accounts(session: Session):
    return repo_get_all_accounts(session)
