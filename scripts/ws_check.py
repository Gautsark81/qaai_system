# scripts/ws_test.py
import asyncio
import os

try:
    import websockets
except Exception:
    raise SystemExit("Install websockets: pip install websockets")


async def test(url):
    try:
        print("Trying to connect to", url)
        async with websockets.connect(url, ping_interval=10, ping_timeout=5) as ws:
            print("Connected OK — server responded to handshake")
            # immediately close
    except Exception as e:
        print("Connection error:", type(e).__name__, str(e))


if __name__ == "__main__":
    url = os.getenv("DHAN_WS_URL", "wss://api-feed.dhan.co/v1/live")
    asyncio.run(test(url))
