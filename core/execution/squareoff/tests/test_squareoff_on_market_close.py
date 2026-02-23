import pytest
from datetime import time

from core.execution.squareoff.authority import ForcedSquareOffAuthority
from core.market_clock.nse_clock import NSEMarketClock
from core.execution.squareoff.reasons import SquareOffReason


def test_squareoff_triggers_during_squareoff_buffer():
    clock = NSEMarketClock.for_test(time(15, 20, 0))
    authority = ForcedSquareOffAuthority(market_clock=clock)

    intent = authority.evaluate()

    assert intent is not None
    assert intent.reason == SquareOffReason.MARKET_CLOSE
