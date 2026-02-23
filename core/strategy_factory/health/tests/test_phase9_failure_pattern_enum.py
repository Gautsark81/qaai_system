from core.strategy_factory.health.death_reason import DeathReason


def test_failure_patterns_are_stable_and_enumerated():
    reasons = {
        DeathReason.MAX_DRAWDOWN,
        DeathReason.SSR_FAILURE,
        DeathReason.CONSECUTIVE_LOSSES,
        DeathReason.VOLATILITY_REGIME,
        DeathReason.MARKET_STRUCTURE,
        DeathReason.OPERATOR_KILL,
        DeathReason.SYSTEM_GUARDRAIL,
    }

    # basic sanity
    assert DeathReason.MAX_DRAWDOWN in reasons
    assert all(isinstance(r.name, str) for r in reasons)
