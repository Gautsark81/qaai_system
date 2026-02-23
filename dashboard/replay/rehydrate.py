from datetime import datetime

from dashboard.view_models import (
    ReplayResultVM,
    ReplayDiffReportVM,
    ReplayDiffItemVM,
)


def _parse_dt(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def replay_result_from_dict(d: dict) -> ReplayResultVM:
    return ReplayResultVM(
        replay_id=d["replay_id"],
        execution_id=d["execution_id"],
        completed_at=_parse_dt(d["completed_at"]),
        invariant_violations=tuple(d.get("invariant_violations", [])),
    )


def replay_diff_from_dict(d: dict) -> ReplayDiffReportVM:
    return ReplayDiffReportVM(
        replay_id=d["replay_id"],
        execution_id=d["execution_id"],
        compared_at=_parse_dt(d["compared_at"]),
        diffs=tuple(
            ReplayDiffItemVM(
                code=item["code"],
                message=item["message"],
            )
            for item in d.get("diffs", [])
        ),
    )
