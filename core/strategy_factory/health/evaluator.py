from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Any

from core.strategy_factory.health.ledger import StrategyHealthLedger
from core.strategy_health.contracts.enums import HealthStatus


# ------------------------------------------------------------------
# Promotion Evidence (IMMUTABLE)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class PromotionEvidence:
    """
    Immutable promotion eligibility evidence.

    Phase C18.4-B:
    Extended to carry reproducibility_record_id.
    """

    strategy_dna: str
    promotable: bool
    reasons: List[str]
    last_evaluated_at: Optional[Any]

    # 🔒 Reproducibility Vault Binding (optional for backward compatibility)
    reproducibility_record_id: Optional[str] = None


# ------------------------------------------------------------------
# Promotion Evidence Evaluator (READ-ONLY)
# ------------------------------------------------------------------

class PromotionEvidenceEvaluator:
    """
    Phase 15.3 — Promotion Evidence Evaluation

    READ-ONLY.
    Deterministic.
    Consumes StrategyHealthLedger only.
    """

    def evaluate(
        self,
        strategy_dna: str,
        ledger: StrategyHealthLedger,
        *,
        reproducibility_record_id: Optional[str] = None,
    ) -> PromotionEvidence:

        history = ledger.history(strategy_dna)

        if not history:
            return PromotionEvidence(
                strategy_dna=strategy_dna,
                promotable=False,
                reasons=["No health history available"],
                last_evaluated_at=None,
                reproducibility_record_id=reproducibility_record_id,
            )

        latest = history[-1]

        if latest.report.health_snapshot.status != HealthStatus.HEALTHY:
            return PromotionEvidence(
                strategy_dna=strategy_dna,
                promotable=False,
                reasons=["Latest health is not healthy"],
                last_evaluated_at=latest.timestamp,
                reproducibility_record_id=reproducibility_record_id,
            )

        return PromotionEvidence(
            strategy_dna=strategy_dna,
            promotable=True,
            reasons=["Latest health is healthy"],
            last_evaluated_at=latest.timestamp,
            reproducibility_record_id=reproducibility_record_id,
        )