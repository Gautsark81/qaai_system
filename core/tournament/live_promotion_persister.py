from typing import Iterable, List

from core.tournament.paper_contracts import PaperEvaluation
from core.tournament.live_promotion_contracts import LivePromotionDecision
from core.tournament.live_candidate_artifact import LiveCandidateArtifact
from core.tournament.live_candidate_store import LiveCandidateStore


def persist_live_candidates(
    *,
    run_id: str,
    evaluations: Iterable[PaperEvaluation],
    decisions: Iterable[LivePromotionDecision],
    paper_version: str,
    live_promotion_version: str = "t6_v1",
    store: LiveCandidateStore | None = None,
) -> None:
    store = store or LiveCandidateStore()

    eval_map = {e.strategy_id: e for e in evaluations}
    artifacts: List[LiveCandidateArtifact] = []

    for d in decisions:
        e = eval_map[d.strategy_id]
        artifacts.append(
            LiveCandidateArtifact(
                run_id=run_id,
                strategy_id=d.strategy_id,
                promoted=d.promoted,
                reasons=d.reasons,
                paper_version=e.paper_version,
                live_promotion_version=live_promotion_version,
                created_at=LiveCandidateArtifact.now_utc(),
            )
        )

    store.persist(artifacts)
