# core/capital/allocator.py

from typing import Dict, Optional

from core.capital.contracts.context import CapitalDecisionContext
from core.capital.result import CapitalAllocationResult
from core.capital.contracts import (
    StrategyCapitalSignal,
    CapitalEvidenceContext,
)
from core.capital.evidence_emitter import (
    emit_capital_allocation_evidence,
)
from core.evidence.decision_store import DecisionEvidenceStore


# ======================================================
# 🧮 PORTFOLIO-LEVEL CAPITAL ALLOCATOR (LIGHTWEIGHT)
# ======================================================

class PortfolioCapitalAllocator:
    """
    Stateless portfolio-level capital allocator.

    Guarantees:
    - Deterministic weights
    - No governance decisions
    - No side effects unless evidence_store is provided
    """

    def _compute_weights(
        self,
        signals: Dict[str, StrategyCapitalSignal],
        min_weight: float,
    ) -> Dict[str, float]:
        """
        Internal pure allocation logic.
        """
        scores = {
            sid: max(signal.ssr * signal.confidence * signal.regime_score, 0.0)
            for sid, signal in signals.items()
        }

        total = sum(scores.values())
        if total <= 0.0:
            return {sid: 0.0 for sid in scores}

        weights = {
            sid: max(score / total, min_weight)
            for sid, score in scores.items()
        }

        norm = sum(weights.values()) or 1.0
        return {sid: round(w / norm, 6) for sid, w in weights.items()}

    def allocate(
        self,
        *,
        signals: Dict[str, StrategyCapitalSignal],
        min_weight: float = 0.0,
        evidence_store: Optional[DecisionEvidenceStore] = None,
        capital_available: float = 1.0,
    ) -> Dict[str, float]:
        """
        Compute portfolio capital weights.

        Evidence emission is optional and non-intrusive.
        """

        weights = self._compute_weights(signals, min_weight)

        if evidence_store is not None:
            emit_capital_allocation_evidence(
                signals=signals,
                allocations=weights,
                capital_available=capital_available,
                store=evidence_store,
            )

        return weights


# ======================================================
# 🛡️ GOVERNED CAPITAL ALLOCATOR (DELEGATION SHELL)
# ======================================================

class CapitalAllocator:
    """
    Delegation shell with zero policy content.
    """

    def __init__(self, composition_engine):
        self.engine = composition_engine

    def allocate(self, context):
        return self.engine.compose(context)
