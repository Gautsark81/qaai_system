from core.strategy_factory.promotion.gating.live_capital_gate import (
    LiveCapitalGate,
)
from core.strategy_factory.promotion.gating.live_capital_gate_reason import (
    LiveCapitalGateReason,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_live_capital_gate_blocks_on_risk_violation(
    strong_ssr_metrics,
    invalid_risk_envelope,
):
    gate = LiveCapitalGate()

    decision = gate.evaluate(
        strategy_state=PromotionState.TINY_LIVE,
        ssr_metrics=strong_ssr_metrics,
        risk_envelope=invalid_risk_envelope,
    )

    assert decision.allowed is False
    assert decision.reason == LiveCapitalGateReason.RISK_ENVELOPE_VIOLATION
