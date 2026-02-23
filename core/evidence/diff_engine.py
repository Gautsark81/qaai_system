# core/evidence/diff_engine.py

from typing import Dict
from core.evidence.replay_contracts import ReplayFrame, ReplayDiff


def diff_frames(
    *,
    before: ReplayFrame,
    after: ReplayFrame,
) -> ReplayDiff:
    """
    Compute structural diff between two replay frames.
    """

    def _diff_dict(a: Dict, b: Dict):
        added = {k: b[k] for k in b.keys() - a.keys()}
        removed = {k: a[k] for k in a.keys() - b.keys()}
        changed = {
            k: (a[k], b[k])
            for k in a.keys() & b.keys()
            if a[k] != b[k]
        }
        return added, removed, changed

    cap_add, cap_rem, cap_chg = _diff_dict(
        before.capital_allocations,
        after.capital_allocations,
    )

    gov_add, gov_rem, gov_chg = _diff_dict(
        before.governance_states,
        after.governance_states,
    )

    return ReplayDiff(
        from_timestamp=before.timestamp,
        to_timestamp=after.timestamp,
        added={
            "capital": cap_add,
            "governance": gov_add,
        },
        removed={
            "capital": cap_rem,
            "governance": gov_rem,
        },
        changed={
            "capital": cap_chg,
            "governance": gov_chg,
        },
    )
