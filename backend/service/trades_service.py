from sqlalchemy.orm import Session
from lib.repo.trades_repository import get_all_trades as repo_get_all_trades

def get_all_trades(session: Session):
    return repo_get_all_trades(session)
