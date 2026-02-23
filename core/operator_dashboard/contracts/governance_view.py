from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GovernanceApprovalView:
    strategy_id: str
    stage: str              # paper / live / scale
    status: str             # approved / rejected / pending
    reviewer: str
    reasons: List[str]
    decided_at: str
