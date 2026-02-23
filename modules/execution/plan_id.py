# modules/execution/plan_id.py

import hashlib
import json
from typing import Mapping


def make_plan_id(payload: Mapping[str, object]) -> str:
    """
    Deterministic, stable across restarts.
    """
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
