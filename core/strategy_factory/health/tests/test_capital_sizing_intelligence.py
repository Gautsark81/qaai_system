import pytest

from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import CapitalConstraintEvidence
from core.strategy_factory.capital.sizing import (
    CapitalSizingEngine,
    CapitalSizingEvidence,
)


# ------------------------------------------------------------------
# STUBS (READ-ONLY)
# ------------------------------------------------------------------

class _CapitalViewStub:
    def __init__(self, *, available_fraction: float):
        self.available_fraction = available_fraction


class _RiskEnvelopeStub:
    def __init__(self, *, max_fraction: float):
        self.max_fraction = max_fraction


def _feasible():
    return CapitalFeasibilityEvidence(
        strategy_dna="S1",
        feasible=True,
        reasons=["ok"],
    )


def _blocked(reason: str):
    return CapitalFeasibilityEvidence(
        strategy_dna="S1",
        feasible=False,
        reasons=[reason],
    )


def _constraint(binding: str, slack: float):
    return CapitalConstraintEvidence(
        strategy_dna="S1",
        binding_constraint=binding,
        slack=slack,
        explanation="x",
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_zero_allocation_when_not_feasible():
    engine = CapitalSizingEngine()

    evidence = engine.size(
        feasibility=_blocked("Insufficient capital"),
        constraint=_constraint("capital", -0.2),
        capital_view=_CapitalViewStub(available_fraction=0.5),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.recommended_fraction == 0.0


def test_allocation_is_min_of_capital_and_risk():
    engine = CapitalSizingEngine()

    evidence = engine.size(
        feasibility=_feasible(),
        constraint=_constraint("none", 0.2),
        capital_view=_CapitalViewStub(available_fraction=0.4),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.recommended_fraction == pytest.approx(0.3)


def test_allocation_limited_by_capital_when_tighter():
    engine = CapitalSizingEngine()

    evidence = engine.size(
        feasibility=_feasible(),
        constraint=_constraint("capital", -0.1),
        capital_view=_CapitalViewStub(available_fraction=0.2),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.5),
    )

    assert evidence.recommended_fraction == pytest.approx(0.2)


def test_allocation_limited_by_risk_when_tighter():
    engine = CapitalSizingEngine()

    evidence = engine.size(
        feasibility=_feasible(),
        constraint=_constraint("risk", -0.3),
        capital_view=_CapitalViewStub(available_fraction=0.9),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.1),
    )

    assert evidence.recommended_fraction == pytest.approx(0.1)


def test_sizing_evidence_is_immutable():
    engine = CapitalSizingEngine()

    evidence = engine.size(
        feasibility=_feasible(),
        constraint=_constraint("none", 0.5),
        capital_view=_CapitalViewStub(available_fraction=0.6),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.4),
    )

    with pytest.raises(Exception):
        evidence.recommended_fraction = 0.9  # type: ignore[misc]
