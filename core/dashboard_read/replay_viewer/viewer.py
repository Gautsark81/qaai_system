from typing import Any, Dict

from core.dashboard_read.replay.report import OfflineReplayReport
from core.dashboard_read.replay_viewer.diff import diff_snapshot_vs_replay


def render_replay_view(
    snapshot: Any,
    report: OfflineReplayReport,
) -> Dict[str, Any]:
    """
    Render-safe representation of snapshot vs replay.

    NO computation
    NO mutation
    NO decisions
    """
    snapshot_components = snapshot.components

    replay_domains = {
        "strategy": report.strategy,
        "risk": report.risk,
        "capital": report.capital,
        "execution": report.execution,
        "compliance": report.compliance,
    }

    return {
        "integrity": {
            "snapshot_hash": snapshot.snapshot_hash,
            "chain_hash": snapshot.chain_hash,
            "replay_consistent": report.is_consistent,
        },
        "coverage": diff_snapshot_vs_replay(
            snapshot_components=snapshot_components,
            replay_domains=replay_domains,
        ),
        "snapshot": snapshot_components,
        "replay": replay_domains,
    }