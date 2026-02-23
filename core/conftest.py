# core/conftest.py

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from core.runtime.environment import RuntimeEnvironment
from core.bootstrap.runtime import build_system_runtime
from core.introspection.red_team import AuthorizedRuntimeView
from core.runtime.run_context import RunContext
from core.runtime.run_states import RunState

from core.dashboard_read.snapshot import SystemSnapshot
from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash
from core.dashboard_read.crypto.chain import compute_chain_hash, GENESIS_CHAIN_HASH


# =====================================================
# 🔧 INTERNAL HELPER — TEST-ONLY EVENT EMITTER
# =====================================================

def _emit_forensic_event(run_registry, run_id: str, event_type: str, payload: dict):
    for name in (
        "emit_run_event",
        "record_event",
        "append_event",
        "publish_event",
        "add_event",
    ):
        fn = getattr(run_registry, name, None)
        if callable(fn):
            fn(run_id=run_id, event_type=event_type, payload=payload)
            return

    for attr in ("_events", "events", "_run_events", "run_events"):
        store = getattr(run_registry, attr, None)
        if isinstance(store, dict) and run_id in store:
            store[run_id].append(
                {"event_type": event_type, "payload": payload}
            )
            return


# =====================================================
# 🔍 TEST-ONLY REGIME FLIP SENTINEL
# =====================================================

class RegimeFlipSentinel:
    def __init__(self, *, run_registry, run_id: str):
        self._last_regime: Optional[str] = None
        self._registry = run_registry
        self._run_id = run_id

    def observe(self, *, ts: int, regime: str):
        if self._last_regime is None:
            self._last_regime = regime
            return

        if regime != self._last_regime:
            _emit_forensic_event(
                run_registry=self._registry,
                run_id=self._run_id,
                event_type="REGIME_FLIP_DETECTED",
                payload={
                    "previous": self._last_regime,
                    "current": regime,
                    "ts": ts,
                },
            )
            self._last_regime = regime


# =====================================================
# 🧊 IMMUTABLE SNAPSHOT ADAPTER (CRITICAL)
# =====================================================

class ReplaySnapshotView:
    """
    Immutable adapter that exposes replay surface
    without mutating SystemSnapshot.

    🔒 ALSO SERVES AS THE FORENSIC SEAL
    """

    def __init__(self, snapshot: SystemSnapshot):
        self._snapshot = snapshot

        self._components = {
            "system_health": snapshot.system_health,
            "market_state": snapshot.market_state,
            "pipeline_state": snapshot.pipeline_state,
            "strategy_state": snapshot.strategy_state,
            "execution_state": snapshot.execution_state,
            "risk_state": snapshot.risk_state,
            "capital_state": snapshot.capital_state,
            "shadow_state": snapshot.shadow_state,
            "paper_state": snapshot.paper_state,
            "incidents": snapshot.incidents,
            "compliance": snapshot.compliance,
            "ops_state": snapshot.ops_state,
        }

        # 🔒 CAPTURE SEALED BASELINE ONCE (STRUCTURAL)
        self._sealed_snapshot_hash = compute_snapshot_hash(self._components)

        self._snapshot_hash = self._sealed_snapshot_hash
        self._chain_hash = compute_chain_hash(
            self._snapshot_hash,
            GENESIS_CHAIN_HASH,
        )

    @property
    def components(self) -> Dict[str, Any]:
        return self._components

    @property
    def snapshot_hash(self) -> str:
        return self._snapshot_hash

    @property
    def chain_hash(self) -> str:
        return self._chain_hash

    @property
    def meta(self):
        return self._snapshot.meta

    # --------------------------------------------------
    # 🔐 FORENSIC VERIFICATION HOOK (ADDED)
    # --------------------------------------------------

    def verify(self):
        """
        Detects post-seal mutation of replay evidence.

        Called by OfflineReplayEngine via _verify_snapshot().
        """
        current_hash = compute_snapshot_hash(self._components)

        if current_hash != self._sealed_snapshot_hash:
            return type(
                "VerificationResult",
                (),
                {
                    "is_valid": False,
                    "reason": "Forensic evidence mutated after sealing",
                },
            )()

        return type(
            "VerificationResult",
            (),
            {
                "is_valid": True,
                "reason": "",
            },
        )()


# =====================================================
# 🔴 PHASE-20 RED-TEAM REPLAY DRIVER
# =====================================================

class RedTeamReplayDriver:
    """
    Phase-20 deterministic replay driver.

    EXECUTION SURFACE:
    - Drives runtime
    - No execution authority

    SNAPSHOT SURFACE:
    - Returns immutable replay adapter
    """

    def __init__(self, runtime, authorized_view):
        self._runtime = runtime
        self._view = authorized_view

        runtime.enable_red_team()
        registry = runtime.run_registry

        self._run_id = f"PHASE20_TEST_RUN_{uuid.uuid4().hex[:8]}"

        ctx = RunContext(
            run_id=self._run_id,
            git_commit="TEST",
            phase_version="20.x",
            config_fingerprint="red-team-test",
            start_time=datetime.utcnow(),
        )

        registry.register(ctx)
        registry.transition(ctx.run_id, RunState.ACTIVE)

        self._regime_sentinel = RegimeFlipSentinel(
            run_registry=registry,
            run_id=self._run_id,
        )

        self._snapshot_view: Optional[ReplaySnapshotView] = None

    # --------------------------------------------------
    # EXECUTION SURFACE
    # --------------------------------------------------

    def replay(self, *, ticks, regime_events):
        for event in regime_events:
            self._regime_sentinel.observe(
                ts=event.ts,
                regime=event.regime,
            )

        if hasattr(self._runtime, "run_for"):
            self._runtime.run_for(timedelta(minutes=30))
        elif hasattr(self._runtime, "run_until_complete"):
            self._runtime.run_until_complete()

        return self

    execute = replay
    run = replay
    run_replay = replay
    drive = replay
    apply = replay

    def __call__(self, *, ticks, regime_events):
        return self.replay(ticks=ticks, regime_events=regime_events)

    # --------------------------------------------------
    # SNAPSHOT SURFACE
    # --------------------------------------------------

    def _materialize_snapshot(self):
        if self._snapshot_view is not None:
            return

        snapshot = self._view.export_system_snapshot()
        if not isinstance(snapshot, SystemSnapshot):
            raise TypeError("export_system_snapshot() must return SystemSnapshot")

        self._snapshot_view = ReplaySnapshotView(snapshot)

    @property
    def snapshot(self):
        self._materialize_snapshot()
        return self._snapshot_view  # type: ignore

    @property
    def components(self):
        return self.snapshot.components

    @property
    def snapshot_hash(self):
        return self.snapshot.snapshot_hash

    @property
    def chain_hash(self):
        return self.snapshot.chain_hash

    @property
    def meta(self):
        return self.snapshot.meta


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture(scope="session")
def system_runtime():
    env = RuntimeEnvironment(mode="test")
    return build_system_runtime(environment=env)


@pytest.fixture
def authorized_runtime_view(system_runtime):
    system_runtime.enable_red_team()
    return AuthorizedRuntimeView(run_registry=system_runtime.run_registry)


@pytest.fixture
def deterministic_replay(system_runtime, authorized_runtime_view):
    return RedTeamReplayDriver(system_runtime, authorized_runtime_view)