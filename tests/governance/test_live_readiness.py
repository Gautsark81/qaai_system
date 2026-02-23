# tests/governance/test_live_readiness.py

from core.governance.live_readiness import evaluate_live_readiness


def test_live_readiness_all_checks_pass():
    report = evaluate_live_readiness(
        governance_enabled=True,
        arming_supported=True,
        capital_safety_enabled=True,
        telemetry_persistence_enabled=True,
        replay_available=True,
        shadow_execution_verified=True,
        paper_execution_verified=True,
    )

    assert report.is_live_eligible is True
    assert report.failed_checks == ()


def test_live_readiness_fails_when_any_check_missing():
    report = evaluate_live_readiness(
        governance_enabled=True,
        arming_supported=True,
        capital_safety_enabled=False,  # ❌
        telemetry_persistence_enabled=True,
        replay_available=True,
        shadow_execution_verified=True,
        paper_execution_verified=True,
    )

    assert report.is_live_eligible is False
    assert any(
        check.name == "Capital safety rails enforced"
        for check in report.failed_checks
    )

