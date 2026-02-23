from __future__ import annotations

import hashlib
import json
from typing import Dict, Any


def make_idempotency_key(order: Dict[str, Any]) -> str:
    """
    Stable idempotency key for an order dict.
    Order content → deterministic hash.
    """
    payload = json.dumps(order, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
