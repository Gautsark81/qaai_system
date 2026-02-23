# core/dashboard_read/replay/wrapper.py

from core.dashboard_read.snapshot import SystemSnapshot


class ReplaySnapshotWrapper:
    """
    OPTION A — STRICT SNAPSHOT WRAPPER

    Guarantees:
    - Holds exactly ONE immutable SystemSnapshot
    - Exposes ONLY snapshot-compatible surface
    - No execution, no mutation, no authority
    - Safe for OfflineReplayEngine
    """

    def __init__(self, snapshot: SystemSnapshot):
        if not isinstance(snapshot, SystemSnapshot):
            raise TypeError("ReplaySnapshotWrapper requires a SystemSnapshot")
        self._snapshot = snapshot

    # --------------------------------------------------
    # Snapshot surface required by OfflineReplayEngine
    # --------------------------------------------------

    @property
    def components(self):
        return self._snapshot.components

    @property
    def snapshot_hash(self):
        return self._snapshot.snapshot_hash

    @property
    def chain_hash(self):
        return self._snapshot.chain_hash

    @property
    def meta(self):
        return getattr(self._snapshot, "meta", None)

    # --------------------------------------------------
    # Explicit access (for auditors / tooling)
    # --------------------------------------------------

    @property
    def snapshot(self) -> SystemSnapshot:
        return self._snapshot