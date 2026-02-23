#!/usr/bin/env python3
"""
Async ingest worker scaffold (aiosqlite). Adapt to your websocket feed.
"""
import asyncio
import aiosqlite
from datetime import datetime
import os

DB_PATH = os.path.join("db", "ticks.db")


async def write_tick(db, ts, symbol, price, volume, bid, ask):
    await db.execute(
        "INSERT OR REPLACE INTO ticks (ts, symbol, price, volume, bid, ask) VALUES (?, ?, ?, ?, ?, ?)",
        (ts, symbol, price, volume, bid, ask),
    )


async def fake_feed(queue: asyncio.Queue):
    # fake feed: pushes a tick every second
    import random

    symbols = ["AAPL", "MSFT"]
    while True:
        ts = datetime.utcnow().isoformat()
        s = random.choice(symbols)
        p = 100 + random.random()
        v = random.randint(1, 100)
        b = p - 0.01
        a = p + 0.01
        await queue.put((ts, s, p, v, b, a))
        await asyncio.sleep(1)


async def worker(queue: asyncio.Queue):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        while True:
            ts, s, p, v, b, a = await queue.get()
            await write_tick(db, ts, s, p, v, b, a)
            await db.commit()
            queue.task_done()


async def main():
    q = asyncio.Queue()
    w = asyncio.create_task(worker(q))
    f = asyncio.create_task(fake_feed(q))
    await asyncio.gather(f, w)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting")
