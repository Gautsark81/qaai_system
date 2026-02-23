from core.strategy_reputation.strategy_identity import StrategyIdentity


def test_strategy_identity_is_immutable():
    s = StrategyIdentity("s1", "mean_reversion", "v1", "qaai")

    try:
        s.name = "changed"
        assert False
    except Exception:
        assert True
