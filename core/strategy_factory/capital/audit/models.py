from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


ThrottleType = Literal["HARD", "SOFT"]


@dataclass(frozen=True)
class ThrottleDecisionEvent:
    strategy_id: str
    requested_capital: float
    approved_capital: float
    throttle_type: ThrottleType
    throttle_reason: str
    stability_score: float
    created_at: str  # ISO format

    @property
    def was_throttled(self) -> bool:
        return self.approved_capital < self.requested_capital