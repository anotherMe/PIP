
# No pandas dependency
import pytz
from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from lib.database import get_session, read_from_db, write_to_db
from lib.models import Price, Instrument, UTCDateTime
from service.myYahooFinanceService import YahooSymbol

from logging_config import setup_logger
log = setup_logger(__name__)

DEFAULT_TIMEZONE = "Europe/Rome"


def load_prices_from_symbol(symbol: YahooSymbol, granularity: str, instrument: Instrument):
    """
    Given a YahooSymbol with 'ochlv' dicts,
    inserts MarketPrice rows for the instrument identified by ticker.
    """

    ochlv_data = symbol.ochlv
    if not ochlv_data:
        print("No OHLCV data to insert.")
        return
    
    inserted = 0
    skipped = 0

    with get_session() as session, session.begin():

        # Pre-fetch existing timestamps for this symbol
        existing_timestamps = set(
            session.scalars(
                select(Price.date).where(Price.instrument_id == instrument.id)
            ).all()
        )

        for row in ochlv_data:
            dt = row["timestamp"]
            if dt in existing_timestamps:
                skipped += 1
                continue

            entry = Price(
                instrument_id=instrument.id,
                date=dt,
                price=write_to_db(int(row["close"] or 0)) if row["close"] is not None else 0,
                granularity=granularity
            )

            session.add(entry)
            inserted += 1

        session.commit()

    print(f"Inserted {inserted} new prices, skipped {skipped} duplicates.")

def load_prices_from_yfinance_dataframe(dataframe, granularity: str, instrument: Instrument):
    """
    Given a yfinance DataFrame with 'timestamp' and 'close' columns,
    inserts MarketPrice rows for the instrument identified by ticker.
    """

    if dataframe.empty:
        print("No OHLCV data to insert.")
        return
    
    inserted = 0
    skipped = 0

    with get_session() as session, session.begin():

        # Pre-fetch existing timestamps for this symbol
        existing_timestamps = set(
            session.scalars(
                select(Price.date).where(Price.instrument_id == instrument.id)
            ).all()
        )

        for ts, row in dataframe.iterrows():
            if ts.to_pydatetime() in existing_timestamps:
                skipped += 1
                continue

            entry = Price(
                instrument_id=instrument.id,
                date=ts,
                price=write_to_db(row["Close"]),
                granularity=granularity
            )

            session.add(entry)
            inserted += 1

        session.commit()

    print(f"Inserted {inserted} new prices, skipped {skipped} duplicates.")


def get_latest_prices_for_instrument_list(session, inst_ids: list[int]):
    
    subquery = (
        select(
            Price.instrument_id,
            func.max(Price.date).label("latest_date")
        )
        .where(Price.instrument_id.in_(inst_ids))
        .group_by(Price.instrument_id)
        .subquery()
    )

    stmt = (
        select(Price.instrument_id, Price.price, subquery.c.latest_date.label("date"))
        .join(
            subquery,
            (Price.instrument_id == subquery.c.instrument_id) &
            (Price.date == subquery.c.latest_date)
        )
    )

    return session.execute(stmt).all()


def get_latest_price(session, inst_id):
    """Return the latest market price for an instrument, or None."""
    
    stmt = (
        select(Price.price)
        .where(Price.instrument_id == inst_id)
        .order_by(Price.date.desc())
        .limit(1)
    )
    return session.scalar(stmt)

def get_latest_prices(session):
    """Return a dictionary of latest prices for all instruments."""
    
    subquery = (
        select(
            Price.instrument_id,
            func.max(Price.date).label("latest_date")
        )
        .group_by(Price.instrument_id)
        .subquery()
    )

    stmt = (
        select(Price.instrument_id, Price.price, subquery.c.latest_date.label("date"))
        .join(
            subquery,
            (Price.instrument_id == subquery.c.instrument_id) &
            (Price.date == subquery.c.latest_date)
        )
    )

    return session.execute(stmt).mappings().all()


class PriceDTO:
    def __init__(self, instrument_id: int, price: float, date):
        self.instrument_id = instrument_id
        self.price = price
        self.date = date

# TODO: move to prices_service.py
def get_latest_prices_for_prices_list(session) -> list[dict]:
        
    # Subquery: get latest timestamp for each instrument
    latest_ts_subq = (
        select(
            Price.instrument_id,
            func.max(Price.date).label("latest_ts")
        )
        .group_by(Price.instrument_id)
        .subquery()
    )

    # Alias OHLCV for joining
    price_latest = aliased(Price)

    # Main query: left join instruments with latest ohlcv data
    query = (
        select(
            Instrument.name,
            Instrument.ticker,
            Instrument.currency,
            price_latest.price,
            price_latest.date
        )
        .outerjoin(
            latest_ts_subq,
            Instrument.id == latest_ts_subq.c.instrument_id
        )
        .outerjoin(
            price_latest,
            (price_latest.instrument_id == latest_ts_subq.c.instrument_id)
            & (price_latest.date == latest_ts_subq.c.latest_ts)
        )
        .order_by(Instrument.name)
    )

    results = session.execute(query).fetchall()

    return [
        {
            "instrument_name": r.name,
            "instrument_ticker": r.ticker,
            "instrument_currency": r.currency.name if r.currency else None,
            "instrument_symbol": r.currency.symbol if r.currency else "",
            "last_close": r.price,
            "timestamp": r.date
        }
        for r in results
    ]
