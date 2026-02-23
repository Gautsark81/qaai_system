from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class CapitalThrottleLedgerEntry:
    """
    Append-only ledger entry for capital throttle decisions.

    Phase 12.4 — Capital Throttle Ledger
    Phase 12.5 — Governance cross-linking
    """

    strategy_id: str
    throttle_factor: float
    reason: Optional[str]
    decision_checksum: Optional[str]
    governance_id: Optional[str]
    timestamp: datetime

    def __init__(
        self,
        strategy_id: str,
        *,
        throttle_level: Optional[float] = None,
        throttle_factor: Optional[float] = None,
        reason: Optional[str] = None,
        decision_checksum: Optional[str] = None,
        governance_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        if throttle_factor is None and throttle_level is None:
            raise TypeError("Either throttle_factor or throttle_level must be provided")

        object.__setattr__(self, "strategy_id", strategy_id)
        object.__setattr__(
            self,
            "throttle_factor",
            throttle_factor if throttle_factor is not None else throttle_level,
        )
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "decision_checksum", decision_checksum)
        object.__setattr__(self, "governance_id", governance_id)
        object.__setattr__(
            self,
            "timestamp",
            timestamp if timestamp is not None else datetime.now(timezone.utc),
        )
