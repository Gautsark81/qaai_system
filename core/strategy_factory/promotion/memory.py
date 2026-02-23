from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.strategy_factory.promotion.models import PromotionLevel


@dataclass(frozen=True)
class PromotionMemory:
    """
    Governance memory for strategy promotion decisions.

    Tracks prior decisions to prevent oscillation and
    enforce upgrade / downgrade discipline.
    """

    last_level: PromotionLevel
    last_decision_at: Optional[datetime]
    downgrade_count: int

    def validate(self) -> None:
        if self.downgrade_count < 0:
            raise ValueError("downgrade_count must be non-negative")
