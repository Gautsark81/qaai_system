from core.alpha.screening import (
    StructuralRiskEvidence,
    run_structural_risk_screen,
)


def test_structural_risk_clean_pass():
    evidence = StructuralRiskEvidence(
        symbol="TCS",
        event_risk_flags=(),
        balance_sheet_flags=(),
        regulatory_flags=(),
    )

    verdict = run_structural_risk_screen(
        symbol="TCS",
        evidence=evidence,
    )

    assert verdict.passed is True
    assert verdict.blocked_dimensions == ()
    assert "passed" in verdict.reasons[0].lower()

def test_event_risk_blocks():
    evidence = StructuralRiskEvidence(
        symbol="XYZ",
        event_risk_flags=("binary_event_dependency",),
        balance_sheet_flags=(),
        regulatory_flags=(),
    )

    verdict = run_structural_risk_screen(
        symbol="XYZ",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("event_risk",)

def test_balance_sheet_fragility_blocks():
    evidence = StructuralRiskEvidence(
        symbol="ABC",
        event_risk_flags=(),
        balance_sheet_flags=("excessive_leverage",),
        regulatory_flags=(),
    )

    verdict = run_structural_risk_screen(
        symbol="ABC",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("balance_sheet",)

def test_regulatory_sensitivity_blocks():
    evidence = StructuralRiskEvidence(
        symbol="DEF",
        event_risk_flags=(),
        balance_sheet_flags=(),
        regulatory_flags=("policy_dependency",),
    )

    verdict = run_structural_risk_screen(
        symbol="DEF",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("regulatory",)

def test_multiple_structural_blocks_ordered():
    evidence = StructuralRiskEvidence(
        symbol="RISKY",
        event_risk_flags=("litigation_risk",),
        balance_sheet_flags=("excessive_leverage",),
        regulatory_flags=("policy_dependency",),
    )

    verdict = run_structural_risk_screen(
        symbol="RISKY",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == (
        "event_risk",
        "balance_sheet",
        "regulatory",
    )
