"""
execution/exceptions.py

Canonical execution & risk exceptions.

Doctrine:
- Deterministic semantics
- Explicit intent
- Backward compatible with existing tests
"""

from __future__ import annotations


# ============================================================
# Base Classes
# ============================================================

class ExecutionException(Exception):
    """Base class for all execution-layer exceptions."""


class RiskViolation(ExecutionException):
    """Base class for all risk-related violations."""


# Backward compatibility alias (used in tests)
RiskLimitViolation = RiskViolation


# ============================================================
# Kill Switch
# ============================================================

class KillSwitchActive(RiskViolation):
    """
    Raised when trading is blocked due to an active kill switch.
    """

    def __init__(self, reason: str | None = None):
        msg = "KILL_SWITCH_ACTIVE"
        if reason:
            msg = f"{msg}: {reason}"
        super().__init__(msg)
        self.reason = reason or "KillSwitch"


# ============================================================
# Circuit Breaker
# ============================================================

class CircuitBreakerTripped(RiskViolation):
    """
    Raised when trading is blocked due to a circuit breaker condition
    (drawdown, daily loss, heartbeat failure, etc.).
    """

    def __init__(self, reason: str | None = None):
        msg = "Trading not allowed by circuit breaker"
        if reason:
            msg = f"{msg}: {reason}"
        super().__init__(msg)
        self.reason = reason or "CircuitBreaker"


# ============================================================
# Order / Routing
# ============================================================

class OrderRejected(ExecutionException):
    """Order rejected before reaching the broker."""


class OrderRoutingError(ExecutionException):
    """Router failed after reservation."""


class ProviderError(ExecutionException):
    """Broker / provider level failure."""


# ============================================================
# Utility
# ============================================================

def is_risk_exception(exc: Exception) -> bool:
    """Helper for guards / audit hooks."""
    return isinstance(exc, RiskViolation)
