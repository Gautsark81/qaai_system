import asyncio
from ingestion.market_ingestor import MarketIngestor
from data.tick_store import TickStore

async def run():
    out_q = asyncio.Queue()
    ingestor = MarketIngestor(feed_url="wss://fake", api_key="x", out_queue=out_q)
    ts = TickStore(db_path="live_ticks.db")
    async def consumer():
        while True:
            t = await out_q.get()
            await ts.write_tick(t)
    await ingestor.start()
    c = asyncio.create_task(consumer())
    # run for some time, then stop
    await asyncio.sleep(5)
    await ingestor.stop()
    c.cancel()
    ts.close()

if __name__ == "__main__":
    asyncio.run(run())
