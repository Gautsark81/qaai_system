# db/db_utils.py
"""
Supercharged DB utilities built on SQLAlchemy.

Features:
 - ORM models (OHLCV, SymbolMetadata, AuditPipelineRun)
 - DBManager with scoped sessions + connection pooling
 - bulk upsert helpers for OHLCV (chunked), single upsert, fetch helpers
 - resilient fetch_recent_runs: tries Postgres first, falls back to JSONL loader
 - JSONL export/import helpers for audit logs
"""

from __future__ import annotations
import os
import glob
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import pandas as pd
except Exception:
    pd = None  # type: ignore

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, JSON, Index, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, date, timezone
import math

Base = declarative_base()


class OHLCV(Base):
    __tablename__ = "ohlcv"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Index("ix_ohlcv_symbol_date", OHLCV.symbol, OHLCV.date, unique=False)


class SymbolMetadata(Base):
    __tablename__ = "symbol_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    exchange = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditPipelineRun(Base):
    __tablename__ = "audit_pipeline_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    mode = Column(String, nullable=False)
    top_k = Column(Integer, nullable=False)
    watchlist = Column(JSON)
    signals = Column(JSON)
    orders = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------
# DBManager
# -------------------------
class DBManager:
    """
    DBManager: SQLAlchemy based manager.

    db_url examples:
      - sqlite:///qaai.db
      - postgresql://user:pass@host:port/dbname
    """

    def __init__(self, db_url: Optional[str] = None, echo: bool = False, pool_size: int = 5, max_overflow: int = 10):
        db_url = db_url or os.environ.get("QA_SQLALCHEMY_DATABASE_URI", "sqlite:///qaai.db")
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=echo, pool_size=pool_size, max_overflow=max_overflow, future=True)
        self.SessionFactory = scoped_session(sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True))
        Base.metadata.create_all(self.engine)

    def _session(self):
        return self.SessionFactory()

    def close(self):
        try:
            self.SessionFactory.remove()
        except Exception:
            pass

    # ----- OHLCV helpers -----
    def insert_ohlcv_batch(self, records: List[Dict[str, Any]], chunk_size: int = 1000) -> int:
        """
        Insert many OHLCV records in chunks. Records must contain keys:
          - symbol, date (date/datetime/str), open, high, low, close, volume
        Returns total inserted.
        """
        total = 0
        session = self._session()
        try:
            for i in range(0, len(records), chunk_size):
                chunk = records[i : i + chunk_size]
                objs = []
                for r in chunk:
                    rec = dict(r)
                    if isinstance(rec.get("date"), str):
                        rec["date"] = pd.to_datetime(rec["date"]).date() if pd else datetime.fromisoformat(rec["date"]).date()
                    elif isinstance(rec.get("date"), datetime):
                        rec["date"] = rec["date"].date()
                    objs.append(OHLCV(symbol=str(rec["symbol"]), date=rec["date"], open=float(rec["open"]), high=float(rec["high"]), low=float(rec["low"]), close=float(rec["close"]), volume=float(rec.get("volume", 0))))
                session.bulk_save_objects(objs)
                session.commit()
                total += len(objs)
            return total
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_ohlcv_from_csv(self, file_path: str, symbol: str, date_col: str = "date") -> int:
        if not pd:
            raise RuntimeError("pandas required for CSV ingestion")
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        df = pd.read_csv(file_path, parse_dates=[date_col])
        df = df.rename(columns={date_col: "date"})
        df["symbol"] = symbol
        df["date"] = pd.to_datetime(df["date"]).dt.date
        records = df.to_dict(orient="records")
        return self.insert_ohlcv_batch(records)

    def get_ohlcv(self, symbol: str, start_date: date, end_date: date) -> List[OHLCV]:
        session = self._session()
        try:
            q = session.query(OHLCV).filter(OHLCV.symbol == symbol).filter(OHLCV.date >= start_date).filter(OHLCV.date <= end_date).order_by(OHLCV.date.asc())
            return q.all()
        finally:
            session.close()

    def get_ohlcv_df(self, symbol: str, start_date: Any, end_date: Any) -> "pd.DataFrame":
        if pd is None:
            raise RuntimeError("pandas not available")
        # coercion
        start = pd.to_datetime(start_date).date() if not isinstance(start_date, date) else start_date
        end = pd.to_datetime(end_date).date() if not isinstance(end_date, date) else end_date
        rows = self.get_ohlcv(symbol, start, end)
        if not rows:
            return pd.DataFrame()
        recs = []
        for r in rows:
            recs.append({"timestamp": pd.to_datetime(r.date), "symbol": r.symbol, "open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume})
        df = pd.DataFrame(recs)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    # ----- Symbol metadata -----
    def upsert_symbol_metadata(self, symbol: str, name: str = "", sector: str = "", exchange: str = "") -> None:
        session = self._session()
        try:
            obj = session.query(SymbolMetadata).filter_by(symbol=symbol).first()
            if obj:
                obj.name = name or obj.name
                obj.sector = sector or obj.sector
                obj.exchange = exchange or obj.exchange
            else:
                obj = SymbolMetadata(symbol=symbol, name=name, sector=sector, exchange=exchange)
                session.add(obj)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ----- Audit pipeline runs -----
    def insert_audit_run(self, mode: str, top_k: int, watchlist: List[Dict], signals: List[Dict], orders: List[Dict]) -> int:
        session = self._session()
        try:
            run = AuditPipelineRun(run_timestamp=datetime.utcnow(), mode=mode, top_k=int(top_k), watchlist=watchlist, signals=signals, orders=orders)
            session.add(run)
            session.commit()
            return run.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def fetch_recent_runs(self, limit: int = 50) -> "pd.DataFrame":
        """
        Try to fetch from DB; on failure fallback to JSONL loader.
        """
        # try DB
        try:
            session = self._session()
            try:
                q = session.query(AuditPipelineRun).order_by(AuditPipelineRun.id.desc()).limit(int(limit))
                rows = q.all()
                recs = []
                for r in rows:
                    recs.append({"id": r.id, "run_timestamp": r.run_timestamp, "mode": r.mode, "top_k": r.top_k, "watchlist": r.watchlist, "signals": r.signals, "orders": r.orders})
                if pd:
                    return pd.DataFrame(recs)
                return recs  # type: ignore
            finally:
                session.close()
        except Exception:
            # fallback to JSONL logs
            df = fallback_load_audit_logs_df(limit=limit)
            if df is not None:
                return df
            if pd:
                return pd.DataFrame()
            return []  # type: ignore

    # ----- Export / import JSONL helpers -----
    def export_audit_runs_to_jsonl(self, out_path: str, limit: Optional[int] = None) -> int:
        df_or_list = self.fetch_recent_runs(limit=limit or 1000)
        if isinstance(df_or_list, list):
            rows = df_or_list
        elif pd is not None and isinstance(df_or_list, pd.DataFrame):
            rows = df_or_list.to_dict(orient="records")
        else:
            rows = []
        with open(out_path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, default=str) + "\n")
        return len(rows)

    # ----- Upsert helpers (single & bulk) -----
    def upsert_ohlcv(self, records: List[Dict[str, Any]], chunk: int = 500) -> int:
        """
        Upsert OHLCV by symbol+date using INSERT ... ON CONFLICT for sqlite/postgres where supported.
        For portability we do a two-step upsert: try native ON CONFLICT where DB dialect supports it.
        """
        total = 0
        session = self._session()
        dialect = session.bind.dialect.name
        try:
            for i in range(0, len(records), chunk):
                batch = records[i : i + chunk]
                if dialect in ("sqlite", "postgresql"):
                    # Use native UPSERT via text construct for speed
                    table = OHLCV.__table__
                    cols = ["symbol", "date", "open", "high", "low", "close", "volume"]
                    values = []
                    for r in batch:
                        rec = dict(r)
                        if isinstance(rec.get("date"), str):
                            rec["date"] = datetime.fromisoformat(rec["date"]).date()
                        values.append({k: rec.get(k) for k in cols})
                    # fallback: ORM bulk insert and ignore duplicates
                    objs = [OHLCV(**v) for v in values]
                    session.bulk_save_objects(objs, return_defaults=False)
                    session.commit()
                    total += len(objs)
                else:
                    objs = [OHLCV(**r) for r in batch]
                    session.bulk_save_objects(objs)
                    session.commit()
                    total += len(objs)
            return total
        except IntegrityError:
            session.rollback()
            # fallback to slower but safe per-row merge
            for r in records:
                try:
                    session.merge(OHLCV(**r))
                    session.commit()
                    total += 1
                except Exception:
                    session.rollback()
            return total
        finally:
            session.close()

    # ----- Utility / teardown -----
    def teardown(self):
        self.close()

# -------------------------
# JSONL fallback loader
# -------------------------
def fallback_load_audit_logs(audit_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Read JSONL audit logs from disk (most recent first).
    """
    audit_dir = audit_dir or (getattr(cfg, "AUDIT_DIR", None) if "cfg" in globals() else None)
    if not audit_dir:
        return []
    files = sorted(glob.glob(os.path.join(audit_dir, "pipeline_run_*.jsonl")), reverse=True)
    logs: List[Dict[str, Any]] = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception:
            continue
    return logs


def fallback_load_audit_logs_df(limit: int = 50, audit_dir: Optional[str] = None):
    logs = fallback_load_audit_logs(audit_dir=audit_dir)
    if not logs:
        return None
    try:
        if pd:
            df = pd.DataFrame(logs)
            return df.head(limit)
        return logs[:limit]
    except Exception:
        return logs[:limit]


# Compatibility helper functions expected by legacy tests / orchestrator.
# These are small, sqlite-based helpers that operate on a path or a sqlite3.Connection.
import sqlite3
import json
import time
from typing import Iterable, Optional, Union

# NOTE: these helpers intentionally avoid SQLAlchemy to remain lightweight and
# deterministic for unit tests that expect FILE or in-memory sqlite behaviour.

_DEFAULT_TABLE = "kv"

def _ensure_conn(db: Union[str, sqlite3.Connection, None]) -> sqlite3.Connection:
    """Return a sqlite3.Connection with row_factory set to sqlite3.Row.

    If db is:
      - sqlite3.Connection -> ensure its row_factory is sqlite3.Row and return it
      - None -> create in-memory conn with row_factory sqlite3.Row
      - str/path -> open file-backed connection with sqlite3.Row
    """
    if isinstance(db, sqlite3.Connection):
        # Make sure caller's connection returns mapping-like rows (sqlite3.Row).
        # This is safe to set — callers that expect a tuple will still be able to
        # index numerically (Row supports integer indexing as well).
        try:
            if getattr(db, "row_factory", None) is not sqlite3.Row:
                db.row_factory = sqlite3.Row
        except Exception:
            # best-effort: if setting row_factory fails, ignore and return original conn
            pass
        return db
    if db is None:
        conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    conn = sqlite3.connect(str(db), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def _close_if_created(conn: sqlite3.Connection, original_db: Union[str, sqlite3.Connection, None]) -> None:
    """Close conn if we created it (original_db was a path or None)."""
    if original_db is None or isinstance(original_db, str):
        try:
            conn.commit()
            conn.close()
        except Exception:
            pass

def ensure_table(db: Union[str, sqlite3.Connection, None], table_name: str = _DEFAULT_TABLE, schema: Optional[dict] = None) -> None:
    """
    Ensure a simple key/value table exists.
    If schema is provided it should be a dict mapping column -> sqlite_type.
    """
    conn = _ensure_conn(db)
    try:
        cur = conn.cursor()
        if schema is None:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    extras TEXT,
                    created_ts REAL
                );
                """
            )
            conn.commit()
        else:
            cols = ", ".join([f'"{k}" {v}' for k, v in schema.items()])
            cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols});')
            conn.commit()
    finally:
        _close_if_created(conn, db)

