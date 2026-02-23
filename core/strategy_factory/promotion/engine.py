from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from core.strategy_factory.health.evaluator import PromotionEvidence
from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import CapitalConstraintEvidence
from core.strategy_factory.capital.sizing import CapitalSizingEvidence

from core.reproducibility.vault_store import VaultStore


@dataclass(frozen=True)
class PromotionDecision:
    strategy_dna: str
    promote: bool
    recommended_fraction: float
    reasons: List[str]

    # Governance propagation (non-breaking)
    governance_chain_id: Optional[str] = None


class AutonomousPromotionEngine:
    """
    Canonical promotion authority.

    Phase C18.4-B:
    Enforces reproducibility vault binding before allowing promotion.
    """

    def __init__(self, vault_store: Optional[VaultStore] = None):
        # Vault store optional for backward compatibility in legacy tests
        self._vault_store = vault_store

    # ---------------------------------------------------------
    # 🔒 Reproducibility Enforcement
    # ---------------------------------------------------------

    def _enforce_reproducibility(
        self,
        promotion: PromotionEvidence,
        reasons: List[str],
    ) -> bool:
        """
        Returns True if reproducibility requirement satisfied.
        Returns False and appends reason if blocked.
        """

        # If no vault store configured → do not enforce (backward compatibility)
        if self._vault_store is None:
            return True

        record_id = getattr(promotion, "reproducibility_record_id", None)

        if not record_id:
            reasons.append("Missing reproducibility vault record")
            return False

        try:
            self._vault_store.get_by_id(record_id)
        except KeyError:
            reasons.append("Reproducibility vault record not found")
            return False

        return True

    # ---------------------------------------------------------
    # 🏛 Promotion Decision Authority
    # ---------------------------------------------------------

    def decide(
        self,
        *,
        promotion: PromotionEvidence,
        feasibility: CapitalFeasibilityEvidence,
        constraint: CapitalConstraintEvidence,
        sizing: CapitalSizingEvidence,
        governance_chain_id: Optional[str] = None,
    ) -> PromotionDecision:

        reasons: List[str] = []

        # -----------------------------------------------------
        # 1️⃣ Promotion eligibility
        # -----------------------------------------------------

        if not promotion.promotable:
            reasons.extend(promotion.reasons)
            return PromotionDecision(
                strategy_dna=promotion.strategy_dna,
                promote=False,
                recommended_fraction=0.0,
                reasons=reasons,
                governance_chain_id=governance_chain_id,
            )

        # -----------------------------------------------------
        # 🔒 Reproducibility Enforcement (C18.4-B)
        # -----------------------------------------------------

        if not self._enforce_reproducibility(promotion, reasons):
            return PromotionDecision(
                strategy_dna=promotion.strategy_dna,
                promote=False,
                recommended_fraction=0.0,
                reasons=reasons,
                governance_chain_id=governance_chain_id,
            )

        # -----------------------------------------------------
        # 2️⃣ Capital feasibility
        # -----------------------------------------------------

        if not feasibility.feasible:
            reasons.extend(feasibility.reasons)
            return PromotionDecision(
                strategy_dna=promotion.strategy_dna,
                promote=False,
                recommended_fraction=0.0,
                reasons=reasons,
                governance_chain_id=governance_chain_id,
            )

        # -----------------------------------------------------
        # 3️⃣ Sizing check
        # -----------------------------------------------------

        if sizing.recommended_fraction <= 0.0:
            reasons.append("Zero capital allocation recommended")
            return PromotionDecision(
                strategy_dna=promotion.strategy_dna,
                promote=False,
                recommended_fraction=0.0,
                reasons=reasons,
                governance_chain_id=governance_chain_id,
            )

        # -----------------------------------------------------
        # ✅ Success
        # -----------------------------------------------------

        reasons.append("All promotion criteria satisfied")

        return PromotionDecision(
            strategy_dna=promotion.strategy_dna,
            promote=True,
            recommended_fraction=sizing.recommended_fraction,
            reasons=reasons,
            governance_chain_id=governance_chain_id,
        )