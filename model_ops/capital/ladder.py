from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CapitalStep:
    name: str
    weight: float  # fraction of total capital


class CapitalLadder:
    """
    Deterministic capital promotion ladder.

    NOTE:
    - Ladder steps are *possible* allocations
    - They are NOT cumulative
    - Capital safety is enforced by CapitalAllocator + constraints
    """

    def __init__(self, steps: List[CapitalStep]):
        if not steps:
            raise ValueError("Capital ladder must have at least one step")

        for step in steps:
            if step.weight <= 0.0 or step.weight > 1.0:
                raise ValueError("Each ladder step must be in (0.0, 1.0]")

        self._steps = list(steps)

    def step(self, index: int) -> CapitalStep:
        return self._steps[index]

    def steps(self) -> List[CapitalStep]:
        return list(self._steps)
