from datetime import date, time

from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession


def enabled_clock():
    return MarketClock(
        config=MarketClockConfig(enable_market_clock=True)
    )


def test_clock_blocks_outside_market_hours():
    clock = enabled_clock()

    session = MarketSession(
        session_date=date(2025, 1, 10),
        current_time=time(8, 45)
    )

    assert clock.is_market_open(session) is False


def test_clock_allows_during_market_hours():
    clock = enabled_clock()

    session = MarketSession(
        session_date=date(2025, 1, 10),
        current_time=time(10, 30)
    )

    assert clock.is_market_open(session) is True


def test_clock_blocks_after_market_close():
    clock = enabled_clock()

    session = MarketSession(
        session_date=date(2025, 1, 10),
        current_time=time(15, 45)
    )

    assert clock.is_market_open(session) is False
