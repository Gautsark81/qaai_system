import pytest
from datetime import date

from core.market_clock.nse_clock import NSEMarketClock


def test_trading_blocked_on_holiday():
    clock = NSEMarketClock.for_test_date(
        trade_date=date(2026, 1, 26),  # Republic Day
        is_holiday=True,
    )

    with pytest.raises(RuntimeError):
        clock.assert_execution_allowed()
