from infra.sqlite_client import SQLiteClient
from datetime import datetime, timedelta
import random

db = SQLiteClient("db/ohlcv.db")

now = datetime.utcnow()
rows = []

price = 100
for i in range(40):
    ts = (now - timedelta(minutes=40 - i)).isoformat()
    o = price
    h = price + random.uniform(0, 1)
    l = price - random.uniform(0, 1)
    c = price + random.uniform(-0.5, 0.5)
    v = random.uniform(1000, 5000)
    rows.append((ts, "AAPL", o, h, l, c, v, "1m"))
    price = c

q = "INSERT INTO ohlcv (ts, symbol, open, high, low, close, volume, timeframe) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

for r in rows:
    db.execute(q, r)

print("Inserted sample OHLCV candles.")
