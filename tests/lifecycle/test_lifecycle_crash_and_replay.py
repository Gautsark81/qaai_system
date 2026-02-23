from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.lifecycle.contracts.enums import TransitionReason
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_lifecycle_transition_emitted_once():
    """
    Phase-B invariant:
    - Engine is pure
    - Exactly-once behavior is achieved by snapshot evolution
    """

    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S1",
        state=LifecycleState.CANDIDATE,
        since=datetime.utcnow() - timedelta(days=5),
        version="v1",
    )

    # First evaluation → promotion to PAPER
    event1, snap1 = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event1 is not None
    assert snap1.state == LifecycleState.PAPER

    # Replay with updated snapshot → no new transition
    event2, snap2 = engine.resolve(
        snapshot=snap1,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event2 is None
    assert snap2.state == LifecycleState.PAPER


def test_crash_before_persist_does_not_advance_state():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S2",
        state=LifecycleState.PAPER,
        since=datetime.utcnow(),
        version="v1",
    )

    # Not enough time in PAPER
    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is None
    assert new_snapshot.state == LifecycleState.PAPER


def test_operator_override_is_terminal_and_replay_safe():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S3",
        state=LifecycleState.PAPER,
        since=datetime.utcnow(),
        version="v1",
    )

    event, snap = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.FAILING,
        health_status=HealthStatus.CRITICAL,
        operator_override=LifecycleState.RETIRED,
    )

    assert event is not None
    assert snap.state == LifecycleState.RETIRED

    # Replay must not resurrect
    event2, snap2 = engine.resolve(
        snapshot=snap,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event2 is None
    assert snap2.state == LifecycleState.RETIRED


def test_retired_strategy_never_recovers():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S4",
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


def test_no_lifecycle_oscillation_on_replay():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S5",
        state=LifecycleState.LIVE,
        since=datetime.utcnow() - timedelta(days=1),
        version="v1",
    )

    # Weak SSR → degradation
    event1, snap1 = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.HEALTHY,
    )

    assert event1 is not None
    assert snap1.state == LifecycleState.DEGRADED

    # Replay must not degrade again
    event2, snap2 = engine.resolve(
        snapshot=snap1,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.HEALTHY,
    )

    assert event2 is None
    assert snap2.state == LifecycleState.DEGRADED


def test_transition_reason_preserved():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="S6",
        state=LifecycleState.LIVE,
        since=datetime.utcnow(),
        version="v1",
    )

    event, snap = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.FAILING,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is not None
    assert event.reason == TransitionReason.SSR_WEAK
