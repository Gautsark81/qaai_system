# modules/strategies/evaluator.py

"""
ABI bridge for strategy lifecycle evaluation.

This module exists ONLY to satisfy the public
modules.strategies package contract.

No logic lives here.
"""

from modules.strategy_lifecycle.evaluator import StrategyLifecycleEvaluator

__all__ = ["StrategyLifecycleEvaluator"]
