from core.execution.execution_guard import ExecutionGuard
import pytest


def test_execution_guard_allows_valid_capital():
    guard = ExecutionGuard()
    guard.validate_execution(strategy_id="s1", capital_fraction=0.25)


def test_execution_guard_blocks_zero_capital():
    guard = ExecutionGuard()
    with pytest.raises(RuntimeError):
        guard.validate_execution(strategy_id="s1", capital_fraction=0.0)


def test_execution_guard_blocks_negative_capital():
    guard = ExecutionGuard()
    with pytest.raises(RuntimeError):
        guard.validate_execution(strategy_id="s1", capital_fraction=-0.1)


def test_execution_guard_blocks_over_allocation():
    guard = ExecutionGuard()
    with pytest.raises(RuntimeError):
        guard.validate_execution(strategy_id="s1", capital_fraction=1.5)
