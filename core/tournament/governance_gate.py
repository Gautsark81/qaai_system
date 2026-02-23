# core/tournament/governance_gate.py

from typing import Iterable, List

from core.tournament.promotion_artifact import PromotionArtifact
from core.tournament.governance_contracts import (
    GovernanceDecision,
    GovernanceStatus,
)


def filter_governance_approved(
    *,
    promotions: Iterable[PromotionArtifact],
    decisions: Iterable[GovernanceDecision],
) -> List[PromotionArtifact]:
    """
    Return only strategies that are:
    - promoted by T-4
    - explicitly APPROVED by governance
    """

    decision_map = {
        (d.run_id, d.strategy_id): d for d in decisions
    }

    approved: List[PromotionArtifact] = []

    for promo in promotions:
        decision = decision_map.get((promo.run_id, promo.strategy_id))
        if decision and decision.status == GovernanceStatus.APPROVED:
            approved.append(promo)

    return approved
