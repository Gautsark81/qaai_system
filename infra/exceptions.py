# infra/exceptions.py
from __future__ import annotations


class QaaiSystemError(Exception):
    """Base error for the AMATS / qaai_system project."""


class ConfigError(QaaiSystemError):
    """Configuration or .env related errors."""


class HealthcheckError(QaaiSystemError):
    """Raised when a health check fails."""


class SchedulerError(QaaiSystemError):
    """Errors in the async scheduler or job management."""


class RedisError(QaaiSystemError):
    """Redis / queue connectivity or protocol errors."""


class MarketDataError(QaaiSystemError):
    """Live / historical data feed issues."""


class BrokerError(QaaiSystemError):
    """Broker (DhanHQ) related issues."""


class RiskError(QaaiSystemError):
    """Risk-rule violations or sanity checks."""


class ExecutionError(QaaiSystemError):
    """Order execution / routing failures."""
