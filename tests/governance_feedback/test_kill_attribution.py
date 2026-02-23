from modules.governance_feedback.kill_attribution import (
    KillAttribution,
    KillReason,
)


def test_kill_attribution_creation():
    attr = KillAttribution(
        strategy_id="s1",
        reason=KillReason.DRAWDOWN,
        details="Exceeded 5% drawdown",
    )

    assert attr.reason == KillReason.DRAWDOWN
