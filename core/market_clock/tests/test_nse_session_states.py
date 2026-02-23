import pytest
from datetime import datetime, time, timezone

from core.market_clock.nse_clock import NSEMarketClock
from core.market_clock.session_state import NSESessionState


IST = timezone.utc  # tests will mock IST internally


@pytest.mark.parametrize(
    "clock_time,expected",
    [
        (time(8, 59, 59), NSESessionState.CLOSED),
        (time(9, 0, 0), NSESessionState.PRE_OPEN),
        (time(9, 14, 59), NSESessionState.PRE_OPEN),
        (time(9, 15, 0), NSESessionState.OPEN),
        (time(9, 15, 5), NSESessionState.NORMAL),
        (time(15, 14, 59), NSESessionState.NORMAL),
        (time(15, 15, 0), NSESessionState.SQUARE_OFF_BUFFER),
        (time(15, 29, 59), NSESessionState.SQUARE_OFF_BUFFER),
        (time(15, 30, 0), NSESessionState.CLOSED),
    ],
)
def test_nse_session_state_mapping(clock_time, expected):
    clock = NSEMarketClock.for_test(clock_time)
    assert clock.session_state == expected
