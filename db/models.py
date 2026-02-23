from sqlalchemy import Column, Integer, String, Float, Date, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base(metadata=MetaData())


class OHLCV(Base):
    __tablename__ = "ohlcv"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class SymbolMetadata(Base):
    __tablename__ = "symbol_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True)
    sector = Column(String)
    industry = Column(String)
    exchange = Column(String)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # 'BUY', 'SELL', 'LONG', 'SHORT'
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    status = Column(String(20), nullable=False)
    strategy_id = Column(String, nullable=True)

    # Audit and classification fields
    trade_type = Column(String, nullable=True)  # e.g. 'intraday' or 'positional'
    entry_reason = Column(
        String, nullable=True
    )  # e.g. 'signal', 'manual', 'forced_exit'
    exit_reason = Column(
        String, nullable=True
    )  # e.g. 'target', 'stoploss', 'forced_exit'

    note = Column(String, nullable=True)
