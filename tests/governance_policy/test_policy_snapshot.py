from datetime import datetime
from modules.governance_policy.policy_snapshot import PolicySnapshot


def test_policy_snapshot():
    snap = PolicySnapshot(
        captured_at=datetime.utcnow(),
        ssr_threshold=0.8,
        max_drawdown_pct=0.05,
        approval_ttl_hours=72,
        max_capital=1_000_000,
    )
    assert snap.ssr_threshold == 0.8
