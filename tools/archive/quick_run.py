# quick_run.py
import asyncio
from integrations.dhan_live import DhanLiveConnector

async def main():
    conn = DhanLiveConnector(feed_url="wss://dhan_live_ws_url", api_key="YOUR_KEY")
    await conn.start()
    # print 5 messages then stop
    for _ in range(5):
        msg = await conn.messages_queue.get()
        print(msg)
    await conn.stop()

asyncio.run(main())
