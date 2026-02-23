# path: qaai_system/risk/risk_exceptions.py
from __future__ import annotations


class RiskError(Exception):
    """Base exception for risk-related failures."""


class HardRiskLimitBreach(RiskError):
    """Raised when a hard risk limit is breached (trading must stop)."""


class SoftRiskLimitBreach(RiskError):
    """
    Raised when a soft risk limit is hit.

    This is typically advisory; the caller may still decide to trade.
    """


class CircuitBreakerTripped(RiskError):
    """Raised when the circuit breaker / kill-switch is active."""
