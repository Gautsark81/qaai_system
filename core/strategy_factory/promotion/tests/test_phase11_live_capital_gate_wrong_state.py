from core.strategy_factory.promotion.gating.live_capital_gate import (
    LiveCapitalGate,
)
from core.strategy_factory.promotion.gating.live_capital_gate_reason import (
    LiveCapitalGateReason,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_live_capital_gate_blocks_wrong_state(
    strong_ssr_metrics,
    valid_risk_envelope,
):
    gate = LiveCapitalGate()

    decision = gate.evaluate(
        strategy_state=PromotionState.PAPER,
        ssr_metrics=strong_ssr_metrics,
        risk_envelope=valid_risk_envelope,
    )

    assert decision.allowed is False
    assert decision.reason == LiveCapitalGateReason.INVALID_PROMOTION_STATE
