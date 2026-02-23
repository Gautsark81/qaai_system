from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from .ladder import CapitalLadder
from .constraints import CapitalConstraintError


@dataclass(frozen=True)
class CapitalAllocation:
    """
    Immutable record of capital assigned to a model.
    """
    model_id: str
    weight: float
    ladder_step: str
    updated_at: datetime


class CapitalAllocator:
    """
    Assigns capital to models based on a CapitalLadder.

    HARD INVARIANTS:
    - Total allocated capital must never exceed 1.0
    - Allocations are immutable once recorded (append-only semantics)
    - Deterministic behavior for same inputs
    """

    def __init__(self, ladder: CapitalLadder):
        self._ladder = ladder
        self._allocations: Dict[str, CapitalAllocation] = {}

    def _allocate_step(self, step_index: int) -> tuple[str, float]:
        steps = self._ladder.steps()
        try:
            step = steps[step_index]
        except IndexError as e:
            raise CapitalConstraintError(
                f"Invalid ladder step index: {step_index}"
            ) from e

        return step.name, step.weight

    def _total_allocated(self) -> float:
        return sum(a.weight for a in self._allocations.values())

    def assign(self, model_id: str, step_index: int) -> CapitalAllocation:
        ladder_step, weight = self._allocate_step(step_index)

        new_total = self._total_allocated() + weight
        if new_total > 1.0:
            raise CapitalConstraintError(
                f"Total capital allocation exceeded: {new_total:.2f} > 1.0"
            )

        allocation = CapitalAllocation(
            model_id=model_id,
            weight=weight,
            ladder_step=ladder_step,
            updated_at=datetime.utcnow(),
        )

        self._allocations[model_id] = allocation
        return allocation

    def get(self, model_id: str) -> CapitalAllocation | None:
        return self._allocations.get(model_id)

    def all(self) -> Dict[str, CapitalAllocation]:
        """
        Returns all allocations keyed by model_id.
        """
        return dict(self._allocations)
