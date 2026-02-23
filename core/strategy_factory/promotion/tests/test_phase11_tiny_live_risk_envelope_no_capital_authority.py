# test_phase11_tiny_live_risk_envelope_no_capital_authority.py

from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_has_no_capital_methods():
    envelope = TinyLiveRiskEnvelope(
        max_capital=10_000,
        max_position_pct=0.01,
        max_daily_loss_pct=0.005,
        max_order_value=1_000,
    )

    forbidden = [
        "allocate",
        "release",
        "execute",
        "place_order",
        "reserve",
    ]

    for name in forbidden:
        assert not hasattr(envelope, name)
