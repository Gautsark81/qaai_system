from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DecayDecision:
    decaying: bool
    reasons: List[str]
