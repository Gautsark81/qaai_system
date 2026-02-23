import pytest
from datetime import datetime, timezone

from core.strategy_factory.health.evaluator import PromotionEvidence
from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import CapitalConstraintEvidence
from core.strategy_factory.capital.sizing import CapitalSizingEvidence
from core.strategy_factory.promotion.engine import (
    AutonomousPromotionEngine,
    PromotionDecision,
)


# ------------------------------------------------------------------
# STUB EVIDENCE (CONTRACT-CORRECT)
# ------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)


def _promotion(promotable: bool):
    return PromotionEvidence(
        strategy_dna="S1",
        promotable=promotable,
        reasons=["health ok"] if promotable else ["health failed"],
        last_evaluated_at=_NOW,
    )


def _feasible(feasible: bool):
    return CapitalFeasibilityEvidence(
        strategy_dna="S1",
        feasible=feasible,
        reasons=["capital ok"] if feasible else ["capital blocked"],
    )


def _constraint(binding: str):
    return CapitalConstraintEvidence(
        strategy_dna="S1",
        binding_constraint=binding,
        slack=0.1,
        explanation="x",
    )


def _sizing(fraction: float):
    return CapitalSizingEvidence(
        strategy_dna="S1",
        recommended_fraction=fraction,
        binding_constraint="none",
        explanation="sized",
    )


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_promotes_when_all_evidence_allows():
    engine = AutonomousPromotionEngine()

    decision = engine.decide(
        promotion=_promotion(True),
        feasibility=_feasible(True),
        constraint=_constraint("none"),
        sizing=_sizing(0.2),
    )

    assert decision.promote is True
    assert decision.recommended_fraction == 0.2


def test_blocks_when_health_blocks():
    engine = AutonomousPromotionEngine()

    decision = engine.decide(
        promotion=_promotion(False),
        feasibility=_feasible(True),
        constraint=_constraint("none"),
        sizing=_sizing(0.2),
    )

    assert decision.promote is False


def test_blocks_when_capital_not_feasible():
    engine = AutonomousPromotionEngine()

    decision = engine.decide(
        promotion=_promotion(True),
        feasibility=_feasible(False),
        constraint=_constraint("capital"),
        sizing=_sizing(0.2),
    )

    assert decision.promote is False


def test_blocks_when_zero_sizing():
    engine = AutonomousPromotionEngine()

    decision = engine.decide(
        promotion=_promotion(True),
        feasibility=_feasible(True),
        constraint=_constraint("none"),
        sizing=_sizing(0.0),
    )

    assert decision.promote is False


def test_decision_is_immutable():
    engine = AutonomousPromotionEngine()

    decision = engine.decide(
        promotion=_promotion(True),
        feasibility=_feasible(True),
        constraint=_constraint("none"),
        sizing=_sizing(0.2),
    )

    with pytest.raises(Exception):
        decision.promote = False  # type: ignore[misc]
