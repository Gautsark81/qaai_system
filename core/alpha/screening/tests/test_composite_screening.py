from dataclasses import dataclass
from typing import Tuple
from core.alpha.screening import (
    CompositeScreeningInput,
    run_composite_screening,
)


@dataclass(frozen=True)
class StepVerdictStub:
    passed: bool
    blocked_dimensions: Tuple[str, ...]
    reasons: Tuple[str, ...]

def test_composite_all_pass():
    inputs = CompositeScreeningInput(
        symbol="TCS",
        liquidity=StepVerdictStub(True, (), ("ok",)),
        regime=StepVerdictStub(True, (), ("ok",)),
        statistical_illusion=StepVerdictStub(True, (), ("ok",)),
        cross_factor=StepVerdictStub(True, (), ("ok",)),
        structural_risk=StepVerdictStub(True, (), ("ok",)),
        crowding_risk=StepVerdictStub(True, (), ("ok",)),
        tail_risk=StepVerdictStub(True, (), ("ok",)),
    )

    verdict = run_composite_screening(inputs)

    assert verdict.passed is True
    assert verdict.failed_step is None
    assert verdict.blocked_dimensions == ()

def test_composite_fails_on_liquidity():
    inputs = CompositeScreeningInput(
        symbol="ILLQ",
        liquidity=StepVerdictStub(False, ("liquidity",), ("low adv",)),
        regime=StepVerdictStub(True, (), ("ok",)),
        statistical_illusion=StepVerdictStub(True, (), ("ok",)),
        cross_factor=StepVerdictStub(True, (), ("ok",)),
        structural_risk=StepVerdictStub(True, (), ("ok",)),
        crowding_risk=StepVerdictStub(True, (), ("ok",)),
        tail_risk=StepVerdictStub(True, (), ("ok",)),
    )

    verdict = run_composite_screening(inputs)

    assert verdict.passed is False
    assert verdict.failed_step == "liquidity"

def test_composite_fails_on_structural_risk():
    inputs = CompositeScreeningInput(
        symbol="RISKY",
        liquidity=StepVerdictStub(True, (), ("ok",)),
        regime=StepVerdictStub(True, (), ("ok",)),
        statistical_illusion=StepVerdictStub(True, (), ("ok",)),
        cross_factor=StepVerdictStub(True, (), ("ok",)),
        structural_risk=StepVerdictStub(False, ("event_risk",), ("litigation",)),
        crowding_risk=StepVerdictStub(True, (), ("ok",)),
        tail_risk=StepVerdictStub(True, (), ("ok",)),
    )

    verdict = run_composite_screening(inputs)

    assert verdict.passed is False
    assert verdict.failed_step == "structural_risk"
    assert "event_risk" in verdict.blocked_dimensions

def test_composite_fails_on_tail_risk():
    inputs = CompositeScreeningInput(
        symbol="TAIL",
        liquidity=StepVerdictStub(True, (), ("ok",)),
        regime=StepVerdictStub(True, (), ("ok",)),
        statistical_illusion=StepVerdictStub(True, (), ("ok",)),
        cross_factor=StepVerdictStub(True, (), ("ok",)),
        structural_risk=StepVerdictStub(True, (), ("ok",)),
        crowding_risk=StepVerdictStub(True, (), ("ok",)),
        tail_risk=StepVerdictStub(False, ("gap_risk",), ("stress gap",)),
    )

    verdict = run_composite_screening(inputs)

    assert verdict.passed is False
    assert verdict.failed_step == "tail_risk"


def test_composite_propagates_blocked_dimensions():
    inputs = CompositeScreeningInput(
        symbol="BLOCKED",
        liquidity=StepVerdictStub(True, (), ("ok",)),
        regime=StepVerdictStub(True, (), ("ok",)),
        statistical_illusion=StepVerdictStub(False, ("overfit",), ("curve fit",)),
        cross_factor=StepVerdictStub(True, (), ("ok",)),
        structural_risk=StepVerdictStub(True, (), ("ok",)),
        crowding_risk=StepVerdictStub(True, (), ("ok",)),
        tail_risk=StepVerdictStub(True, (), ("ok",)),
    )

    verdict = run_composite_screening(inputs)

    assert verdict.passed is False
    assert verdict.failed_step == "statistical_illusion"
    assert verdict.blocked_dimensions == ("overfit",)


