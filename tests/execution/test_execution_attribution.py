from datetime import datetime, timedelta

from modules.execution.attribution import ExecutionAttributionEngine
from modules.execution.events import ExecutionEvent, ExecutionStatus
from modules.execution.analytics import SlippageMetrics
from modules.execution.latency import LatencyMetrics


def test_execution_attribution_summary():
    events = [
        ExecutionEvent(
            order_id="O1",
            symbol="NIFTY",
            requested_qty=100,
            filled_qty=100,
            avg_price=19510.0,
            status=ExecutionStatus.FILLED,
            exchange_ts=datetime.utcnow(),
            system_ts=datetime.utcnow(),
        ),
        ExecutionEvent(
            order_id="O2",
            symbol="BANKNIFTY",
            requested_qty=100,
            filled_qty=50,
            avg_price=44000.0,
            status=ExecutionStatus.PARTIAL,
            exchange_ts=datetime.utcnow(),
            system_ts=datetime.utcnow(),
        ),
    ]

    slippage = {
        "O1": SlippageMetrics(
            expected_price=19500.0,
            executed_price=19510.0,
            filled_qty=100,
            requested_qty=100,
            slippage_abs=10.0,
            slippage_bps=5.13,
            fill_ratio=1.0,
            fully_filled=True,
        ),
        "O2": SlippageMetrics(
            expected_price=44010.0,
            executed_price=44000.0,
            filled_qty=50,
            requested_qty=100,
            slippage_abs=-10.0,
            slippage_bps=-2.27,
            fill_ratio=0.5,
            fully_filled=False,
        ),
    }

    latency = {
        "O1": LatencyMetrics(
            decision_to_system_ms=5.0,
            system_to_exchange_ms=20.0,
            exchange_to_fill_ms=0.0,
            end_to_end_ms=25.0,
            fully_filled=True,
        ),
        "O2": LatencyMetrics(
            decision_to_system_ms=4.0,
            system_to_exchange_ms=18.0,
            exchange_to_fill_ms=0.0,
            end_to_end_ms=22.0,
            fully_filled=False,
        ),
    }

    report = ExecutionAttributionEngine.build(
        events=events,
        slippage=slippage,
        latency=latency,
    )

    summary = report.summary()

    assert summary["orders"] == 2
    assert summary["avg_fill_ratio"] == 0.75
    assert summary["fill_rate"] == 0.5
    assert "avg_slippage_bps" in summary
    assert "avg_latency_ms" in summary
