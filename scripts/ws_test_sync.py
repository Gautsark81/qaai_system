# scripts/ws_test_sync.py
import os
from websocket import create_connection

url = os.getenv("DHAN_WS_URL", "wss://api-feed.dhan.co/v1/live")
headers = [
    "client-id: " + os.getenv("DHAN_CLIENT_ID", ""),
    "access-token: " + os.getenv("DHAN_ACCESS_TOKEN", ""),
    "Origin: https://api.dhan.co",
]

try:
    print("Trying sync connect...")
    ws = create_connection(url, header=headers, timeout=10)
    print("Connected (sync).")
    ws.close()
except Exception as e:
    print("Sync connect error:", type(e).__name__, e)
