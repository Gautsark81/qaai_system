# core/strategy_factory/health/decay/decay_state.py

from enum import Enum


class AlphaDecayState(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADING = "degrading"
    CRITICAL = "critical"
