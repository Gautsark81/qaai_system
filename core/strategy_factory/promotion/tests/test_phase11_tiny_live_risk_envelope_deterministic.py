# test_phase11_tiny_live_risk_envelope_deterministic.py

from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_is_deterministic():
    a = TinyLiveRiskEnvelope(
        max_capital=100_000,
        max_position_pct=0.03,
        max_daily_loss_pct=0.015,
        max_order_value=7_500,
    )

    b = TinyLiveRiskEnvelope(
        max_capital=100_000,
        max_position_pct=0.03,
        max_daily_loss_pct=0.015,
        max_order_value=7_500,
    )

    assert a == b
    assert hash(a) == hash(b)
