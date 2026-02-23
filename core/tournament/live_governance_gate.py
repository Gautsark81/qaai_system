from typing import Iterable, List

from core.tournament.live_candidate_artifact import LiveCandidateArtifact
from core.tournament.live_governance_contracts import (
    LiveGovernanceDecision,
    LiveGovernanceStatus,
)


def filter_live_governance_approved(
    *,
    live_candidates: Iterable[LiveCandidateArtifact],
    decisions: Iterable[LiveGovernanceDecision],
) -> List[LiveCandidateArtifact]:
    """
    Allow only strategies that:
    - passed T-6
    - are explicitly APPROVED by human governance
    """

    decision_map = {
        (d.run_id, d.strategy_id): d for d in decisions
    }

    approved: List[LiveCandidateArtifact] = []

    for candidate in live_candidates:
        if not candidate.promoted:
            continue

        decision = decision_map.get(
            (candidate.run_id, candidate.strategy_id)
        )

        if decision and decision.status == LiveGovernanceStatus.APPROVED:
            approved.append(candidate)

    return approved
