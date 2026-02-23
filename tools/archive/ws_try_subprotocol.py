# ws_try_subprotocol.py
import websocket
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

url = "wss://api-feed.dhan.co/v1/live"
client = os.getenv("DHAN_CLIENT_ID", "").strip()
token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
subproto = f"clientid.{client};token.{token}"

try:
    print("Trying subprotocol:", subproto[:80])
    ws = websocket.create_connection(
        url, subprotocols=[subproto], sslopt={"cert_reqs": ssl.CERT_REQUIRED}, timeout=8
    )
    print("create_connection succeeded with subprotocol")
    ws.close()
except Exception as e:
    print("create_connection failed (subprotocol):", type(e).__name__, e)
