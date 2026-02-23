from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig


def test_market_clock_disabled_by_default():
    clock = MarketClock()
    assert clock.is_enabled is False


def test_market_clock_requires_explicit_enable():
    config = MarketClockConfig()
    clock = MarketClock(config=config)
    assert clock.is_enabled is False


def test_market_clock_enables_with_flag():
    config = MarketClockConfig(enable_market_clock=True)
    clock = MarketClock(config=config)
    assert clock.is_enabled is True
