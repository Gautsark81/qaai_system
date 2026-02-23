# test_phase11_tiny_live_risk_envelope_immutable.py

import pytest
from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_is_immutable():
    envelope = TinyLiveRiskEnvelope(
        max_capital=30_000,
        max_position_pct=0.02,
        max_daily_loss_pct=0.01,
        max_order_value=3_000,
    )

    with pytest.raises(Exception):
        envelope.max_capital = 100_000
