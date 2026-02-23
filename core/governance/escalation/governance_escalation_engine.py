from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class EscalationDecision:
    governance_id: str
    strike_count: int
    escalation_level: str
    throttle_override: Optional[float]
    freeze_capital: bool
    zero_capital: bool
    explanation: str
    timestamp: datetime

    # Backward-compat field (optional)
    level: Optional[str] = None

    def __post_init__(self):
        # Auto-derive level if not explicitly provided
        if self.level is None:
            object.__setattr__(self, "level", self.escalation_level)


@dataclass(frozen=True)
class EscalationPolicy:
    soft_throttle_threshold: int = 2
    hard_throttle_threshold: int = 3
    freeze_threshold: int = 4
    zero_capital_threshold: int = 5
    soft_throttle_level: float = 0.75
    hard_throttle_level: float = 0.5


class GovernanceEscalationEngine:

    def __init__(self, policy: Optional[EscalationPolicy] = None):
        self._policy = policy or EscalationPolicy()

    def evaluate(
        self,
        *,
        governance_id: str,
        strike_count: int,
    ) -> EscalationDecision:

        p = self._policy
        now = datetime.now(timezone.utc)

        if strike_count <= 0:
            return EscalationDecision(
                governance_id=governance_id,
                strike_count=strike_count,
                escalation_level="NONE",
                throttle_override=None,
                freeze_capital=False,
                zero_capital=False,
                explanation="No strikes. Governance normal.",
                timestamp=now,
            )

        if strike_count >= p.zero_capital_threshold:
            return EscalationDecision(
                governance_id=governance_id,
                strike_count=strike_count,
                escalation_level="ZERO_CAPITAL",
                throttle_override=None,
                freeze_capital=False,
                zero_capital=True,
                explanation="Maximum strike threshold exceeded. Capital allocation revoked.",
                timestamp=now,
            )

        if strike_count >= p.freeze_threshold:
            return EscalationDecision(
                governance_id=governance_id,
                strike_count=strike_count,
                escalation_level="FREEZE",
                throttle_override=None,
                freeze_capital=True,
                zero_capital=False,
                explanation="Freeze threshold reached. Capital frozen.",
                timestamp=now,
            )

        if strike_count >= p.hard_throttle_threshold:
            return EscalationDecision(
                governance_id=governance_id,
                strike_count=strike_count,
                escalation_level="HARD_THROTTLE",
                throttle_override=p.hard_throttle_level,
                freeze_capital=False,
                zero_capital=False,
                explanation="Hard throttle enforced due to repeated violations.",
                timestamp=now,
            )

        if strike_count >= p.soft_throttle_threshold:
            return EscalationDecision(
                governance_id=governance_id,
                strike_count=strike_count,
                escalation_level="SOFT_THROTTLE",
                throttle_override=p.soft_throttle_level,
                freeze_capital=False,
                zero_capital=False,
                explanation="Soft throttle enforced due to violations.",
                timestamp=now,
            )

        return EscalationDecision(
            governance_id=governance_id,
            strike_count=strike_count,
            escalation_level="WARNING",
            throttle_override=None,
            freeze_capital=False,
            zero_capital=False,
            explanation="Warning level strike.",
            timestamp=now,
        )