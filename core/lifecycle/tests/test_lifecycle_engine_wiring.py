from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.rules import LifecycleRules
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_engine_is_deterministic():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s1",
        state=LifecycleState.CANDIDATE,
        since=datetime.utcnow() - timedelta(days=10),
        version="v1",
    )

    now = datetime.utcnow()

    e1, s1 = engine.resolve(
        snapshot=snapshot,
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    e2, s2 = engine.resolve(
        snapshot=snapshot,
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert e1 == e2
    assert s1 == s2
