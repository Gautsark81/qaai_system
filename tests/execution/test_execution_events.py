from datetime import datetime

from modules.execution.events import (
    ExecutionEvent,
    ExecutionStatus,
)


def test_fill_ratio():
    ev = ExecutionEvent(
        order_id="O1",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=40,
        avg_price=19500.0,
        status=ExecutionStatus.PARTIAL,
        exchange_ts=datetime.utcnow(),
        system_ts=datetime.utcnow(),
    )

    assert ev.fill_ratio() == 0.4


def test_terminal_states():
    ev = ExecutionEvent(
        order_id="O2",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=100,
        avg_price=19510.0,
        status=ExecutionStatus.FILLED,
        exchange_ts=datetime.utcnow(),
        system_ts=datetime.utcnow(),
    )

    assert ev.is_terminal() is True
