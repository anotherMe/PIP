from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from lib.database import get_session
from lib.repo.accounts_repository import get_account_by_name
from service.positions_service import get_positions_summary

app = FastAPI(title="PIP Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/api/positions")
def read_positions(
    account_name: Optional[str] = "All",
    status_filter: str = Query("all", description="all, open, or closed"),
    db = Depends(get_db)
):
    include_closed = status_filter in ("all", "closed")
    include_open = status_filter in ("all", "open")
    
    account = None
    if account_name and account_name.lower() != "all":
        account = get_account_by_name(db, account_name)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    positions = get_positions_summary(
        db, 
        account=account, 
        include_closed=include_closed, 
        include_open=include_open
    )
    
    # Serialize to standard list of dicts to avoid serialization issues
    return [vars(p) for p in positions]
