from dataclasses import dataclass
from typing import List

from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


@dataclass(frozen=True)
class TinyLiveGateDecision:
    """
    Descriptive-only decision indicating whether a strategy
    is allowed to be CONSIDERED for Tiny Live.

    This object has NO execution, capital, or arming authority.
    """

    strategy_id: str
    from_state: PromotionState
    to_state: PromotionState
    allowed: bool
    reasons: List[str]
