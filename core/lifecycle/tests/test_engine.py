from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.lifecycle.contracts.enums import TransitionReason
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def _snapshot(state, since=None):
    return LifecycleSnapshot(
        strategy_id="s1",
        state=state,
        since=since or datetime.utcnow(),
        version="v1",
    )


def test_engine_promotes_candidate_to_paper():
    engine = LifecycleEngine()
    now = datetime.utcnow()

    snap = _snapshot(LifecycleState.CANDIDATE, since=now - timedelta(days=1))

    event, new_snap = engine.resolve(
        snapshot=snap,
        now=now,
        ssr_status=SSRStatus.STABLE,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is not None
    assert event.to_state == LifecycleState.PAPER
    assert new_snap.state == LifecycleState.PAPER
    assert event.reason == TransitionReason.SSR_STRONG


def test_engine_no_transition_when_rules_not_met():
    engine = LifecycleEngine()
    now = datetime.utcnow()

    snap = _snapshot(LifecycleState.PAPER, since=now - timedelta(days=1))

    event, new_snap = engine.resolve(
        snapshot=snap,
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is None
    assert new_snap.state == LifecycleState.PAPER


def test_engine_demotes_live_to_degraded():
    engine = LifecycleEngine()
    now = datetime.utcnow()

    snap = _snapshot(LifecycleState.LIVE, since=now - timedelta(days=10))

    event, new_snap = engine.resolve(
        snapshot=snap,
        now=now,
        ssr_status=SSRStatus.WEAK,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is not None
    assert event.to_state == LifecycleState.DEGRADED
    assert new_snap.state == LifecycleState.DEGRADED


def test_engine_operator_override():
    engine = LifecycleEngine()
    now = datetime.utcnow()

    snap = _snapshot(LifecycleState.LIVE)

    event, new_snap = engine.resolve(
        snapshot=snap,
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
        operator_override=LifecycleState.RETIRED,
    )

    assert event is not None
    assert event.to_state == LifecycleState.RETIRED
    assert event.reason == TransitionReason.OPERATOR_OVERRIDE
    assert new_snap.state == LifecycleState.RETIRED


def test_engine_retired_is_terminal():
    engine = LifecycleEngine()
    now = datetime.utcnow()

    snap = _snapshot(LifecycleState.RETIRED)

    event, new_snap = engine.resolve(
        snapshot=snap,
        now=now,
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event is None
    assert new_snap.state == LifecycleState.RETIRED
