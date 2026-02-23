# test_phase11_tiny_live_risk_envelope_explanation.py

from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_explains_itself():
    envelope = TinyLiveRiskEnvelope(
        max_capital=40_000,
        max_position_pct=0.015,
        max_daily_loss_pct=0.008,
        max_order_value=4_000,
    )

    explanation = envelope.describe()

    assert "max_capital" in explanation
    assert "max_daily_loss" in explanation
