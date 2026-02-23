from __future__ import annotations

import hashlib
from typing import Any, Dict

from core.dashboard_read.canonical.serializer import canonicalize_snapshot


def compute_snapshot_fingerprint(snapshot: Any) -> str:
    """
    Compute the ONLY valid snapshot fingerprint.

    fingerprint = SHA256(canonical_semantic_snapshot_bytes)

    Rules:
    - Deterministic
    - Ignores snapshot_id, created_at, schema_version
    - Ignores existing fingerprint & payload_hash
    - Survives serialization / deserialization
    """

    if not hasattr(snapshot, "_fingerprint_payload"):
        raise TypeError(
            "Fingerprint must be computed from SystemSnapshot semantic payload"
        )

    semantic_payload: Dict[str, Any] = snapshot._fingerprint_payload()

    canonical_bytes = canonicalize_snapshot(semantic_payload)
    return hashlib.sha256(canonical_bytes).hexdigest()