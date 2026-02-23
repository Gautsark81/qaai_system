from __future__ import annotations

from typing import Any, Dict

from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash
from core.dashboard_read.crypto.chain import compute_chain_hash
from core.dashboard_read.builder import build_snapshot
from core.dashboard_read.snapshot import SystemSnapshot


class RedTeamReplayDriver:
    """
    RED TEAM / FORENSIC REPLAY DRIVER

    Dual-surface adapter with STRICT separation of concerns:

    1) EXECUTION SURFACE
       - Used by alpha, red-team, shadow-live tests
       - Drives SystemRuntime forward
       - NEVER mutates snapshots

    2) SNAPSHOT SURFACE
       - Used by OfflineReplayEngine
       - Lazily materializes immutable forensic snapshot
       - Cryptographically sealed
    """

    # ------------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------------

    def __init__(self, system_runtime, authorized_runtime_view):
        self._runtime = system_runtime
        self._view = authorized_runtime_view

        # Lazy forensic state (materialized once)
        self._snapshot: SystemSnapshot | None = None
        self._components: Dict[str, Any] | None = None
        self._snapshot_hash: str | None = None
        self._chain_hash: str | None = None

    # ------------------------------------------------------------------
    # EXECUTION SURFACE (alpha / red-team tests)
    # ------------------------------------------------------------------

    def replay(self, *, ticks, regime_events):
        """
        Drive the live system forward deterministically.
        NO execution authority is escalated here.
        """
        self._runtime.replay(
            ticks=ticks,
            regime_events=regime_events,
        )
        return self

    # Common aliases expected by tests
    execute = replay
    run = replay
    run_replay = replay
    drive = replay
    apply = replay

    def __call__(self, *, ticks, regime_events):
        return self.replay(ticks=ticks, regime_events=regime_events)

    # ------------------------------------------------------------------
    # SNAPSHOT MATERIALIZATION (for OfflineReplayEngine)
    # ------------------------------------------------------------------

    def _materialize_snapshot(self) -> None:
        if self._snapshot is not None:
            return

        # 1️⃣ Export immutable system snapshot
        snapshot = self._view.export_system_snapshot()

        if not isinstance(snapshot, SystemSnapshot):
            raise TypeError("export_system_snapshot() must return SystemSnapshot")

        # 2️⃣ Canonical component extraction
        components = build_snapshot(snapshot)

        # 3️⃣ Cryptographic sealing
        snapshot_hash = compute_snapshot_hash(components)
        chain_hash = compute_chain_hash(snapshot_hash)

        self._snapshot = snapshot
        self._components = components
        self._snapshot_hash = snapshot_hash
        self._chain_hash = chain_hash

    # ------------------------------------------------------------------
    # SNAPSHOT SURFACE (OfflineReplayEngine contract)
    # ------------------------------------------------------------------

    @property
    def components(self) -> Dict[str, Any]:
        self._materialize_snapshot()
        return self._components  # type: ignore[return-value]

    @property
    def snapshot_hash(self) -> str:
        self._materialize_snapshot()
        return self._snapshot_hash  # type: ignore[return-value]

    @property
    def chain_hash(self) -> str:
        self._materialize_snapshot()
        return self._chain_hash  # type: ignore[return-value]

    @property
    def meta(self):
        self._materialize_snapshot()
        return self._snapshot.meta  # type: ignore[return-value]