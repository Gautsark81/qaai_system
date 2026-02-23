import pytest
from core.live_trading.capital import (
    CapitalManager,
    CapitalLimitError,
)


def test_capital_allocation_blocked_when_exceeded():
    mgr = CapitalManager(
        max_capital=5000,
        max_daily_loss=1000,
    )

    mgr.record_allocation(3000)

    with pytest.raises(CapitalLimitError):
        mgr.record_allocation(2500)


def test_daily_loss_limit_enforced():
    mgr = CapitalManager(
        max_capital=5000,
        max_daily_loss=1000,
    )

    with pytest.raises(CapitalLimitError):
        mgr.record_pnl(-1500)
