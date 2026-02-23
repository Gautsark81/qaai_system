# File: core/strategy_factory/promotion/promotion_decision.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PromotionDecision:
    """
    Phase 11.1 — Promotion decision is descriptive only.
    No execution, no capital, no lifecycle authority.
    """

    strategy_id: str
    eligible: bool
    reasons: List[str]
