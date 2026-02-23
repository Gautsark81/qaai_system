# ws_try_queryparam.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

base = "https://api-feed.dhan.co/v1/live"
client = os.getenv("DHAN_CLIENT_ID", "").strip()
token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
url = f"{base}?client_id={client}&access_token={token}"

hdrs = {"Origin": "https://api.dhan.co", "User-Agent": "qaai-system/1.0"}
try:
    r = requests.get(url, headers=hdrs, timeout=10)
    print("URL test ->", r.status_code, r.text[:300])
except Exception as e:
    print("Error:", type(e).__name__, e)
