from core.governance_drift import (
    GovernanceSnapshot,
    detect_governance_drift,
)


def test_detects_ruleset_drift():
    base = GovernanceSnapshot(
        rules_hash="abc",
        thresholds={"risk": 0.1},
        version="v1",
    )

    curr = GovernanceSnapshot(
        rules_hash="def",
        thresholds={"risk": 0.1},
        version="v2",
    )

    snapshot = detect_governance_drift(base, curr)
    assert len(snapshot.drift_signals) == 1
