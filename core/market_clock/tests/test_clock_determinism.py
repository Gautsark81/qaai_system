from datetime import date, time

from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession


def test_market_clock_deterministic_across_instances():
    config = MarketClockConfig(enable_market_clock=True)

    clock_1 = MarketClock(config=config)
    clock_2 = MarketClock(config=config)

    session = MarketSession(
        session_date=date(2025, 1, 20),
        current_time=time(12, 15)
    )

    assert clock_1.snapshot(session) == clock_2.snapshot(session)
