from sqlalchemy.orm import Session
from lib.repo.trades_repository import get_all_trades as repo_get_all_trades, get_all_trades_by_account as repo_get_all_trades_by_account

def get_all_trades(session: Session, account=None):
    if account:
        return repo_get_all_trades_by_account(session, account)
    return repo_get_all_trades(session)
