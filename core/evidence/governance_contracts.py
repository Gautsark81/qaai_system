# core/evidence/governance_contracts.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SignedGovernanceEvidence:
    """
    Cryptographically signed evidence of a governance decision.

    This does NOT execute anything.
    This does NOT approve anything.
    This PROVES that a human decision occurred.
    """

    # Identity
    decision_id: str                 # Derived from checksum
    governance_type: str             # PAPER | LIVE | CANARY
    strategy_id: str

    # Decision
    status: str                      # APPROVED | REJECTED
    reasons: tuple[str, ...]         # Immutable

    # Actor
    reviewer: str                    # Human identifier
    reviewer_fingerprint: str        # Public key hash / ID

    # Time
    decided_at: datetime             # UTC

    # Integrity
    decision_checksum: str           # From DecisionEvidence
    signature: str                   # Cryptographic signature
    algorithm: str                   # e.g. HMAC-SHA256
