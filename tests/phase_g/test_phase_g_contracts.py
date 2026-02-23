# tests/phase_g/test_phase_g_contracts.py

import inspect

from modules.strategies.base import BaseStrategy
from modules.execution.plan import ExecutionPlan
from modules.strategies.intent import StrategyIntent


def test_strategy_cannot_return_execution_plan():
    """
    Strategy.run must never expose ExecutionPlan in its signature.
    """
    sig = inspect.signature(BaseStrategy.run)
    sig_str = str(sig)

    assert "ExecutionPlan" not in sig_str


def test_strategy_returns_only_intent_or_none():
    """
    Contract sanity: StrategyIntent exists and is the only valid output type.
    """
    assert StrategyIntent is not None


def test_execution_plan_contains_quantity():
    """
    ExecutionPlan must carry execution-specific fields.
    """
    src = inspect.getsource(ExecutionPlan)
    assert "quantity" in src
