# core/compliance/export/hasher.py

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


# ---------------------------------------------------------------------
# Canonical JSON Utilities
# ---------------------------------------------------------------------

def _canonicalize(value: Any) -> Any:
    """
    Convert arbitrary nested structures into a canonical,
    JSON-serializable form with deterministic ordering.

    Rules:
    - dicts → sorted by key
    - lists → preserved order (caller must ensure determinism)
    - primitives → unchanged
    """

    if isinstance(value, dict):
        return {
            key: _canonicalize(value[key])
            for key in sorted(value.keys())
        }

    if isinstance(value, list):
        return [_canonicalize(v) for v in value]

    return value


def _canonical_json(payload: Dict[str, Any]) -> str:
    """
    Produce a canonical JSON string suitable for hashing.

    Guarantees:
    - Stable key ordering
    - No whitespace variance
    - UTF-8 encoded
    """

    canonical_payload = _canonicalize(payload)

    return json.dumps(
        canonical_payload,
        separators=(",", ":"),
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------
# Canonical Hasher
# ---------------------------------------------------------------------

class CanonicalSHA256Hasher:
    """
    Deterministic SHA-256 hasher for regulator exports.

    This is the ONLY approved hashing mechanism for Phase 28.4.
    """

    algorithm = "SHA256"

    def hash(self, payload: Dict[str, Any]) -> str:
        """
        Compute a SHA-256 hex digest over canonical JSON.

        Input:
        - payload: dict already filtered to allowed fields

        Output:
        - hex digest string
        """

        canonical = _canonical_json(payload)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return digest
