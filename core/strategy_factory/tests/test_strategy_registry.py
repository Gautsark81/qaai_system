import pytest
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.exceptions import DuplicateStrategyError


def test_registry_rejects_duplicate_strategy():
    registry = StrategyRegistry()

    spec = StrategySpec(
        name="mean_revert",
        alpha_stream="rv",
        timeframe="5m",
        universe=["NIFTY"],
        params={"z": 2.0},
    )

    registry.register(spec)

    with pytest.raises(DuplicateStrategyError):
        registry.register(spec)


def test_registry_returns_strategy_record():
    registry = StrategyRegistry()
    spec = StrategySpec("trend", "trend", "15m", ["NIFTY"], {"len": 50})

    record = registry.register(spec)

    assert record.dna
    assert record.state == "GENERATED"