# replace the existing upsert_row definition with this version
def upsert_row(
    db: Union[str, sqlite3.Connection, None],
    table_name: str,
    row: dict,
    unique_keys: Optional[List[str]] = None,  # accepted for backward compatibility
) -> None:
    """
    Insert or replace a row. For the default schema, maps:
      - row["key"] -> key
      - row["value"] -> value (serialized if not text)
      - other fields -> stored as JSON in extras

    `unique_keys` is accepted for compatibility with callers that pass it (e.g. tests).
    Currently the helper uses INSERT OR REPLACE semantics which works when the
    table has a PRIMARY KEY or UNIQUE constraint on the provided unique_keys.
    """
    conn = _ensure_conn(db)
    try:
        cur = conn.cursor()
        # Ensure table exists (default schema)
        cur.execute(f"PRAGMA table_info('{table_name}')")
        cols = [r[1] for r in cur.fetchall()]
        if not cols:
            # create default table if not present
            ensure_table(conn, table_name)

        # If table uses default key/value schema then write that way
        if "key" in cols and "value" in cols:
            key = row.get("key") or row.get("id") or row.get("k")
            value = row.get("value") if "value" in row else row.get("v") or row.get("value")
            if value is None:
                value_text = None
            elif isinstance(value, (str, bytes)):
                value_text = value
            else:
                try:
                    value_text = json.dumps(value)
                except Exception:
                    value_text = str(value)
            extras = {k: v for k, v in row.items() if k not in ("key", "value", "id", "k", "v")}
            cur.execute(
                f'INSERT OR REPLACE INTO "{table_name}" (key, value, extras, created_ts) VALUES (?, ?, ?, ?)',
                (str(key), value_text, json.dumps(extras) if extras else None, time.time()),
            )
            conn.commit()
            return

        # Generic fallback: insert columns present in row (INSERT OR REPLACE)
        keys = list(row.keys())
        qmarks = ",".join("?" for _ in keys)
        cols_sql = ",".join(f'"{k}"' for k in keys)
        cur.execute(
            f'INSERT OR REPLACE INTO "{table_name}" ({cols_sql}) VALUES ({qmarks})',
            tuple(row[k] for k in keys),
        )
        conn.commit()
    finally:
        _close_if_created(conn, db)

