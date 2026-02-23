from domain.capital.strategy_capital_state import StrategyCapitalState


def test_strategy_capital_state():
    s = StrategyCapitalState("S1", 100_000, 0.05, 0.72)
    assert s.ssr > 0.7
