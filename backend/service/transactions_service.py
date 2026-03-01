from sqlalchemy.orm import Session
from lib.repo.transactions_repository import get_all_transactions as repo_get_all_transactions

def get_all_transactions(session: Session, account=None):
    return repo_get_all_transactions(session, account=account)
