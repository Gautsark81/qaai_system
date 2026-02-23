from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class CapitalScalingLedgerEntry:
    """
    Append-only ledger entry for capital scaling decisions.

    Phase 12.2 — Capital Scaling Ledger
    Phase 12.5 — Governance cross-linking
    """

    # Identity
    strategy_id: str

    # Capital change
    previous_capital: float
    new_capital: float
    scale_factor: float

    # Phase 12.2 — decision provenance (optional, immutable)
    decision_reason: Optional[str] = None
    decision_checksum: Optional[str] = None

    # Phase 12.5 — governance chain (optional for backward compatibility)
    governance_id: Optional[str] = None

    # Temporal ordering
    timestamp: datetime = datetime.now(timezone.utc)
