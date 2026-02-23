from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_live_degrades_on_weak_ssr():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s4",
        state=LifecycleState.LIVE,
        since=datetime.utcnow() - timedelta(days=10),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.HEALTHY,
    )

    assert new_snapshot.state == LifecycleState.DEGRADED


def test_degraded_retires_on_critical_health():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s5",
        state=LifecycleState.DEGRADED,
        since=datetime.utcnow() - timedelta(days=2),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.CRITICAL,
    )

    assert new_snapshot.state == LifecycleState.RETIRED
