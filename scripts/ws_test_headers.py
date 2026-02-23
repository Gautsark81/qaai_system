# ws_test_headers.py
import websocket
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

url = "wss://api-feed.dhan.co/v1/live"
cid = os.getenv("DHAN_CLIENT_ID")
token = os.getenv("DHAN_ACCESS_TOKEN")
# try list-of-strings
headers_list = [
    f"client-id: {cid}",
    f"access-token: {token}",
    "Origin: https://api.dhan.co",
    "User-Agent: qaai-system/1.0",
    "Host: api-feed.dhan.co",
]
print("Trying header list:", headers_list[:3])
try:
    ws = websocket.create_connection(
        url, header=headers_list, sslopt={"cert_reqs": ssl.CERT_REQUIRED}, timeout=5
    )
    print("create_connection succeeded with header list")
    ws.close()
except Exception as e:
    print("create_connection failed (list):", type(e).__name__, e)

# try dict form (some versions accept this)
headers_dict = {
    "client-id": cid,
    "access-token": token,
    "Origin": "https://api.dhan.co",
    "User-Agent": "qaai-system/1.0",
    "Host": "api-feed.dhan.co",
}
print(
    "Trying header dict:",
    {
        k: (v[:6] + "...")
        for k, v in headers_dict.items()
        if k in ("client-id", "access-token")
    },
)
try:
    ws = websocket.create_connection(
        url, header=headers_dict, sslopt={"cert_reqs": ssl.CERT_REQUIRED}, timeout=5
    )
    print("create_connection succeeded with header dict")
    ws.close()
except Exception as e:
    print("create_connection failed (dict):", type(e).__name__, e)
