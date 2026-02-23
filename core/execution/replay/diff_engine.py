from datetime import datetime
from typing import Iterable, Tuple

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.replay.results import ReplayResult
from core.execution.replay.diff_models import (
    ReplayDiffReport,
    ReplayDiffItem,
)
from core.execution.replay.diff_rules import (
    event_count_matches,
    invariant_violations_match,
)


DIFF_RULES = (
    event_count_matches,
    invariant_violations_match,
)


def diff_replay_vs_live(
    live: ExecutionTelemetrySnapshot,
    replay: ReplayResult,
    rules: Iterable = DIFF_RULES,
) -> ReplayDiffReport:
    """
    Compare live execution telemetry with replay results.

    Never raises.
    """
    diffs: list[ReplayDiffItem] = []

    for rule in rules:
        try:
            diff = rule(live, replay)
        except Exception as exc:
            diff = ReplayDiffItem(
                code="DIFF_RULE_ERROR",
                message=f"{rule.__name__} failed: {type(exc).__name__}",
            )

        if diff is not None:
            diffs.append(diff)

    return ReplayDiffReport(
        execution_id=live.telemetry.execution_id,
        replay_id=replay.replay_id,
        compared_at=datetime.utcnow(),
        diffs=tuple(diffs),
    )
