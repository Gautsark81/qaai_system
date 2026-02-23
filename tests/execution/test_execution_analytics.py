from datetime import datetime

from modules.execution.analytics import ExecutionAnalytics
from modules.execution.events import ExecutionEvent, ExecutionStatus


def test_full_fill_positive_slippage():
    ev = ExecutionEvent(
        order_id="O1",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=100,
        avg_price=19510.0,
        status=ExecutionStatus.FILLED,
        exchange_ts=datetime.utcnow(),
        system_ts=datetime.utcnow(),
    )

    metrics = ExecutionAnalytics.slippage(
        event=ev,
        expected_price=19500.0,
    )

    assert metrics.fully_filled is True
    assert metrics.slippage_abs == 10.0
    assert round(metrics.slippage_bps, 2) == round((10 / 19500) * 10_000, 2)
    assert metrics.fill_ratio == 1.0


def test_partial_fill_slippage():
    ev = ExecutionEvent(
        order_id="O2",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=40,
        avg_price=19490.0,
        status=ExecutionStatus.PARTIAL,
        exchange_ts=datetime.utcnow(),
        system_ts=datetime.utcnow(),
    )

    metrics = ExecutionAnalytics.slippage(
        event=ev,
        expected_price=19500.0,
    )

    assert metrics.fully_filled is False
    assert metrics.fill_ratio == 0.4
    assert metrics.slippage_abs == -10.0
    assert metrics.slippage_bps < 0


def test_rejected_order_has_no_slippage():
    ev = ExecutionEvent(
        order_id="O3",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=0,
        avg_price=None,
        status=ExecutionStatus.REJECTED,
        exchange_ts=datetime.utcnow(),
        system_ts=datetime.utcnow(),
        reason="Rejected by exchange",
    )

    metrics = ExecutionAnalytics.slippage(
        event=ev,
        expected_price=19500.0,
    )

    assert metrics.executed_price is None
    assert metrics.slippage_abs is None
    assert metrics.slippage_bps is None
    assert metrics.fill_ratio == 0.0
