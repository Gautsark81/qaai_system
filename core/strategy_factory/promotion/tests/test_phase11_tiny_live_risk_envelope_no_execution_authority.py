# test_phase11_tiny_live_risk_envelope_no_execution_authority.py

from core.strategy_factory.promotion.risk.tiny_live_risk_envelope import (
    TinyLiveRiskEnvelope,
)

def test_risk_envelope_cannot_execute_or_block():
    envelope = TinyLiveRiskEnvelope(
        max_capital=25_000,
        max_position_pct=0.02,
        max_daily_loss_pct=0.01,
        max_order_value=2_000,
    )

    assert not hasattr(envelope, "approve_trade")
    assert not hasattr(envelope, "block_trade")
    assert not hasattr(envelope, "kill_strategy")
