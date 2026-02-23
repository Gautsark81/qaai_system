from datetime import datetime, timedelta

from modules.execution.latency import ExecutionLatency
from modules.execution.events import ExecutionEvent, ExecutionStatus


def test_latency_computation_full_fill():
    decision_ts = datetime.utcnow()
    system_ts = decision_ts + timedelta(milliseconds=5)
    exchange_ts = system_ts + timedelta(milliseconds=20)

    ev = ExecutionEvent(
        order_id="O100",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=100,
        avg_price=19510.0,
        status=ExecutionStatus.FILLED,
        exchange_ts=exchange_ts,
        system_ts=system_ts,
    )

    metrics = ExecutionLatency.compute(
        event=ev,
        decision_ts=decision_ts,
    )

    assert metrics.decision_to_system_ms == 5.0
    assert metrics.system_to_exchange_ms == 20.0
    assert metrics.end_to_end_ms == 25.0
    assert metrics.fully_filled is True


def test_latency_partial_fill():
    decision_ts = datetime.utcnow()
    system_ts = decision_ts + timedelta(milliseconds=3)
    exchange_ts = system_ts + timedelta(milliseconds=10)

    ev = ExecutionEvent(
        order_id="O101",
        symbol="NIFTY",
        requested_qty=100,
        filled_qty=40,
        avg_price=19500.0,
        status=ExecutionStatus.PARTIAL,
        exchange_ts=exchange_ts,
        system_ts=system_ts,
    )

    metrics = ExecutionLatency.compute(
        event=ev,
        decision_ts=decision_ts,
    )

    assert metrics.decision_to_system_ms == 3.0
    assert metrics.system_to_exchange_ms == 10.0
    assert metrics.fully_filled is False
