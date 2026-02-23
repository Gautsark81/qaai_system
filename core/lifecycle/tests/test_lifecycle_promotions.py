from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_candidate_to_paper():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s2",
        state=LifecycleState.CANDIDATE,
        since=datetime.utcnow() - timedelta(days=5),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is not None
    assert new_snapshot.state == LifecycleState.PAPER


def test_paper_to_live_requires_time_and_health():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="s3",
        state=LifecycleState.PAPER,
        since=datetime.utcnow() - timedelta(days=1),  # too short
        version="v1",
    )

    event, _ = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is None
