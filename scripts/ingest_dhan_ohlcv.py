from providers.dhan_client import DhanClient
from infra.sqlite_client import SQLiteClient
from datetime import datetime

db = SQLiteClient("db/ohlcv.db")


def store_ohlcv(symbol, rows):
    for row in rows:
        ts = datetime.fromtimestamp(row["timestamp"]).isoformat()
        db.execute(
            """
            INSERT OR REPLACE INTO ohlcv
            (ts, symbol, timeframe, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                symbol,
                "1m",
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
            ),
        )


def main():
    client = DhanClient()
    symbols = ["AAPL", "MSFT"]  # replace with your NSE symbols

    for s in symbols:
        resp = client.get_ohlc(s)
        if "data" in resp:
            store_ohlcv(s, resp["data"])

    print("OHLCV ingestion complete.")


if __name__ == "__main__":
    main()
