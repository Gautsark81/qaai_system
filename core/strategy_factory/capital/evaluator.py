from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.strategy_factory.health.evaluator import PromotionEvidence


# ------------------------------------------------------------------
# Capital Feasibility Evidence (IMMUTABLE)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class CapitalFeasibilityEvidence:
    strategy_dna: str
    feasible: bool
    reasons: List[str]


# ------------------------------------------------------------------
# Capital Feasibility Evaluator (READ-ONLY)
# ------------------------------------------------------------------

class CapitalFeasibilityEvaluator:
    """
    Phase 16.0 — Capital-Aware Intelligence (READ-ONLY)

    Determines whether a promotable strategy is capital-feasible.
    No allocation, no mutation, no execution.
    """

    def evaluate(
        self,
        *,
        promotion: PromotionEvidence,
        capital_view,
        risk_envelope,
    ) -> CapitalFeasibilityEvidence:

        # ----------------------------------------------------------
        # Gate 1: Promotion eligibility
        # ----------------------------------------------------------

        if not promotion.promotable:
            return CapitalFeasibilityEvidence(
                strategy_dna=promotion.strategy_dna,
                feasible=False,
                reasons=["Strategy is not promotable"],
            )

        # ----------------------------------------------------------
        # Gate 2: Capital sufficiency
        # ----------------------------------------------------------

        if capital_view.available_fraction < risk_envelope.max_fraction:
            return CapitalFeasibilityEvidence(
                strategy_dna=promotion.strategy_dna,
                feasible=False,
                reasons=["Insufficient capital available"],
            )

        # ----------------------------------------------------------
        # Gate 3: Risk envelope viability (non-trivial)
        # ----------------------------------------------------------

        if risk_envelope.max_fraction < 0.1:
            return CapitalFeasibilityEvidence(
                strategy_dna=promotion.strategy_dna,
                feasible=False,
                reasons=["Risk limit exceeded"],
            )

        # ----------------------------------------------------------
        # Capital feasible
        # ----------------------------------------------------------

        return CapitalFeasibilityEvidence(
            strategy_dna=promotion.strategy_dna,
            feasible=True,
            reasons=["Capital and risk constraints satisfied"],
        )
