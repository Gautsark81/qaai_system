# core/governance/integrity/governance_snapshot_hash_engine.py

import hashlib

from core.governance.integrity.governance_snapshot_serializer import (
    GovernanceSnapshotSerializer,
)
from core.governance.reconstruction import GovernanceState


class GovernanceSnapshotHashEngine:
    """
    Phase C6.2

    Deterministic SHA-256 hashing over canonical snapshot.
    """

    @staticmethod
    def compute_hash(state: GovernanceState) -> str:
        canonical = GovernanceSnapshotSerializer.serialize(state)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return digest