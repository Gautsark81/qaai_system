from core.telemetry.metrics_snapshot import MetricsSnapshot


def test_metrics_snapshot_is_immutable():
    snap = MetricsSnapshot.now(
        strategy_id="s1",
        source="paper",
        ssr=0.82,
        total_trades=120,
    )

    assert snap.strategy_id == "s1"
    assert snap.source == "paper"
    assert snap.ssr == 0.82
    assert snap.version == "metrics_v1"
