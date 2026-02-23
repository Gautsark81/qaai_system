from core.strategy_factory.promotion.gating.tiny_live_gate import (
    TinyLiveGate,
)
from core.strategy_factory.promotion.eligibility import (
    PromotionEligibilityEvaluator,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_non_paper_state_cannot_enter_tiny_live():
    eligibility = PromotionEligibilityEvaluator(ssr_threshold=0.8)
    decision = eligibility.evaluate("STRAT_OK", ssr=0.95)

    gate = TinyLiveGate()

    result = gate.evaluate(
        strategy_id="STRAT_OK",
        current_state=PromotionState.SHADOW,
        promotion_decision=decision,
        paper_trades=200,
        paper_drawdown=0.02,
    )

    assert result.allowed is False
