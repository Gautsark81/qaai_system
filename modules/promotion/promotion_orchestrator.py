from modules.promotion.promotion_state import PromotionState
from modules.promotion.promotion_gate import PromotionGate
from modules.promotion.capital_ramp import capital_ramp


class PromotionOrchestrator:
    """
    Controls PAPER → LIVE lifecycle.
    """

    def __init__(self):
        self.gate = PromotionGate()

    def step(self, *, current_state, stats, live_days: int):
        if current_state == PromotionState.PAPER:
            if self.gate.eligible(stats=stats):
                return PromotionState.CANDIDATE, 0.0

        if current_state == PromotionState.CANDIDATE:
            return PromotionState.LIVE, capital_ramp(live_days)

        return current_state, capital_ramp(live_days)
