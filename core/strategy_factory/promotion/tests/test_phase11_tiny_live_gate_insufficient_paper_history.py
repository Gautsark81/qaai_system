from core.strategy_factory.promotion.gating.tiny_live_gate import (
    TinyLiveGate,
)
from core.strategy_factory.promotion.eligibility import (
    PromotionEligibilityEvaluator,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_insufficient_paper_trades_blocks_tiny_live():
    eligibility = PromotionEligibilityEvaluator(ssr_threshold=0.8)
    decision = eligibility.evaluate("STRAT_FEW", ssr=0.95)

    gate = TinyLiveGate()

    result = gate.evaluate(
        strategy_id="STRAT_FEW",
        current_state=PromotionState.PAPER,
        promotion_decision=decision,
        paper_trades=10,
        paper_drawdown=0.01,
    )

    assert result.allowed is False
