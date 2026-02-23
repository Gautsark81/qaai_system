from core.strategy_factory.promotion.gating.live_capital_gate import (
    LiveCapitalGate,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_live_capital_gate_is_deterministic(
    strong_ssr_metrics,
    valid_risk_envelope,
):
    gate = LiveCapitalGate()

    decision_1 = gate.evaluate(
        strategy_state=PromotionState.TINY_LIVE,
        ssr_metrics=strong_ssr_metrics,
        risk_envelope=valid_risk_envelope,
    )

    decision_2 = gate.evaluate(
        strategy_state=PromotionState.TINY_LIVE,
        ssr_metrics=strong_ssr_metrics,
        risk_envelope=valid_risk_envelope,
    )

    assert decision_1 == decision_2
