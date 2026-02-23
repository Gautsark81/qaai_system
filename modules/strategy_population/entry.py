from dataclasses import dataclass
from typing import Optional


@dataclass
class PopulationEntry:
    strategy_id: str
    symbol: str
    fitness_score: float
    age_steps: int
    state: str                  # ACTIVE / WARNING
    generation: int
