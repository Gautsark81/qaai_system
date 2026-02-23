from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StrategyCandidate:
    strategy_id: str
    params: Dict
    generation: int
