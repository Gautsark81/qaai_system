from dataclasses import dataclass
from datetime import datetime

from core.strategy_factory.promotion.gating.live_capital_gate_reason import (
    LiveCapitalGateReason,
)


@dataclass(frozen=True)
class LiveCapitalGateDecision:
    allowed: bool
    reason: LiveCapitalGateReason
    explanation: str
    timestamp: datetime
