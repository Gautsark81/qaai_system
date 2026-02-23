from __future__ import annotations

import hashlib
import json
from typing import Any


def fingerprint_transition(from_state: Any, to_state: Any) -> str:
    """
    Deterministic fingerprint for a lifecycle transition.
    """
    payload = json.dumps(
        {
            "from": from_state.value,
            "to": to_state.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
