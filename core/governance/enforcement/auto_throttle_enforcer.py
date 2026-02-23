from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from core.governance.reconstruction import (
    GovernanceState,
    CapitalExposureDriftResult,
)

from core.governance.capital_usage.capital_throttle_ledger import (
    CapitalThrottleLedger,
    CapitalThrottleLedgerEntry,
)


@dataclass(frozen=True)
class AutoThrottleResult:
    enforced: bool
    throttle_level: Optional[float]
    reason: Optional[str]
    governance_id: str
    timestamp: Optional[datetime]


class AutoThrottleEnforcer:
    """
    Phase C5.4

    Automatically emits throttle events when over-allocation drift is detected.
    Immutable. Deterministic. Governance-chain preserving.
    """

    DEFAULT_THROTTLE_LEVEL = 0.75

    def enforce(
        self,
        *,
        governance_state: GovernanceState,
        drift_result: CapitalExposureDriftResult,
        throttle_ledger: CapitalThrottleLedger,
        throttle_level: Optional[float] = None,
    ) -> AutoThrottleResult:

        # Only enforce on HARD over-allocation
        if not drift_result.over_allocated:
            return AutoThrottleResult(
                enforced=False,
                throttle_level=None,
                reason=None,
                governance_id=governance_state.governance_id,
                timestamp=None,
            )

        level = throttle_level or self.DEFAULT_THROTTLE_LEVEL
        ts = datetime.now(timezone.utc)

        checksum = self._build_checksum(
            governance_id=governance_state.governance_id,
            strategy_id=governance_state.strategy_id,
            throttle_level=level,
            timestamp=ts,
        )

        entry = CapitalThrottleLedgerEntry(
            strategy_id=governance_state.strategy_id,
            throttle_level=level,
            reason="AUTO_THROTTLE_OVER_ALLOCATION",
            decision_checksum=checksum,
            governance_id=governance_state.governance_id,
            timestamp=ts,
        )

        throttle_ledger.append(entry)

        return AutoThrottleResult(
            enforced=True,
            throttle_level=level,
            reason="AUTO_THROTTLE_OVER_ALLOCATION",
            governance_id=governance_state.governance_id,
            timestamp=ts,
        )

    def _build_checksum(
        self,
        *,
        governance_id: str,
        strategy_id: str,
        throttle_level: float,
        timestamp: datetime,
    ) -> str:

        payload = f"{governance_id}|{strategy_id}|{throttle_level}|{timestamp.isoformat()}"
        return hashlib.sha256(payload.encode()).hexdigest()