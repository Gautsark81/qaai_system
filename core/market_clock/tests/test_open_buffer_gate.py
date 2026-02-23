import pytest
from datetime import time

from core.market_clock.nse_clock import NSEMarketClock


def test_open_buffer_blocks_execution():
    clock = NSEMarketClock.for_test(time(9, 15, 2))

    with pytest.raises(RuntimeError):
        clock.assert_execution_allowed()


def test_execution_allowed_after_buffer():
    clock = NSEMarketClock.for_test(time(9, 15, 5))
    clock.assert_execution_allowed()  # must not raise
