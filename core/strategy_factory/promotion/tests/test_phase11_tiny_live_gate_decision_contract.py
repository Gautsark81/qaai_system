from core.strategy_factory.promotion.gating.tiny_live_gate_decision import (
    TinyLiveGateDecision,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_tiny_live_gate_decision_is_descriptive():
    d = TinyLiveGateDecision(
        strategy_id="STRAT_001",
        from_state=PromotionState.PAPER,
        to_state=PromotionState.TINY_LIVE,
        allowed=True,
        reasons=["SSR stable", "Paper performance acceptable"],
    )

    assert d.allowed is True
    assert isinstance(d.reasons, list)
