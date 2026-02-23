from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------
# Immutable Result Model
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class GovernanceChainChecksum:
    governance_id: str
    checksum: str
    created_at: datetime


# ---------------------------------------------------------------------
# Deterministic Checksum Engine
# ---------------------------------------------------------------------


class GovernanceChecksumEngine:
    """
    Phase 2E — Governance Hard Binding

    Produces a deterministic, tamper-evident checksum across:
    - Scaling
    - Throttle
    - Promotion (optional)
    - Governance ID
    - Timestamp

    Guarantees:
    - Deterministic ordering
    - Replay safe
    - Side-effect free
    """

    def compute(
        self,
        *,
        governance_id: str,
        scaling_checksum: Optional[str],
        throttle_checksum: Optional[str],
        promotion_checksum: Optional[str],
        timestamp: datetime,
    ) -> GovernanceChainChecksum:

        if not governance_id:
            raise ValueError("governance_id required")

        payload = "|".join(
            [
                governance_id,
                scaling_checksum or "",
                throttle_checksum or "",
                promotion_checksum or "",
                timestamp.isoformat(),
            ]
        )

        checksum = hashlib.sha256(payload.encode()).hexdigest()

        return GovernanceChainChecksum(
            governance_id=governance_id,
            checksum=checksum,
            created_at=timestamp,
        )