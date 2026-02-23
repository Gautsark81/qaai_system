# core/compliance/notary/verifier.py
import hashlib
from typing import Any, Dict
from core.compliance.notary.snapshot import SnapshotSeal, _canonical_bytes


class SnapshotVerifier:
    """
    Verifies snapshot integrity against a seal.
    """

    def verify(self, *, snapshot: Dict[str, Any], seal: SnapshotSeal) -> bool:
        canonical = _canonical_bytes(snapshot)
        digest = hashlib.sha256(canonical).hexdigest()
        return digest == seal.digest
