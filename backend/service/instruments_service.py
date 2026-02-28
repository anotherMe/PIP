from sqlalchemy.orm import Session
from lib.repo.instruments_repository import get_all_instruments as repo_get_all_instruments

def get_all_instruments(session: Session):
    return repo_get_all_instruments(session)
