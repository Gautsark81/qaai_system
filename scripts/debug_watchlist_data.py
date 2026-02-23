from infra.db_client import DBClient

db = DBClient()
watchlist = db.fetch_watchlist()
print("✅ Watchlist symbols:", watchlist)

for symbol in watchlist:
    df = db.fetch_ohlcv(symbol, days=60)
    print(f"\n📈 OHLCV for {symbol}:\n{df.tail()}")
    print(f"Shape: {df.shape}")
