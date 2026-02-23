from modules.shadow_live.health_policy import (
    ShadowHealthEvaluator,
    ShadowHealthPolicy,
)


def test_health_violation_drawdown():
    policy = ShadowHealthPolicy(0.05, 0.5, 10_000)
    eval = ShadowHealthEvaluator()

    assert eval.violated(
        peak_pnl=100_000,
        current_pnl=90_000,
        ssr=0.8,
        policy=policy,
    )
