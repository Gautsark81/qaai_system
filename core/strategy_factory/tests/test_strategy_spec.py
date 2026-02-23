import pytest
from core.strategy_factory.spec import StrategySpec


def test_strategy_spec_is_immutable():
    spec = StrategySpec(
        name="momentum_v1",
        alpha_stream="momentum",
        timeframe="5m",
        universe=["NIFTY"],
        params={"lookback": 20},
    )

    with pytest.raises(TypeError):
        spec.params["lookback"] = 50


def test_strategy_spec_equality_is_structural():
    a = StrategySpec("x", "momentum", "5m", ["NIFTY"], {"lookback": 20})
    b = StrategySpec("x", "momentum", "5m", ["NIFTY"], {"lookback": 20})

    assert a == b
