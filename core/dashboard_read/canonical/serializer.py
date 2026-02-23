from __future__ import annotations

import json
from typing import Any, Dict

from core.dashboard_read.canonical.errors import CanonicalizationError

# =============================================================================
# CANONICAL SERIALIZATION — SINGLE SOURCE OF TRUTH
# =============================================================================
#
# Guarantees:
# - Deterministic
# - Semantic-only
# - Explicitly validated
# - Bit-flip detectable
#
# This module is the ONLY allowed input to:
# - fingerprinting
# - snapshot hashing
# - evidence chain sealing
# =============================================================================

_CANONICAL_SCHEMA_VERSION = 1

_CANONICAL_JSON_KWARGS = dict(
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
)


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------

def _validate(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise CanonicalizationError(
                    f"Non-string key at {path}: {k!r}"
                )
            _validate(v, f"{path}.{k}")
        return

    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _validate(v, f"{path}[{i}]")
        return

    if isinstance(value, (str, int, float, bool)) or value is None:
        return

    raise CanonicalizationError(
        f"Unsupported type at {path}: {type(value).__name__}"
    )

# ---------------------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------------------

def _strip_non_semantic_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: v
        for k, v in meta.items()
        if k not in {
            "schema_version",
            "snapshot_id",
            "payload_hash",
        }
    }


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(value[k]) for k in value}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    return value

# ---------------------------------------------------------------------
# CANONICAL PAYLOAD
# ---------------------------------------------------------------------

def canonical_snapshot_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise CanonicalizationError("Snapshot must be a dict")

    _validate(snapshot)

    snapshot = dict(snapshot)

    meta = snapshot.get("meta", {})
    canonical_meta = _strip_non_semantic_meta(meta)

    semantic: Dict[str, Any] = {
        "_canonical_schema_version": _CANONICAL_SCHEMA_VERSION,
        "meta": _normalize(canonical_meta),
    }

    for key, value in snapshot.items():
        if key == "meta":
            continue
        semantic[key] = _normalize(value)

    return semantic


# ---------------------------------------------------------------------
# BYTE FORM
# ---------------------------------------------------------------------

def snapshot_to_canonical_bytes(snapshot: Dict[str, Any]) -> bytes:
    semantic_payload = canonical_snapshot_payload(snapshot)

    return json.dumps(
        semantic_payload,
        **_CANONICAL_JSON_KWARGS,
    ).encode("utf-8")


# ---------------------------------------------------------------------
# PUBLIC API (TEST CONTRACT)
# ---------------------------------------------------------------------

def canonicalize_snapshot(snapshot: Dict[str, Any]) -> bytes:
    return snapshot_to_canonical_bytes(snapshot)