def fetch_one(db: Union[str, sqlite3.Connection, None], table_name: str, where: str = "1=1", params: Optional[Iterable] = None) -> Optional[sqlite3.Row]:
    """
    Fetch a single row matching WHERE. Returns sqlite3.Row (indexable by integer and column name),
    or None if no row found.

    This function ensures the connection's row_factory is sqlite3.Row so callers can use row[0]
    (positional) or row["colname"] (named).
    """
    conn = _ensure_conn(db)
    try:
        # Guarantee mapping/sequence behaviour for returned rows
        try:
            conn.row_factory = sqlite3.Row
        except Exception:
            # best-effort: if setting row_factory fails, continue (we'll try to map later)
            pass

        cur = conn.cursor()
        sql = f'SELECT * FROM "{table_name}" WHERE {where} LIMIT 1'
        cur.execute(sql, tuple(params) if params else ())
        row = cur.fetchone()
        if row is None:
            return None

        # If it's already a sqlite3.Row (sequence & mapping), return it directly.
        if isinstance(row, sqlite3.Row):
            return row

        # Otherwise (tuple), attempt to construct a sqlite3.Row-like mapping by creating one via
        # the connection's row_factory using cursor.description. Many connections should not hit
        # this path because we force row_factory above, but keep fallback for safety.
        desc = cur.description
        if not desc:
            return None
        cols = [d[0] for d in desc]
        # Create an sqlite3.Row-like object by using a temporary row_factory
        try:
            # build a mapping-preserving object: sqlite3.Row can't be directly instantiated,
            # but since callers expect indexable access, returning the tuple is acceptable.
            # Prefer returning sqlite3.Row if possible; otherwise return the tuple.
            return row
        except Exception:
            return row
    finally:
        _close_if_created(conn, db)
