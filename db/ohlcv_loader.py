# qaai_system/db/ohlcv_loader.py
"""
CLI helper: insert OHLCV CSV into DB.
Usage (from repo parent dir):
  python -m qaai_system.db.ohlcv_loader --csv qaai_system/data/ohlcv/AAPL.csv --symbol AAPL --db sqlite:///qaai.db
"""
from __future__ import annotations
import argparse
import os
import pandas as pd

# robust import: allow running from inside qaai_system or from parent dir
try:
    from qaai_system.db.db_utils import DBManager
except Exception:
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
    from qaai_system.db.db_utils import DBManager  # try again


def insert_from_csv(db_url: str, csv_path: str, symbol: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["date"], infer_datetime_format=True)
    # normalize columns to lowercase
    df.columns = [c.lower() for c in df.columns]

    required = {"date", "open", "high", "low", "close", "volume"}
    if not required.issubset(set(df.columns)):
        raise ValueError(
            f"CSV missing required columns. Need: {required}. Got: {list(df.columns)}"
        )

    records = []
    for _, r in df.iterrows():
        records.append(
            {
                "symbol": symbol,
                "date": (
                    r["date"].date()
                    if hasattr(r["date"], "date")
                    else pd.to_datetime(r["date"]).date()
                ),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
            }
        )

    db = DBManager(db_url=db_url)
    db.insert_ohlcv_batch(records)
    print(f"[OK] Inserted {len(records)} rows for {symbol} into {db_url}")


def build_argparser():
    p = argparse.ArgumentParser(description="Insert OHLCV CSV into DB")
    p.add_argument(
        "--csv",
        required=True,
        help="Path to OHLCV CSV (date,open,high,low,close,volume)",
    )
    p.add_argument("--symbol", required=True, help="Ticker symbol")
    p.add_argument(
        "--db", default="sqlite:///qaai.db", help="DB URL (default: sqlite:///qaai.db)"
    )
    return p


def main(argv=None):
    parser = build_argparser()
    args = parser.parse_args(argv)
    insert_from_csv(db_url=args.db, csv_path=args.csv, symbol=args.symbol)


if __name__ == "__main__":
    main()
