from __future__ import annotations

import hashlib
import json
from typing import Any


def _to_stable_dict(obj: Any) -> dict:
    """
    Convert a dataclass or object with __dict__ into
    a JSON-serializable, order-stable dict.
    """
    if obj is None:
        return {}

    if hasattr(obj, "__dict__"):
        data = obj.__dict__
    else:
        raise TypeError(f"Unsupported object type for fingerprinting: {type(obj)}")

    return {
        k: _normalize(v)
        for k, v in sorted(data.items())
        if not k.startswith("_")
    }


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def fingerprint(obj: Any) -> str:
    """
    Compute a deterministic SHA-256 fingerprint for an object.
    """
    stable = _to_stable_dict(obj)
    payload = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
