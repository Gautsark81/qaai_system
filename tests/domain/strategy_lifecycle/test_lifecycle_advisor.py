from datetime import datetime
from domain.strategy_lifecycle.lifecycle_state import StrategyLifecycleState
from domain.strategy_lifecycle.health_snapshot import StrategyHealthSnapshot
from domain.strategy_lifecycle.lifecycle_advisor import LifecycleAdvisor


def test_live_strategy_degraded_on_health_drop():
    snap = StrategyHealthSnapshot(
        strategy_id="S1",
        observed_at=datetime.utcnow(),
        ssr_current=0.60,
        ssr_reference=0.85,
        drawdown_pct=0.12,
        trade_count=200,
        anomaly_flag=False,
    )

    next_state = LifecycleAdvisor.suggest(
        StrategyLifecycleState.LIVE,
        snap,
    )

    assert next_state == StrategyLifecycleState.DEGRADED
