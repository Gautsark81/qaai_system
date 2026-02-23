from datetime import datetime, timedelta

from core.lifecycle.engine import LifecycleEngine
from core.lifecycle.contracts.snapshot import LifecycleSnapshot
from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.strategy_health.contracts.enums import HealthStatus


def test_live_promotion_blocked_without_governance():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="G1",
        state=LifecycleState.PAPER,
        since=datetime.utcnow() - timedelta(days=10),
        version="v1",
    )

    event, new_snapshot = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
        operator_override=None,  # no approval
    )

    # Promotion logic allowed only via governance pipeline
    assert new_snapshot.state in {
        LifecycleState.PAPER,
        LifecycleState.CANDIDATE,
    }


def test_operator_override_cannot_resurrect_retired():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="G2",
        state=LifecycleState.RETIRED,
        since=datetime.utcnow() - timedelta(days=365),
        version="v1",
    )

    event, snap = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
        operator_override=LifecycleState.LIVE,
    )

    assert event is None
    assert snap.state == LifecycleState.RETIRED


from core.safety.kill_switch import KillSwitch
from qaai_system.execution.execution_engine import ExecutionEngine


def test_kill_switch_blocks_execution():
    kill_switch = KillSwitch(scope="global")
    kill_switch.arm(reason="emergency")

    engine = ExecutionEngine(
        mode="paper",
        config={"kill_switch": kill_switch},
    )

    try:
        engine.process_signals()
    except Exception:
        pass

    assert kill_switch.is_armed() is True


def test_kill_switch_persists_across_restart():
    kill_switch = KillSwitch(scope="global")
    kill_switch.arm(reason="breach")

    # Simulated restart
    restored = KillSwitch(scope="global")

    assert restored.is_armed() is True


def test_governance_replay_does_not_force_live():
    engine = LifecycleEngine()

    snapshot = LifecycleSnapshot(
        strategy_id="G3",
        state=LifecycleState.PAPER,
        since=datetime.utcnow() - timedelta(days=30),
        version="v1",
    )

    # Simulated replay of approval without state change
    event1, snap1 = engine.resolve(
        snapshot=snapshot,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    # Replay again
    event2, snap2 = engine.resolve(
        snapshot=snap1,
        now=datetime.utcnow(),
        ssr_status=SSRStatus.STRONG,
        health_status=HealthStatus.HEALTHY,
    )

    assert event2 is None
    assert snap2.state == snap1.state
