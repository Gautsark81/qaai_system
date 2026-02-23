import pytest
from datetime import time

from core.market_clock.nse_clock import NSEMarketClock


def test_new_positions_blocked_during_squareoff_buffer():
    clock = NSEMarketClock.for_test(time(15, 20, 0))

    with pytest.raises(RuntimeError):
        clock.assert_new_position_allowed()
