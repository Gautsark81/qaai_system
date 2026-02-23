"""
Public health contracts for strategy governance.

This module defines the stable, import-safe API for strategy health artifacts
used by promotion, lifecycle, governance, and observability layers.

IMPORTANT:
- Downstream systems MUST import health artifacts from this module.
- Internal implementation modules must NOT be imported directly.
"""

from core.strategy_factory.health.snapshot import StrategyHealthSnapshot

__all__ = [
    "StrategyHealthSnapshot",
]
