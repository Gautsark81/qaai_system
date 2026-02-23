# ws_test_async.py
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()
import websockets


async def main():
    url = "wss://api-feed.dhan.co/v1/live"
    extra_headers = [
        ("client-id", os.getenv("DHAN_CLIENT_ID", "")),
        ("access-token", os.getenv("DHAN_ACCESS_TOKEN", "")),
        ("origin", "https://api.dhan.co"),
    ]
    try:
        print("Connecting (async) with extra_headers:", extra_headers)
        async with websockets.connect(
            url, extra_headers=extra_headers, ping_interval=20, ping_timeout=10
        ) as ws:
            print("Connected. Sending subscribe...")
            await ws.send(
                json.dumps({"type": "subscribe", "instruments": ["NSE_EQ:RELIANCE.NS"]})
            )
            async for msg in ws:
                print("msg:", msg)
    except Exception as e:
        print("Async connect failed:", type(e).__name__, e)


if __name__ == "__main__":
    asyncio.run(main())
