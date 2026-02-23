import json
import hashlib
from typing import Any
from types import MappingProxyType
from datetime import datetime


_HASH_EXCLUDE_KEYS = {"timestamp"}


def _canonicalize(obj: Any) -> Any:
    """
    Convert object into JSON-serializable,
    deterministic, hash-safe form.
    """
    if isinstance(obj, MappingProxyType):
        return _canonicalize(dict(obj))

    if isinstance(obj, dict):
        return {
            k: _canonicalize(v)
            for k, v in sorted(obj.items())
            if k not in _HASH_EXCLUDE_KEYS
        }

    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]

    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj


def compute_snapshot_hash(snapshot_core: dict) -> str:
    canonical = _canonicalize(snapshot_core)
    payload = json.dumps(
        canonical,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
