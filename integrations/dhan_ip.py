# integrations/dhan_ip.py
"""
Helper to call Dhan modifyIP endpoint to add a developer/CI IP to allowlist.
DO NOT run in production without authorization.
Docs: see modifyIP API.
"""
import requests
import logging
logger = logging.getLogger(__name__)

DHAN_MODIFY_IP_URL = "https://api.dhan.co/v2/modifyIP"  # check exact URL per docs

def add_ip(api_key: str, ip: str):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"ip": ip, "action": "add"}
    r = requests.post(DHAN_MODIFY_IP_URL, json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
