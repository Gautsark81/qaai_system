from datetime import date, time

from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession


def test_market_clock_is_replayable():
    config = MarketClockConfig(enable_market_clock=True)

    clock = MarketClock(config=config)

    session = MarketSession(
        session_date=date(2025, 1, 15),
        current_time=time(11, 0)
    )

    snapshot_1 = clock.snapshot(session)
    snapshot_2 = clock.snapshot(session)

    assert snapshot_1 == snapshot_2
