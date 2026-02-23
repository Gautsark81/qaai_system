from datetime import datetime
from domain.strategy_lifecycle.health_snapshot import StrategyHealthSnapshot
from domain.strategy_lifecycle.health_classifier import StrategyHealthClassifier


def test_degraded_strategy_unhealthy():
    snap = StrategyHealthSnapshot(
        strategy_id="S1",
        observed_at=datetime.utcnow(),
        ssr_current=0.60,
        ssr_reference=0.85,
        drawdown_pct=0.1,
        trade_count=50,
        anomaly_flag=False,
    )

    assert StrategyHealthClassifier.is_healthy(snap) is False
