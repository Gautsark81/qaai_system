import pytest
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.phase_b.confidence import ConfidenceEngine
from core.execution.execution_guard import ExecutionGuard
from core.strategy_factory.exceptions import ExecutionNotAllowed


def test_phase_b_does_not_grant_execution_permission():
    registry = StrategyRegistry()
    guard = ExecutionGuard(registry)

    spec = StrategySpec("s", "m", "5m", ["N"], {"x": 1})
    record = registry.register(spec)

    engine = ConfidenceEngine(registry)
    advisory = engine.compute(record.dna)

    assert advisory.confidence >= 0.0

    # Phase B must NOT enable execution
    with pytest.raises(ExecutionNotAllowed):
        guard.assert_can_execute(record.dna)
