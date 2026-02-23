from datetime import datetime
from domain.strategy_lifecycle.health_snapshot import StrategyHealthSnapshot


def test_health_snapshot_immutable():
    snap = StrategyHealthSnapshot(
        strategy_id="S1",
        observed_at=datetime.utcnow(),
        ssr_current=0.72,
        ssr_reference=0.85,
        drawdown_pct=0.08,
        trade_count=120,
        anomaly_flag=False,
    )

    assert snap.trade_count == 120
