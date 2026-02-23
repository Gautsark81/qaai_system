from typing import List

from core.strategy_factory.promotion.gating.tiny_live_gate_decision import (
    TinyLiveGateDecision,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)
from core.strategy_factory.promotion.promotion_decision import (
    PromotionDecision,
)


class TinyLiveGate:
    """
    Evaluates whether a PAPER strategy may be considered
    for Tiny Live deployment.

    This class is PURELY DESCRIPTIVE.
    """

    MIN_PAPER_TRADES = 50
    MAX_PAPER_DRAWDOWN = 0.10

    def evaluate(
        self,
        *,
        strategy_id: str,
        current_state: PromotionState,
        promotion_decision: PromotionDecision,
        paper_trades: int,
        paper_drawdown: float,
    ) -> TinyLiveGateDecision:
        reasons: List[str] = []

        # State gate
        if current_state != PromotionState.PAPER:
            reasons.append("Strategy is not in PAPER state")
            return TinyLiveGateDecision(
                strategy_id=strategy_id,
                from_state=current_state,
                to_state=PromotionState.TINY_LIVE,
                allowed=False,
                reasons=reasons,
            )

        # Promotion eligibility gate
        if not promotion_decision.eligible:
            reasons.append("Strategy is not promotion-eligible")
            return TinyLiveGateDecision(
                strategy_id=strategy_id,
                from_state=current_state,
                to_state=PromotionState.TINY_LIVE,
                allowed=False,
                reasons=reasons,
            )

        # Paper history gate
        if paper_trades < self.MIN_PAPER_TRADES:
            reasons.append("Insufficient paper trade history")

        if paper_drawdown > self.MAX_PAPER_DRAWDOWN:
            reasons.append("Paper drawdown exceeds Tiny Live limit")

        allowed = len(reasons) == 0

        if allowed:
            reasons.append("Paper performance acceptable for Tiny Live")

        return TinyLiveGateDecision(
            strategy_id=strategy_id,
            from_state=current_state,
            to_state=PromotionState.TINY_LIVE,
            allowed=allowed,
            reasons=reasons,
        )
