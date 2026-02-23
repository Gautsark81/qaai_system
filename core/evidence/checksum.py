# core/evidence/checksum.py

import hashlib
from datetime import datetime
from typing import Any, Iterable, Tuple


def _normalize(value: Any) -> str:
    """
    Normalize values into a deterministic string form.
    """

    if value is None:
        return "∅"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, float):
        # Fixed precision for determinism
        return f"{value:.10f}"

    if isinstance(value, (int, str)):
        return str(value)

    if isinstance(value, datetime):
        # Always UTC ISO format
        return value.isoformat()

    if isinstance(value, tuple):
        return "[" + ",".join(_normalize(v) for v in value) + "]"

    raise TypeError(f"Unsupported type for checksum: {type(value)}")


def compute_checksum(
    *,
    fields: Iterable[Tuple[str, Any]],
    algorithm: str = "sha256",
) -> str:
    """
    Compute a deterministic checksum for ordered (key, value) fields.

    This function is PURE:
    - No side effects
    - No IO
    - No global state
    """

    hasher = hashlib.new(algorithm)

    for key, value in fields:
        hasher.update(key.encode("utf-8"))
        hasher.update(b"=")
        hasher.update(_normalize(value).encode("utf-8"))
        hasher.update(b"|")

    return hasher.hexdigest()
