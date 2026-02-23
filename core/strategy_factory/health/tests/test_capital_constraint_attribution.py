import pytest

from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import (
    CapitalConstraintAttributor,
    CapitalConstraintEvidence,
)


# ------------------------------------------------------------------
# READ-ONLY STUBS
# ------------------------------------------------------------------

class _CapitalViewStub:
    def __init__(self, *, available_fraction: float):
        self.available_fraction = available_fraction


class _RiskEnvelopeStub:
    def __init__(self, *, max_fraction: float):
        self.max_fraction = max_fraction


def _feasible_evidence() -> CapitalFeasibilityEvidence:
    return CapitalFeasibilityEvidence(
        strategy_dna="S1",
        feasible=True,
        reasons=["ok"],
    )


def _blocked_evidence(reason: str) -> CapitalFeasibilityEvidence:
    return CapitalFeasibilityEvidence(
        strategy_dna="S1",
        feasible=False,
        reasons=[reason],
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_attributes_capital_constraint_when_insufficient():
    attributor = CapitalConstraintAttributor()

    evidence = attributor.attribute(
        feasibility=_blocked_evidence("Insufficient capital available"),
        capital_view=_CapitalViewStub(available_fraction=0.1),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.binding_constraint == "capital"
    assert evidence.slack < 0.0


def test_attributes_risk_constraint_when_exceeded():
    attributor = CapitalConstraintAttributor()

    evidence = attributor.attribute(
        feasibility=_blocked_evidence("Risk limit exceeded"),
        capital_view=_CapitalViewStub(available_fraction=0.8),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.05),
    )

    assert evidence.binding_constraint == "risk"
    assert evidence.slack < 0.0


def test_attributes_none_when_feasible():
    attributor = CapitalConstraintAttributor()

    evidence = attributor.attribute(
        feasibility=_feasible_evidence(),
        capital_view=_CapitalViewStub(available_fraction=0.6),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.binding_constraint == "none"
    assert evidence.slack >= 0.0


def test_slack_is_difference_between_capital_and_risk():
    attributor = CapitalConstraintAttributor()

    evidence = attributor.attribute(
        feasibility=_feasible_evidence(),
        capital_view=_CapitalViewStub(available_fraction=0.5),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.slack == pytest.approx(0.2)


def test_evidence_is_immutable():
    attributor = CapitalConstraintAttributor()

    evidence = attributor.attribute(
        feasibility=_feasible_evidence(),
        capital_view=_CapitalViewStub(available_fraction=0.6),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    with pytest.raises(Exception):
        evidence.binding_constraint = "capital"  # type: ignore[misc]
