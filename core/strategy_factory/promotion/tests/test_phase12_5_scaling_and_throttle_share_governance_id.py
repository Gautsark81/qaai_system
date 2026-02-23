from core.strategy_factory.promotion.scaling.capital_scaling_decision import (
    CapitalScalingDecision,
)
from core.capital.throttle.capital_throttle_decision import (
    CapitalThrottleDecision,
)


def test_scaling_and_throttle_share_governance_id():
    scaling = CapitalScalingDecision(
        allowed=True,
        scale_factor=1.2,
        reason="CAPITAL_SCALE_UP",
        explanation="Strong performance",
        evidence_checksum="gov-123",
    )

    throttle = CapitalThrottleDecision(
        allowed=True,
        throttle_factor=1.0,
        reason="NO_THROTTLE",
        explanation="No throttle required",
        governance_id="gov-123",
    )

    assert scaling.evidence_checksum == throttle.governance_id
