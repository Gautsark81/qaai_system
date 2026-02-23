from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CapitalStep:
    stage: str
    capital: float


def simulate_capital_scale(
    initial_capital: float,
    steps: int,
    multiplier: float,
    cap: float,
) -> List[CapitalStep]:

    result = []
    capital = initial_capital

    for i in range(steps):
        capital = min(capital * multiplier, cap)
        result.append(
            CapitalStep(stage=f"STEP_{i+1}", capital=capital)
        )

    return result
