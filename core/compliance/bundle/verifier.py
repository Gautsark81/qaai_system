# core/compliance/bundle/verifier.py
import hashlib
from typing import Any, Dict
from core.compliance.bundle.bundle import ImmutableAuditBundle, _canonical_bytes


class AuditBundleVerifier:
    """
    Verifies integrity of an immutable audit bundle.
    """

    def verify(self, *, bundle: ImmutableAuditBundle) -> bool:
        canonical = _canonical_bytes(bundle.payload)
        digest = hashlib.sha256(canonical).hexdigest()
        return digest == bundle.bundle_hash
