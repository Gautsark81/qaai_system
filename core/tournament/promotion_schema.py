# core/tournament/promotion_schema.py

from typing import TypedDict, List


class PromotionArtifactSchema(TypedDict):
    run_id: str
    strategy_id: str
    promoted: bool
    reasons: List[str]

    metrics_version: str
    promotion_version: str
    created_at: str
