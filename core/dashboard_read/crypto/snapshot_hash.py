# core/dashboard_read/crypto/snapshot_hash.py

from __future__ import annotations

import hashlib
from typing import Dict, Any

from core.dashboard_read.canonical.serializer import canonicalize_snapshot
from core.dashboard_read.canonical.errors import CanonicalizationError


HASH_ALGORITHM = "sha256"
HASH_ENCODING = "hex"


class SnapshotHashError(Exception):
    """Raised when snapshot hashing fails."""


def compute_snapshot_hash(snapshot: Dict[str, Any]) -> str:
    """
    Compute the cryptographic hash of a snapshot.

    Rules:
    - Hash is computed ONLY from canonical snapshot bytes
    - SHA-256 is used
    - Output is lowercase hex
    """

    try:
        canonical_bytes = canonicalize_snapshot(snapshot)
    except CanonicalizationError as exc:
        raise SnapshotHashError(f"Canonicalization failed: {exc}") from exc

    hasher = hashlib.sha256()
    hasher.update(canonical_bytes)

    return hasher.hexdigest()
