from datetime import time

from core.market_clock.nse_clock import NSEMarketClock


def test_clock_is_pure_and_deterministic():
    clock = NSEMarketClock.for_test(time(9, 16, 0))

    state1 = clock.session_state
    state2 = clock.session_state

    assert state1 == state2
