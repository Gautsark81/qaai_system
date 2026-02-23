# test_telegram.py

import requests

TOKEN = "7823832614:AAFbAfCVNHljd_lxYt3QgYLRVF9rbCWCu_Y"
CHAT_ID = 1242579589

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "✅ QAAI Shadow Live test message"
}

r = requests.post(url, json=payload)
print(r.json())
