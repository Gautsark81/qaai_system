import pytest
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.exceptions import ExecutionNotAllowed


def test_execution_guard_blocks_unknown_strategy():
    registry = StrategyRegistry()

    with pytest.raises(ExecutionNotAllowed):
        registry.assert_can_execute("fake_dna")
