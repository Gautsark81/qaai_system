from core.strategy_factory.promotion.gating.live_capital_gate import (
    LiveCapitalGate,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_live_capital_gate_happy_path(
    healthy_tiny_live_strategy,
    valid_risk_envelope,
    strong_ssr_metrics,
):
    gate = LiveCapitalGate()

    decision = gate.evaluate(
        strategy_state=PromotionState.TINY_LIVE,
        ssr_metrics=strong_ssr_metrics,
        risk_envelope=valid_risk_envelope,
    )

    assert decision.allowed is True
