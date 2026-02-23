# infra/__init__.py
"""
Core infrastructure primitives for the AMATS / qaai_system project.

Phase 0 – Core Foundation:
- Exceptions
- Logging
- Timezone utilities (IST)
- Safe-call wrappers
- Redis queue abstractions
- Health checks
"""

from .exceptions import (
    QaaiSystemError,
    ConfigError,
    HealthcheckError,
    SchedulerError,
    RedisError,
    MarketDataError,
    BrokerError,
    RiskError,
    ExecutionError,
)
from .logging import get_logger, configure_logging
from .time_utils import (
    IST,
    now_ist,
    to_ist,
    is_trading_session_open,
    TRADING_START_IST,
    BLOCK_NEW_ENTRIES_IST,
    FORCE_EXIT_IST,
)
