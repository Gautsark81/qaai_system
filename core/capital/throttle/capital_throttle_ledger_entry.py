from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CapitalScalingLedgerEntry:
    """
    Append-only ledger entry for capital scaling decisions.

    Phase 12.2 — Capital Scaling Ledger
    Phase 12.5 — Governance cross-linking
    """

    strategy_id: str
    previous_capital: float
    new_capital: float
    scale_factor: float

    # Phase 12.5 — governance chain
    governance_id: str

    timestamp: datetime = datetime.now(timezone.utc)
