# Path: tools/decode_token.py
"""
Decode DHAN JWT payload (no signature verification) to inspect claims like exp, clientId, etc.
Run: python tools/decode_token.py
"""
import os
import base64
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

TOK = os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("DHAN_ACCESS_TOKEN_LIVE") or os.getenv("DHAN_ACCESS_TOKEN_PAPER")

def safe_b64decode(s: str) -> bytes:
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * ((4 - len(s) % 4) % 4)
    return base64.b64decode(s)

def decode_jwt_noverify(token: str):
    try:
        parts = token.split(".")
        if len(parts) < 2:
            print("Token does not look like a JWT (missing parts).")
            return None
        payload_b64 = parts[1]
        raw = safe_b64decode(payload_b64)
        return json.loads(raw)
    except Exception as e:
        print("Failed to decode token payload:", e)
        return None

def format_ts(ts):
    try:
        return datetime.datetime.utcfromtimestamp(int(ts)).isoformat() + "Z"
    except Exception:
        return str(ts)

def main():
    if not TOK:
        print("No DHAN token found in environment. Check your .env or env vars (DHAN_ACCESS_TOKEN / DHAN_ACCESS_TOKEN_LIVE).")
        return
    print("Token preview (masked):", TOK[:8] + "..." + TOK[-8:])
    claims = decode_jwt_noverify(TOK)
    if not claims:
        print("Unable to decode claims. Token may be truncated or not a JWT.")
        return
    print("Decoded claims:")
    for k, v in claims.items():
        if k in ("exp", "iat", "nbf"):
            print(f"  {k}: {v} -> {format_ts(v)}")
        else:
            print(f"  {k}: {v}")
    # heuristic
    if "exp" in claims:
        exp = int(claims["exp"])
        now = int(datetime.datetime.utcnow().timestamp())
        if exp < now:
            print("\nWARNING: token appears EXPIRED (exp < now).")
        else:
            print("\nToken expiry looks OK.")
    # presence of dhan client id in token (if present)
    for guess in ("dhanClientId", "dhanClientID", "dhanClientId", "dhan_client_id", "dhanClient"):
        if guess in claims:
            print("Found claim", guess, "=", claims[guess])

if __name__ == "__main__":
    main()
