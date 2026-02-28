from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from lib.database import get_session
from lib.repo.accounts_repository import get_account_by_name
from service.positions_service import get_positions_summary, get_positions_totals
from service.instruments_service import get_all_instruments
from service.transactions_service import get_all_transactions
from service.trades_service import get_all_trades
from service.accounts_service import get_all_accounts

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

@app.get("/api/positions/totals")
def read_positions_totals(
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

    totals = get_positions_totals(
        db, 
        account=account, 
        include_closed=include_closed, 
        include_open=include_open
    )
    
    return [vars(t) for t in totals]

@app.get("/api/instruments")
def read_instruments(db = Depends(get_db)):
    instruments = get_all_instruments(db)
    return instruments

@app.get("/api/transactions")
def read_transactions(db = Depends(get_db)):
    transactions = get_all_transactions(db)
    return [
        {
            "id": t.id,
            "date": t.date,
            "type": t.type,
            "amount": t.amount / 100.0 if t.amount is not None else None,
            "description": t.description,
            "account_id": t.account_id,
            "position_id": t.position_id,
        }
        for t in transactions
    ]

@app.get("/api/trades")
def read_trades(db = Depends(get_db)):
    trades = get_all_trades(db)
    return [
        {
            "id": t.id,
            "date": t.date,
            "type": t.type,
            "quantity": t.quantity,
            "price": t.price / 100.0 if t.price is not None else None,
            "description": t.description,
            "position_id": t.position_id,
        }
        for t in trades
    ]

@app.get("/api/accounts")
def read_accounts(db = Depends(get_db)):
    accounts = get_all_accounts(db)
    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
        }
        for a in accounts
    ]
