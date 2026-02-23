from typing import Optional

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.replay.results import ReplayResult
from core.execution.replay.diff_models import ReplayDiffItem


def event_count_matches(
    live: ExecutionTelemetrySnapshot,
    replay: ReplayResult,
) -> Optional[ReplayDiffItem]:
    if len(live.telemetry.events) != len(replay.reconstructed_events):
        return ReplayDiffItem(
            code="EVENT_COUNT_MISMATCH",
            message=(
                f"Live events={len(live.telemetry.events)} "
                f"Replay events={len(replay.reconstructed_events)}"
            ),
        )
    return None


def invariant_violations_match(
    live: ExecutionTelemetrySnapshot,
    replay: ReplayResult,
) -> Optional[ReplayDiffItem]:
    live_codes = {v.code for v in live.invariants.violations}
    replay_codes = set(replay.invariant_violations)

    if live_codes != replay_codes:
        return ReplayDiffItem(
            code="INVARIANT_SET_MISMATCH",
            message=(
                f"Live={sorted(live_codes)} "
                f"Replay={sorted(replay_codes)}"
            ),
        )
    return None
