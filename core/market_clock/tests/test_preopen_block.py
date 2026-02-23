import pytest
from datetime import time

from core.market_clock.nse_clock import NSEMarketClock


def test_execution_blocked_during_preopen():
    clock = NSEMarketClock.for_test(time(9, 5, 0))

    with pytest.raises(RuntimeError):
        clock.assert_execution_allowed()
