from intelligence.snapshots.snapshot_writer import SnapshotWriter
from datetime import datetime

def test_snapshot_is_immutable():
    writer = SnapshotWriter()
    payload = {
        "strategy_id": "S1",
        "strategy_version": "1.0",
        "stage": "BACKTEST",
        "window_type": "FIXED",
        "window_start": datetime(2020,1,1),
        "window_end": datetime(2021,1,1),
        "total_trades": 40,
        "successful_trades": 30,
        "ssr": 0.75,
        "avg_r": 0.4,
        "expectancy": 0.2,
        "max_drawdown": 0.12,
        "profit_factor": 1.9,
        "risk_blocks": 0,
        "atr_violations": 1,
        "position_size_violations": 0,
        "avg_slippage": 0.01,
        "p95_slippage": 0.03,
        "order_reject_rate": 0.0,
        "latency_p95_ms": 120,
    }

    snap1 = writer.write(payload)
    snap2 = writer.write(payload)

    assert snap1.snapshot_id != snap2.snapshot_id
