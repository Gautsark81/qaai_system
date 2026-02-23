from datetime import datetime

from core.ssr.engine import SSREngine
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.snapshot import StrategyHealthSnapshot
from core.strategy_health.contracts.enums import HealthStatus


def test_ssr_engine_end_to_end():
    engine = SSREngine()

    health_snaps = [
        StrategyHealthSnapshot(
            strategy_id="s1",
            as_of=datetime.utcnow(),
            overall_score=0.9,
            status=HealthStatus.HEALTHY,
            dimensions={},
            trailing_metrics={},
            regime_context="TREND",
            confidence=0.9,
            flags=[],
            version="v1",
        )
        for _ in range(10)
    ]

    snap = engine.compute(
        strategy_id="s1",
        as_of=datetime.utcnow(),
        outcome_inputs={
            "returns": [0.01] * 20,
            "expectancy": 0.01,
            "win_rate": 0.7,
        },
        health_inputs={
            "health_snapshots": health_snaps,
        },
        consistency_inputs={
            "returns": [0.01, 0.011, 0.009],
        },
        trailing_metrics={},
        confidence=0.9,
    )

    assert snap.ssr > 0.7
    assert snap.status in (SSRStatus.STRONG, SSRStatus.STABLE)
