from domain.behavior_fingerprint.governance import GovernanceFingerprint


def test_governance_fingerprint():
    fp = GovernanceFingerprint(
        allowed_environments={"backtest", "paper"},
        requires_human_approval=True,
        max_capital_allocation_pct=0.10,
        kill_switch_required=True,
        audit_level="strict",
    )

    assert fp.kill_switch_required is True
