# scripts/ingest_dhan_ticks.py
import asyncio
import aiosqlite
from datetime import datetime
from providers.dhan_client import DhanClient

TICKS_DB = "db/ticks.db"


async def store_tick(db, ts, symbol, price, volume):
    await db.execute(
        """
        INSERT OR REPLACE INTO ticks (ts, symbol, price, volume, bid, ask)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ts, symbol, price, volume, None, None),
    )
    await db.commit()


async def main():
    client = DhanClient()
    symbols = ["AAPL", "MSFT"]  # ⚠ replace with your NSE symbols

    async with aiosqlite.connect(TICKS_DB) as db:
        db.row_factory = aiosqlite.Row

        def on_tick(data):
            ts = datetime.utcnow().isoformat()
            for tick in data["data"]:
                symbol = tick["securityId"].split(":")[1]
                price = tick["lastTradedPrice"]
                volume = tick.get("lastTradeQty", 0)
                asyncio.create_task(store_tick(db, ts, symbol, price, volume))

        client.subscribe_feed(symbols, on_tick)

        print("Streaming ticks from DhanHQ…")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
