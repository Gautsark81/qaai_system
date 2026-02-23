#!/usr/bin/env python3
"""
Backfill OHLCV using yfinance for a list of symbols.
Writes into db/ohlcv.db table `ohlcv`.
"""
from infra.sqlite_client import SQLiteClient
import yfinance as yf
import pandas as pd

DB = SQLiteClient("db/ohlcv.db")


def insert_rows(symbol: str, timeframe: str, df: pd.DataFrame):
    q = "INSERT OR REPLACE INTO ohlcv (ts, symbol, timeframe, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    for idx, row in df.iterrows():
        ts = idx.to_pydatetime().isoformat()
        DB.execute(
            q,
            (
                ts,
                symbol,
                timeframe,
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                float(row["Volume"]),
            ),
        )


def fetch_history(symbol: str, period: str = "60d", interval: str = "1m"):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval, auto_adjust=False)
    return hist


if __name__ == "__main__":
    symbols = ["AAPL", "MSFT"]
    for s in symbols:
        print("Fetching", s)
        df = fetch_history(s, period="30d", interval="1m")
        if df is None or df.empty:
            print("No data for", s)
            continue
        insert_rows(s, "1m", df)
        print("Inserted", len(df), "rows for", s)
