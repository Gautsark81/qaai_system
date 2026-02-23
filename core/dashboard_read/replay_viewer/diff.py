from typing import Dict, Any


def diff_snapshot_vs_replay(
    snapshot_components: Dict[str, Any],
    replay_domains: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Structural diff only.
    No interpretation. No thresholds. No opinions.
    """
    snapshot_keys = set(snapshot_components.keys())
    replay_keys = set(replay_domains.keys())

    return {
        "missing_in_replay": sorted(snapshot_keys - replay_keys),
        "extra_in_replay": sorted(replay_keys - snapshot_keys),
        "common": sorted(snapshot_keys & replay_keys),
    }