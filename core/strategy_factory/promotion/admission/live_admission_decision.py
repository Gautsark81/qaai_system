from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState


@dataclass(frozen=True)
class LiveAdmissionDecision:
    allowed: bool
    reason: str
    explanation: str
    next_state: Optional[PromotionState]
    evidence_checksum: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
