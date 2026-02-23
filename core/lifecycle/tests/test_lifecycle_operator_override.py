from datetime import datetime

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_operator_override_always_wins():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s6",
        state=LifecycleState.LIVE,
        since=datetime.utcnow(),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
        operator_override=LifecycleState.RETIRED,
    )

    assert new_snapshot.state == LifecycleState.RETIRED
