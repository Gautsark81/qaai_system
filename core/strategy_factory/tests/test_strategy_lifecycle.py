import pytest
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote
from core.strategy_factory.exceptions import IllegalLifecycleTransition


def test_illegal_lifecycle_jump_blocked():
    registry = StrategyRegistry()
    record = registry.register(
        StrategySpec("s", "m", "5m", ["N"], {"x": 1})
    )

    with pytest.raises(IllegalLifecycleTransition):
        promote(record, "LIVE")


def test_valid_lifecycle_progression():
    registry = StrategyRegistry()
    record = registry.register(
        StrategySpec("s", "m", "5m", ["N"], {"x": 1})
    )

    promote(record, "BACKTESTED")
    promote(record, "PAPER")

    assert record.state == "PAPER"
