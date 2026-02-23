from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ExecutionGateResult:
    allowed: bool
    reasons: List[str]
