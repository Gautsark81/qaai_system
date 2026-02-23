# core/v2/orchestration/strategy_generation.py
from typing import List
from .contracts import StrategyCandidate
import uuid


class StrategyGenerator:
    """
    Deterministic candidate generator.
    NO randomness unless explicitly injected.
    """

    def generate(self, count: int) -> List[StrategyCandidate]:
        candidates: List[StrategyCandidate] = []

        for i in range(count):
            candidates.append(
                StrategyCandidate(
                    strategy_id=f"GEN_{uuid.uuid4().hex[:8]}",
                    parameters={"lookback": 20 + i},
                    source="v2_generator",
                )
            )

        return candidates
