from domain.behavior_fingerprint.diff import FingerprintDiff


def test_fingerprint_diff_structure():
    diff = FingerprintDiff(
        from_version=1,
        to_version=2,
        breaking_changes=["strategy_family"],
        non_breaking_changes=["meta"],
        risk_relevant_changes=[],
        execution_relevant_changes=[],
    )

    assert diff.breaking_changes
