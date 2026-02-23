from core.alpha.screening import (
    CrowdingRiskEvidence,
    run_crowding_risk_screen,
)


def test_crowding_risk_clean_pass():
    evidence = CrowdingRiskEvidence(
        symbol="TCS",
        institutional_crowding_flags=(),
        strategy_consensus_flags=(),
        positioning_fragility_flags=(),
    )

    verdict = run_crowding_risk_screen(
        symbol="TCS",
        evidence=evidence,
    )

    assert verdict.passed is True
    assert verdict.blocked_dimensions == ()
    assert "passed" in verdict.reasons[0].lower()

def test_institutional_crowding_blocks():
    evidence = CrowdingRiskEvidence(
        symbol="ABC",
        institutional_crowding_flags=("fii_overcrowding",),
        strategy_consensus_flags=(),
        positioning_fragility_flags=(),
    )

    verdict = run_crowding_risk_screen(
        symbol="ABC",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("institutional_crowding",)

def test_strategy_consensus_blocks():
    evidence = CrowdingRiskEvidence(
        symbol="DEF",
        institutional_crowding_flags=(),
        strategy_consensus_flags=("strategy_saturation",),
        positioning_fragility_flags=(),
    )

    verdict = run_crowding_risk_screen(
        symbol="DEF",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("strategy_consensus",)

def test_positioning_fragility_blocks():
    evidence = CrowdingRiskEvidence(
        symbol="GHI",
        institutional_crowding_flags=(),
        strategy_consensus_flags=(),
        positioning_fragility_flags=("one_way_positioning",),
    )

    verdict = run_crowding_risk_screen(
        symbol="GHI",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == ("positioning_fragility",)

def test_multiple_crowding_blocks_ordered():
    evidence = CrowdingRiskEvidence(
        symbol="RISKY",
        institutional_crowding_flags=("fii_overcrowding",),
        strategy_consensus_flags=("strategy_saturation",),
        positioning_fragility_flags=("one_way_positioning",),
    )

    verdict = run_crowding_risk_screen(
        symbol="RISKY",
        evidence=evidence,
    )

    assert verdict.passed is False
    assert verdict.blocked_dimensions == (
        "institutional_crowding",
        "strategy_consensus",
        "positioning_fragility",
    )

