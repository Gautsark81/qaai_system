# core/tournament/promotion_artifact.py

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class PromotionArtifact:
    """
    Immutable persisted result of Phase T-4 promotion gate.
    """

    run_id: str
    strategy_id: str
    promoted: bool
    reasons: List[str]

    metrics_version: str
    promotion_version: str

    created_at: datetime

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
