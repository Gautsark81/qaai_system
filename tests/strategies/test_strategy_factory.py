# tests/strategies/test_strategy_factory.py

import pytest
from modules.strategies.factory import StrategyFactory
from modules.strategies.spec import StrategySpec
from modules.strategies.ema_cross import EMACrossStrategy


def test_factory_creates_strategy():
    spec = StrategySpec(
        strategy_id="s1",
        strategy_type="ema_cross",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={"fast": 10, "slow": 20},
    )

    strategy = StrategyFactory.create(spec)

    assert isinstance(strategy, EMACrossStrategy)
    assert strategy.strategy_id == "s1"
    assert strategy.version == "1.0"


def test_factory_rejects_unknown_strategy():
    spec = StrategySpec(
        strategy_id="x",
        strategy_type="does_not_exist",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={},
    )

    with pytest.raises(ValueError):
        StrategyFactory.create(spec)


def test_factory_is_deterministic():
    spec = StrategySpec(
        strategy_id="s1",
        strategy_type="ema_cross",
        version="1.0",
        symbol="NIFTY",
        timeframe="5m",
        params={"fast": 10, "slow": 20},
    )

    s1 = StrategyFactory.create(spec)
    s2 = StrategyFactory.create(spec)

    assert s1.__dict__ == s2.__dict__
