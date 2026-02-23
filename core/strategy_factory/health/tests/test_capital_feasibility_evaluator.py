import pytest

from core.strategy_factory.health.evaluator import PromotionEvidence
from core.strategy_factory.capital.evaluator import (
    CapitalFeasibilityEvaluator,
    CapitalFeasibilityEvidence,
)


# ------------------------------------------------------------------
# READ-ONLY CAPITAL STUBS (OPAQUE)
# ------------------------------------------------------------------

class _CapitalViewStub:
    """
    Read-only view of available capital.
    """
    def __init__(self, *, available_fraction: float):
        self.available_fraction = available_fraction


class _RiskEnvelopeStub:
    """
    Read-only risk envelope.
    """
    def __init__(self, *, max_fraction: float):
        self.max_fraction = max_fraction


def _promotion_evidence(
    *,
    promotable: bool = True,
) -> PromotionEvidence:
    return PromotionEvidence(
        strategy_dna="S1",
        promotable=promotable,
        reasons=["ok"] if promotable else ["blocked"],
        last_evaluated_at=None,
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_blocks_when_not_promotable():
    evaluator = CapitalFeasibilityEvaluator()

    evidence = evaluator.evaluate(
        promotion=_promotion_evidence(promotable=False),
        capital_view=_CapitalViewStub(available_fraction=0.5),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.feasible is False
    assert "not promotable" in evidence.reasons[0].lower()


def test_blocks_when_insufficient_capital():
    evaluator = CapitalFeasibilityEvaluator()

    evidence = evaluator.evaluate(
        promotion=_promotion_evidence(promotable=True),
        capital_view=_CapitalViewStub(available_fraction=0.1),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.feasible is False
    assert "insufficient capital" in evidence.reasons[0].lower()


def test_blocks_when_risk_limit_exceeded():
    evaluator = CapitalFeasibilityEvaluator()

    evidence = evaluator.evaluate(
        promotion=_promotion_evidence(promotable=True),
        capital_view=_CapitalViewStub(available_fraction=0.8),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.05),
    )

    assert evidence.feasible is False
    assert "risk limit" in evidence.reasons[0].lower()


def test_allows_when_capital_and_risk_allow():
    evaluator = CapitalFeasibilityEvaluator()

    evidence = evaluator.evaluate(
        promotion=_promotion_evidence(promotable=True),
        capital_view=_CapitalViewStub(available_fraction=0.6),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    assert evidence.feasible is True
    assert evidence.strategy_dna == "S1"


def test_evidence_is_immutable():
    evaluator = CapitalFeasibilityEvaluator()

    evidence = evaluator.evaluate(
        promotion=_promotion_evidence(promotable=True),
        capital_view=_CapitalViewStub(available_fraction=0.6),
        risk_envelope=_RiskEnvelopeStub(max_fraction=0.3),
    )

    with pytest.raises(Exception):
        evidence.feasible = False  # type: ignore[misc]
