from pathlib import Path

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.telemetry.metrics_snapshot import MetricsSnapshot


def test_metrics_history_append_and_load(tmp_path: Path):
    store = MetricsHistoryStore(root_dir=tmp_path)

    snap1 = MetricsSnapshot.now(
        strategy_id="s1",
        source="backtest",
        ssr=0.78,
        total_trades=200,
    )

    snap2 = MetricsSnapshot.now(
        strategy_id="s1",
        source="paper",
        ssr=0.81,
        total_trades=85,
        latency_ms=42.0,
    )

    store.append(snap1)
    store.append(snap2)

    history = store.load("s1")

    assert len(history) == 2
    assert history[0]["source"] == "backtest"
    assert history[1]["source"] == "paper"
    assert history[1]["latency_ms"] == 42.0
