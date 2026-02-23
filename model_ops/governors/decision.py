from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RollbackDecision:
    triggered: bool
    reasons: List[str]
