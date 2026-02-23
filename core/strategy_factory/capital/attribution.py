from __future__ import annotations

from dataclasses import dataclass

from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence


# ------------------------------------------------------------------
# Capital Constraint Evidence (IMMUTABLE)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class CapitalConstraintEvidence:
    strategy_dna: str
    binding_constraint: str  # "capital" | "risk" | "none"
    slack: float
    explanation: str


# ------------------------------------------------------------------
# Capital Constraint Attributor (READ-ONLY)
# ------------------------------------------------------------------

class CapitalConstraintAttributor:
    """
    Phase 16.1 — Capital Constraint Attribution

    Explains WHICH constraint binds and HOW TIGHT it is.
    Pure, deterministic, non-mutating.
    """

    def attribute(
        self,
        *,
        feasibility: CapitalFeasibilityEvidence,
        capital_view,
        risk_envelope,
    ) -> CapitalConstraintEvidence:

        available = capital_view.available_fraction
        max_allowed = risk_envelope.max_fraction

        # ----------------------------------------------------------
        # Blocked: Capital constraint
        # ----------------------------------------------------------

        if not feasibility.feasible:
            reason = feasibility.reasons[0]

            if "capital" in reason.lower():
                return CapitalConstraintEvidence(
                    strategy_dna=feasibility.strategy_dna,
                    binding_constraint="capital",
                    slack=available - max_allowed,
                    explanation=reason,
                )

            if "risk" in reason.lower():
                return CapitalConstraintEvidence(
                    strategy_dna=feasibility.strategy_dna,
                    binding_constraint="risk",
                    slack=max_allowed - available,
                    explanation=reason,
                )

        # ----------------------------------------------------------
        # Feasible: No binding constraint
        # ----------------------------------------------------------

        return CapitalConstraintEvidence(
            strategy_dna=feasibility.strategy_dna,
            binding_constraint="none",
            slack=available - max_allowed,
            explanation="No binding capital constraints",
        )
