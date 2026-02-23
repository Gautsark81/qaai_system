from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class LiveCandidateArtifact:
    run_id: str
    strategy_id: str
    promoted: bool
    reasons: List[str]

    paper_version: str
    live_promotion_version: str
    created_at: datetime

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
