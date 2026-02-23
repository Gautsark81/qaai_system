# tests/unit/test_db_utils.py
import sqlite3
import tempfile
import os
from db.db_utils import ensure_table, upsert_row, fetch_one

def test_upsert_and_fetch():
    conn = sqlite3.connect(":memory:")
    table = "positions"
    ensure_table(conn, table, {"symbol": "TEXT PRIMARY KEY", "qty": "REAL", "avg_price": "REAL"})
    upsert_row(conn, table, {"symbol": "NSE:ABC", "qty": 1.0, "avg_price": 100.0}, unique_keys=["symbol"])
    row = fetch_one(conn, table, "symbol=?", ("NSE:ABC",))
    assert row is not None
    assert row[0] == "NSE:ABC"
    # update existing
    upsert_row(conn, table, {"symbol": "NSE:ABC", "qty": 2.0, "avg_price": 101.0}, unique_keys=["symbol"])
    row2 = fetch_one(conn, table, "symbol=?", ("NSE:ABC",))
    assert row2[1] == 2.0
    assert row2[2] == 101.0
