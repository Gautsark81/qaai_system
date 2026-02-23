# modules/strategies/scheduler.py

"""
ABI bridge for strategy scheduling.

This module exists solely to satisfy the public
`modules.strategies` package contract.

NO logic must live here.
"""

from modules.strategy_lifecycle.scheduler import StrategyScheduler

__all__ = ["StrategyScheduler"]
