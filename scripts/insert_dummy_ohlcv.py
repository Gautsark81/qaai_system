# scripts/insert_dummy_ohlcv.py
import pandas as pd
from infra.db_client import DBClient
from datetime import datetime, timedelta

symbols = ["RELIANCE", "TCS", "INFY"]
today = datetime.today()


def generate_dummy_ohlcv(days=60):
    return pd.DataFrame(
        [
            {
                "date": today - timedelta(days=i),
                "open": 100 + i,
                "high": 102 + i,
                "low": 98 + i,
                "close": 100 + i,
                "volume": 300000,
            }
            for i in range(days)
        ]
    )


if __name__ == "__main__":
    db = DBClient()
    for symbol in symbols:
        df = generate_dummy_ohlcv()
        db.insert_ohlcv(df, symbol)
        print(f"Inserted dummy OHLCV for {symbol}")
    db.close()
