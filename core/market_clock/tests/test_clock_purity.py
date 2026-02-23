from datetime import date, time

from core.market_clock.clock import MarketClock
from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession
from core.governance.reconstruction import reconstruct_system_state


def test_market_clock_has_no_side_effects():
    clock = MarketClock(
        config=MarketClockConfig(enable_market_clock=True)
    )

    session = MarketSession(
        session_date=date(2025, 1, 22),
        current_time=time(11, 45)
    )

    before_state = reconstruct_system_state()
    clock.snapshot(session)
    after_state = reconstruct_system_state()

    assert before_state == after_state
