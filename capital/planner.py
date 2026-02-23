from uuid import uuid4
from datetime import datetime

from qaai_system.capital.allocator import CapitalAllocator
from qaai_system.capital.models import (
    CapitalAllocation,
    CapitalAllocationPlan,
)


class CapitalAllocationPlanner:
    def __init__(self):
        self.allocator = CapitalAllocator()

    def build_plan(
        self,
        *,
        snapshots,
        allocatable_capital: float,
        stage: str,
        correlation_map: dict[str, bool],
    ):
        raw = []

        for snap in snapshots:
            weight, status, reason = self.allocator.allocate(
                snapshot=snap,
                correlated=correlation_map.get(snap.strategy_id, False),
            )
            raw.append((snap, weight, status, reason))

        total_weight = sum(w for _, w, _, _ in raw) or 1.0

        allocations = []

        for snap, weight, status, reason in raw:
            capital = round(
                allocatable_capital * (weight / total_weight),
                2,
            )

            allocations.append(
                CapitalAllocation(
                    strategy_id=snap.strategy_id,
                    strategy_version=snap.strategy_version,
                    stage=stage,
                    allocated_capital=capital,
                    weight=weight,
                    status=status,
                    reason=reason,
                )
            )

        return CapitalAllocationPlan(
            allocation_id=uuid4(),
            created_at=datetime.utcnow(),
            total_allocatable_capital=allocatable_capital,
            allocations=allocations,
        )
