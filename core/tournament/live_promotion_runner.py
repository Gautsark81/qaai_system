from typing import Iterable, List

from core.tournament.paper_contracts import PaperEvaluation
from core.tournament.live_promotion_contracts import (
    LivePromotionDecision,
    LivePromotionThresholds,
)
from core.tournament.live_promotion_gate import evaluate_for_live


def evaluate_paper_for_live(
    evaluations: Iterable[PaperEvaluation],
    thresholds: LivePromotionThresholds | None = None,
) -> List[LivePromotionDecision]:
    thresholds = thresholds or LivePromotionThresholds()
    return [evaluate_for_live(ev, thresholds) for ev in evaluations]
