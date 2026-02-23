from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from core.governance.escalation.governance_escalation_engine import EscalationDecision
from core.governance.escalation.governance_strike_ledger import GovernanceStrikeLedger


@dataclass(frozen=True)
class GovernanceBreachResult:
    governance_id: str
    breached: bool
    reason: Optional[str]
    timestamp: datetime


class GovernanceBreachSentinel:

    ZERO_CAPITAL_WINDOW_HOURS = 6
    ZERO_CAPITAL_REPEAT_THRESHOLD = 2
    STRIKE_LIMIT_THRESHOLD = 10

    def evaluate(
        self,
        *,
        governance_id: str,
        escalation_history: List[EscalationDecision],
        strike_ledger: GovernanceStrikeLedger,
        now: Optional[datetime] = None,
    ) -> GovernanceBreachResult:

        now = now or datetime.now(timezone.utc)

        # -----------------------------------------------------
        # Rule 1: Repeated ZERO_CAPITAL within time window
        # -----------------------------------------------------
        zero_capital_events = [
            e for e in escalation_history
            if e.zero_capital and
               (now - e.timestamp) <= timedelta(hours=self.ZERO_CAPITAL_WINDOW_HOURS)
        ]

        if len(zero_capital_events) >= self.ZERO_CAPITAL_REPEAT_THRESHOLD:
            return GovernanceBreachResult(
                governance_id=governance_id,
                breached=True,
                reason="REPEATED_ZERO_CAPITAL_ESCALATION",
                timestamp=now,
            )

        # -----------------------------------------------------
        # Rule 2: Strike limit exceeded
        # -----------------------------------------------------
        strike_count = strike_ledger.get_strike_count(governance_id)

        if strike_count >= self.STRIKE_LIMIT_THRESHOLD:
            return GovernanceBreachResult(
                governance_id=governance_id,
                breached=True,
                reason="STRIKE_LIMIT_EXCEEDED",
                timestamp=now,
            )

        # -----------------------------------------------------
        # Safe
        # -----------------------------------------------------
        return GovernanceBreachResult(
            governance_id=governance_id,
            breached=False,
            reason=None,
            timestamp=now,
        )