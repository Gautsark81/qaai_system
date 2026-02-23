from datetime import datetime, timezone

from dashboard.domain.phase1_state import Phase1SystemState
from dashboard.domain.phase1_reducer import reduce_event
from dashboard.domain.invariants import Phase1InvariantViolation


class Phase1SnapshotBuilder:
    """
    Builds the authoritative Phase-1 core snapshot
    from an ordered stream of events.

    PHASE-1.4 GUARANTEES:
    - Snapshot is read-only (immutability enforced later)
    - Snapshot content is hash-safe
    - Only explicitly allowed volatile fields exist
    """

    def __init__(self, initial_state: Phase1SystemState):
        self._state = initial_state
        self._events_processed = 0

    def ingest(self, event: dict):
        try:
            self._state = reduce_event(self._state, event)
            self._events_processed += 1
        except Phase1InvariantViolation:
            # Hard safety fallback — mood collapse only
            self._state = self._state.__class__(**{
                **self._state.__dict__,
                "system_mood_index": 0.0,
            })
            raise

    def build_snapshot(self) -> dict:
        """
        Returns the immutable Phase-1 DICT snapshot
        (UI-safe, deterministic, snapshot-only).

        NOTE:
        - `timestamp` is observational and excluded from hashing
        """
        s = self._state

        return {
            # ─────────────────────────────────────────────
            # Snapshot metadata (VOLATILE — excluded from hash)
            # ─────────────────────────────────────────────
            "timestamp": datetime.now(timezone.utc),

            # ─────────────────────────────────────────────
            # Core identity (HASHED)
            # ─────────────────────────────────────────────
            "run_id": s.run_id,
            "mode": s.mode,
            "uptime_sec": s.uptime_sec,
            "events_processed": self._events_processed,

            # ─────────────────────────────────────────────
            # Safety & execution guarantees (HASHED)
            # ─────────────────────────────────────────────
            "safety": {
                "execution_possible": s.execution_possible,
                "capital_allocated": s.capital_allocated,
                "kill_switch_state": s.kill_switch_state,
            },

            # ─────────────────────────────────────────────
            # Determinism & replay (HASHED)
            # ─────────────────────────────────────────────
            "determinism": {
                "intent_count": s.intent_count,
                "replay_match_rate": s.replay_match_rate,
                "hashes": tuple(s.determinism_hashes),
            },

            # ─────────────────────────────────────────────
            # Telemetry health (HASHED)
            # ─────────────────────────────────────────────
            "telemetry": {
                "expected": s.telemetry_expected,
                "written": s.telemetry_written,
                "completeness": s.telemetry_completeness,
            },

            # ─────────────────────────────────────────────
            # Violations (HASHED)
            # ─────────────────────────────────────────────
            "violations": {
                "count": s.violation_count,
                "rate": s.violation_rate,
                "last_ts": s.last_violation_ts,
            },

            # ─────────────────────────────────────────────
            # System mood (Phase-1 scalar, HASHED)
            # ─────────────────────────────────────────────
            "system_mood": s.system_mood_index,

            # ─────────────────────────────────────────────
            # Capital (OBSERVATIONAL — HASHED, no mutation)
            # ─────────────────────────────────────────────
            "capital": {
                "allocated": s.capital_allocated,
                "available": 0.0,
                "currency": "INR",
            },

            # ─────────────────────────────────────────────
            # Phase-1 UI adapter contract (HASHED)
            # ─────────────────────────────────────────────
            "alerts": [],
            "screening": None,
            "watchlist": None,
            "strategies": None,
        }


# ------------------------------------------------------------
# Canonical Phase-1 Core Snapshot Factory
# ------------------------------------------------------------
def build_dashboard_snapshot() -> dict:
    """
    Single authoritative snapshot entry point.
    """
    builder = Phase1SnapshotBuilder(
        initial_state=Phase1SystemState.initial()
    )
    return builder.build_snapshot()
