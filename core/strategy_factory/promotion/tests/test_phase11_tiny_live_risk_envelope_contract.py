# test_phase11_tiny_live_risk_envelope_contract.py

from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_is_descriptive_only():
    envelope = TinyLiveRiskEnvelope(
        max_capital=50_000,
        max_position_pct=0.02,
        max_daily_loss_pct=0.01,
        max_order_value=5_000,
    )

    assert envelope.max_capital == 50_000
    assert envelope.max_position_pct == 0.02
    assert envelope.max_daily_loss_pct == 0.01
    assert envelope.max_order_value == 5_000
