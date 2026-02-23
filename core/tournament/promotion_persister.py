# core/tournament/promotion_persister.py

from typing import Iterable, List

from core.tournament.metrics_contract import StrategyMetrics
from core.tournament.promotion_contracts import PromotionDecision
from core.tournament.promotion_artifact import PromotionArtifact
from core.tournament.promotion_store import PromotionStore


def persist_promotion_decisions(
    *,
    run_id: str,
    metrics_list: Iterable[StrategyMetrics],
    decisions: Iterable[PromotionDecision],
    promotion_version: str = "t4_v1",
    store: PromotionStore | None = None,
) -> None:
    """
    Persist Phase T-4 promotion decisions as immutable artifacts.
    """

    store = store or PromotionStore()

    metrics_map = {m.strategy_id: m for m in metrics_list}

    artifacts: List[PromotionArtifact] = []

    for decision in decisions:
        metrics = metrics_map[decision.strategy_id]

        artifacts.append(
            PromotionArtifact(
                run_id=run_id,
                strategy_id=decision.strategy_id,
                promoted=decision.promoted,
                reasons=decision.reasons,

                metrics_version=metrics.metrics_version,
                promotion_version=promotion_version,

                created_at=PromotionArtifact.now_utc(),
            )
        )

    store.persist(artifacts)
