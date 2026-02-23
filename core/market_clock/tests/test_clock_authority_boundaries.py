from datetime import date, time

from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession


def test_market_clock_has_no_execution_authority():
    clock = MarketClock(
        config=MarketClockConfig(enable_market_clock=True)
    )

    session = MarketSession(
        session_date=date(2025, 1, 25),
        current_time=time(10, 0)
    )

    snapshot = clock.snapshot(session)

    assert snapshot.has_execution_authority is False
    assert snapshot.has_capital_authority is False
