from core.governance_drift import GovernanceSnapshot, detect_governance_drift


def test_drift_detection_is_deterministic():
    base = GovernanceSnapshot(
        rules_hash="abc",
        thresholds={"risk": 0.1},
        version="v1",
    )

    curr = GovernanceSnapshot(
        rules_hash="abc",
        thresholds={"risk": 0.2},
        version="v2",
    )

    r1 = detect_governance_drift(base, curr)
    r2 = detect_governance_drift(base, curr)

    assert r1.drift_signals == r2.drift_signals
