# ws_try_header_variants.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api-feed.dhan.co/v1/live"
client = os.getenv("DHAN_CLIENT_ID", "").strip()
token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()

variants = [
    {"client-id": client, "access-token": token},
    {"x-client-id": client, "x-access-token": token},
    {"client_id": client, "access_token": token},
    {"clientid": client, "accesstoken": token},
    {"X-CLIENT-ID": client, "ACCESS-TOKEN": token},
]

for i, h in enumerate(variants, 1):
    hdrs = {**h, "Origin": "https://api.dhan.co", "User-Agent": "qaai-system/1.0"}
    try:
        r = requests.get(url, headers=hdrs, timeout=10)
        print(
            f"Variant {i}: headers keys={list(h.keys())} -> status={r.status_code} text={r.text[:120]!r}"
        )
    except Exception as e:
        print("Variant", i, "error:", type(e).__name__, e)
