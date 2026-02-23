from __future__ import annotations

from dataclasses import dataclass

from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import CapitalConstraintEvidence


# ------------------------------------------------------------------
# Capital Sizing Evidence (IMMUTABLE)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class CapitalSizingEvidence:
    strategy_dna: str
    recommended_fraction: float
    binding_constraint: str
    explanation: str


# ------------------------------------------------------------------
# Capital Sizing Engine (READ-ONLY)
# ------------------------------------------------------------------

class CapitalSizingEngine:
    """
    Phase 16.2 — Capital Sizing Intelligence

    Computes a recommended capital fraction.
    Read-only, deterministic, non-mutating.
    """

    def size(
        self,
        *,
        feasibility: CapitalFeasibilityEvidence,
        constraint: CapitalConstraintEvidence,
        capital_view,
        risk_envelope,
    ) -> CapitalSizingEvidence:

        # ----------------------------------------------------------
        # Gate 1: Not feasible → zero allocation
        # ----------------------------------------------------------

        if not feasibility.feasible:
            return CapitalSizingEvidence(
                strategy_dna=feasibility.strategy_dna,
                recommended_fraction=0.0,
                binding_constraint=constraint.binding_constraint,
                explanation="Strategy is not capital feasible",
            )

        # ----------------------------------------------------------
        # Gate 2: Conservative bounded sizing
        # ----------------------------------------------------------

        recommended = min(
            capital_view.available_fraction,
            risk_envelope.max_fraction,
        )

        return CapitalSizingEvidence(
            strategy_dna=feasibility.strategy_dna,
            recommended_fraction=recommended,
            binding_constraint=constraint.binding_constraint,
            explanation="Capital sized within available and risk limits",
        )
