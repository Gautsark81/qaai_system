from core.alpha.screening import (
    TailRiskEvidence,
    run_tail_risk_screen,
)

def test_tail_risk_clean_pass():
    evidence = TailRiskEvidence(
        symbol="TCS",
        crisis_regime_flags=(),
        volatility_explosion_flags=(),
        gap_risk_flags=(),
        correlation_breakdown_flags=(),
        convexity_failure_flags=(),
    )

    verdict = run_tail_risk_screen(
        symbol="TCS",
        evidence=evidence,
    )

    assert verdict.passed is True
    assert verdict.blocked_dimensions == ()
    assert "passed" in verdict.reasons[0].lower()

def test_crisis_regime_blocks():
    evidence = TailRiskEvidence(
        symbol="ABC",
        crisis_regime_flags=("crisis_dependency",),
        volatility_explosion_flags=(),
        gap_risk_flags=(),
        correlation_breakdown_flags=(),
        convexity_failure_flags=(),
    )

    verdict = run_tail_risk_screen(
        symbol="ABC",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("crisis_regime",)

def test_volatility_explosion_blocks():
    evidence = TailRiskEvidence(
        symbol="DEF",
        crisis_regime_flags=(),
        volatility_explosion_flags=("vol_explosion_fragility",),
        gap_risk_flags=(),
        correlation_breakdown_flags=(),
        convexity_failure_flags=(),
    )

    verdict = run_tail_risk_screen(
        symbol="DEF",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("volatility_explosion",)

def test_gap_risk_blocks():
    evidence = TailRiskEvidence(
        symbol="GHI",
        crisis_regime_flags=(),
        volatility_explosion_flags=(),
        gap_risk_flags=("stress_gap_exposure",),
        correlation_breakdown_flags=(),
        convexity_failure_flags=(),
    )

    verdict = run_tail_risk_screen(
        symbol="GHI",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("gap_risk",)

def test_correlation_breakdown_blocks():
    evidence = TailRiskEvidence(
        symbol="JKL",
        crisis_regime_flags=(),
        volatility_explosion_flags=(),
        gap_risk_flags=(),
        correlation_breakdown_flags=("correlation_spike_risk",),
        convexity_failure_flags=(),
    )

    verdict = run_tail_risk_screen(
        symbol="JKL",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("correlation_breakdown",)

def test_convexity_failure_blocks():
    evidence = TailRiskEvidence(
        symbol="MNO",
        crisis_regime_flags=(),
        volatility_explosion_flags=(),
        gap_risk_flags=(),
        correlation_breakdown_flags=(),
        convexity_failure_flags=("drawdown_convexity_failure",),
    )

    verdict = run_tail_risk_screen(
        symbol="MNO",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("convexity_failure",)

def test_multiple_tail_risks_ordered():
    evidence = TailRiskEvidence(
        symbol="RISKY",
        crisis_regime_flags=("crisis_dependency",),
        volatility_explosion_flags=("vol_explosion_fragility",),
        gap_risk_flags=("stress_gap_exposure",),
        correlation_breakdown_flags=("correlation_spike_risk",),
        convexity_failure_flags=("drawdown_convexity_failure",),
    )

    verdict = run_tail_risk_screen(
        symbol="RISKY",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == (
        "crisis_regime",
        "volatility_explosion",
        "gap_risk",
        "correlation_breakdown",
        "convexity_failure",
    )
