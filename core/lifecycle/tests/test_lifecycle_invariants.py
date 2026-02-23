from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_terminal_state_is_absorbing():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s7",
        state=LifecycleState.RETIRED,
        since=datetime.utcnow() - timedelta(days=100),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is None
    assert new_snapshot.state == LifecycleState.RETIRED


def test_no_skipping_states():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s8",
        state=LifecycleState.CANDIDATE,
        since=datetime.utcnow(),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert new_snapshot.state == LifecycleState.PAPER
