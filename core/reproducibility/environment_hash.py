# core/reproducibility/environment_hash.py

from __future__ import annotations

import hashlib
from core.reproducibility.environment_snapshot import (
    EnvironmentSnapshot,
)


class EnvironmentHasher:
    """
    Deterministic SHA256 hash over canonical environment snapshot.
    """

    @staticmethod
    def hash(snapshot: EnvironmentSnapshot) -> str:
        canonical_json = snapshot.to_canonical_json()
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()