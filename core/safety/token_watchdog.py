# core/safety/token_watchdog.py
from __future__ import annotations

import base64
import json
import os
import time
from typing import Dict, Optional

from datetime import datetime, timezone

# The watchdog focuses on detecting JWT 'exp' claim and returning seconds left.
# It does NOT automatically refresh tokens — your operator process / orchestrator
# should call refresh procedures. The watchdog will raise or return stale status.

def _decode_jwt_no_verify(token: str) -> Optional[Dict]:
    """
    Lightweight decode of JWT payload without signature verification.
    Returns payload dict or None on failure.
    """
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        # fix padding
        padding = "=" * (-len(payload_b64) % 4)
        payload_b64 += padding
        data = base64.urlsafe_b64decode(payload_b64.encode())
        return json.loads(data.decode())
    except Exception:
        return None


def token_expiry_seconds(token: str) -> Optional[int]:
    payload = _decode_jwt_no_verify(token)
    if not payload:
        return None
    exp = payload.get("exp")
    if exp is None:
        return None
    now = int(datetime.now(timezone.utc).timestamp())
    return int(exp) - now


def check_env_dhan_token() -> Dict[str, Optional[int]]:
    """
    Inspect environment for DHAN token variables and return seconds to expiry.
    Returns { 'token_env_name': seconds_left or None }
    """
    results = {}
    for key in ("DHAN_ACCESS_TOKEN", "DHAN_TOKEN", "ACCESS_TOKEN"):
        token = os.getenv(key)
        if token:
            results[key] = token_expiry_seconds(token)
    return results


def ensure_token_not_expired(*, grace_seconds: int = 60) -> None:
    """
    Raise RuntimeError if the primary DHAN_ACCESS_TOKEN has expired (or
    will expire within grace_seconds). Intended to be used as a soft-block
    check in watchdog and operator flows.
    """
    token = os.getenv("DHAN_ACCESS_TOKEN")
    if not token:
        # No token set — treat as expired for safety
        raise RuntimeError("DHAN_ACCESS_TOKEN missing")
    secs = token_expiry_seconds(token)
    if secs is None:
        # unknown format — be conservative and require operator check
        raise RuntimeError("DHAN_ACCESS_TOKEN has no expiry information")
    if secs <= grace_seconds:
        raise RuntimeError(f"DHAN_ACCESS_TOKEN expires in {secs} seconds (<= {grace_seconds})")
