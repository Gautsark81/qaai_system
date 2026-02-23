# tests/infra/test_logging_and_exceptions.py
import logging

from infra import (
    QaaiSystemError,
    ConfigError,
    HealthcheckError,
    SchedulerError,
    RedisError,
    MarketDataError,
    BrokerError,
    RiskError,
    ExecutionError,
    get_logger,
    configure_logging,
)


def test_exceptions_hierarchy():
    assert issubclass(ConfigError, QaaiSystemError)
    assert issubclass(HealthcheckError, QaaiSystemError)
    assert issubclass(SchedulerError, QaaiSystemError)
    assert issubclass(RedisError, QaaiSystemError)
    assert issubclass(MarketDataError, QaaiSystemError)
    assert issubclass(BrokerError, QaaiSystemError)
    assert issubclass(RiskError, QaaiSystemError)
    assert issubclass(ExecutionError, QaaiSystemError)


def test_logging_config_and_get_logger():
    configure_logging(level=logging.DEBUG, json_logs=True)
    logger = get_logger("test_logger")
    logger.info("hello_phase0", extra={"phase": 0})
    # If we reached here without error, logger is configured
    assert logger.name == "test_logger"
