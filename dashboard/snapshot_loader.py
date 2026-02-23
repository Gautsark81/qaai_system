from datetime import datetime, timezone
from dashboard.domain.phase2_interpretation import attach_phase2_to_snapshot
from dashboard.lifecycle import DashboardState  # ✅ canonical enum
from dashboard.domain.dashboard_snapshot import DashboardSnapshot
from dashboard.services.phase1_snapshot_builder import build_dashboard_snapshot
from dashboard.domain.system_mood import compute_system_mood
from dashboard.domain.system_mood_drift import compute_system_mood_drift
from dashboard.domain.violation_pulse import ViolationPulseResult


def load_dashboard_snapshot():
    """
    Canonical dashboard snapshot loader.

    PHASE COVERAGE:
    - Phase-1.x (Snapshot Safety, Lineage, Governance, Arming)
    - Phase-2.x compatible (Interpretation & Governance Surfaces are snapshot-bound)

    GUARANTEES:
    - Never raises into UI
    - Never returns None
    - Snapshot is READ-ONLY
    - Deterministic per invocation
    - No side effects
    """

    try:
        # ─────────────────────────────────────────────
        # Core snapshot (event-sourced, immutable)
        # ─────────────────────────────────────────────
        core_snapshot = build_dashboard_snapshot()

        # ─────────────────────────────────────────────
        # Derived analytics (pure functions)
        # ─────────────────────────────────────────────
        system_mood_detail = compute_system_mood(core_snapshot)
        system_mood_drift = compute_system_mood_drift(system_mood_detail)

        snapshot = DashboardSnapshot(
            core=core_snapshot,
            system_mood_detail=system_mood_detail,
            system_mood_drift=system_mood_drift,
            violation_pulse=ViolationPulseResult(
                score=0.0,
                contributors=(),
                computed_at=datetime.now(timezone.utc),
            ),
            parent_hash=None,
            lineage_depth=0,
            cause="BOOT",
        )

        snapshot = attach_phase2_to_snapshot(snapshot)

        return DashboardState.IDLE, snapshot


    except Exception:
        # ─────────────────────────────────────────────
        # Degraded-safe fallback (NO RAISE)
        # ─────────────────────────────────────────────
        core_snapshot = build_dashboard_snapshot()

        neutral_mood = compute_system_mood(core_snapshot)
        neutral_drift = compute_system_mood_drift(neutral_mood)

        snapshot = DashboardSnapshot(
            core=core_snapshot,
            system_mood_detail=neutral_mood,
            system_mood_drift=neutral_drift,
            violation_pulse=ViolationPulseResult(
                score=0.0,
                contributors=(),
                computed_at=datetime.now(timezone.utc),
            ),
            parent_hash=None,
            lineage_depth=0,
            cause="BOOT",
        )

        return DashboardState.DEGRADED, snapshot
