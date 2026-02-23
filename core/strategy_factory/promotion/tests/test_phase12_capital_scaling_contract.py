from core.strategy_factory.promotion.scaling.capital_scaling_decision import (
    CapitalScalingDecision,
)

def test_capital_scaling_decision_contract():
    decision = CapitalScalingDecision(
        allowed=False,
        scale_factor=1.0,
        reason="blocked",
        explanation="test",
        evidence_checksum="abc123",
    )

    assert hasattr(decision, "allowed")
    assert hasattr(decision, "scale_factor")
    assert hasattr(decision, "reason")
    assert hasattr(decision, "explanation")
    assert hasattr(decision, "evidence_checksum")
    assert hasattr(decision, "timestamp")
