import pytest
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote
from core.live_trading.guard import LiveExecutionGuard
from core.live_trading.config import LiveTradingConfig
from core.strategy_factory.exceptions import ExecutionNotAllowed


def test_live_trading_blocked_when_disabled():
    registry = StrategyRegistry()
    spec = StrategySpec("s", "m", "5m", ["N"], {"x": 1})
    record = registry.register(spec)

    promote(record, "BACKTESTED")
    promote(record, "PAPER")
    promote(record, "LIVE")

    guard = LiveExecutionGuard(
        registry,
        LiveTradingConfig(
            enabled=False,
            max_capital_per_strategy=5000,
            max_daily_loss=1000,
        ),
    )

    with pytest.raises(ExecutionNotAllowed):
        guard.assert_can_trade_live(record.dna)


def test_only_live_strategies_can_trade():
    registry = StrategyRegistry()
    spec = StrategySpec("s", "m", "5m", ["N"], {"x": 1})
    record = registry.register(spec)

    guard = LiveExecutionGuard(
        registry,
        LiveTradingConfig(
            enabled=True,
            max_capital_per_strategy=5000,
            max_daily_loss=1000,
        ),
    )

    with pytest.raises(ExecutionNotAllowed):
        guard.assert_can_trade_live(record.dna)
