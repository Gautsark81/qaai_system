# modules/strategies/orchestrator.py

"""
ABI bridge for strategy lifecycle orchestration.

This module exists solely to satisfy the public
`modules.strategies` package contract.

NO logic must live here.
"""

from modules.strategy_lifecycle.orchestrator import StrategyLifecycleOrchestrator

__all__ = ["StrategyLifecycleOrchestrator"]
