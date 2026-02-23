from typing import Iterable, Tuple

from .allocation import MetaAlphaAllocation


class MetaAlphaAllocator:
    """
    Governed, advisory-only capital allocation intelligence.

    - No execution
    - No capital mutation
    - Deterministic
    """

    def __init__(self, max_per_strategy: float) -> None:
        if not (0.0 < max_per_strategy <= 1.0):
            raise ValueError("max_per_strategy must be in (0, 1].")
        self.max_per_strategy = max_per_strategy

    def allocate(
        self,
        strategies: Iterable,
        total_capital: float,
    ) -> Tuple[MetaAlphaAllocation, ...]:
        """
        Produce advisory allocation recommendations.
        """
        strategies = tuple(strategies)

        allocations = []

        # Step 1 — determine eligible strategies
        eligible = []
        for s in strategies:
            if s.health == "UNSTABLE":
                allocations.append(
                    MetaAlphaAllocation(
                        strategy_id=s.strategy_id,
                        recommended_weight=0.0,
                        rationale="UNSTABLE strategy — allocation blocked",
                    )
                )
            else:
                eligible.append(s)

        if not eligible or total_capital <= 0:
            return tuple(allocations)

        # Step 2 — base equal-weight allocation
        base_weight = min(
            self.max_per_strategy,
            total_capital / len(eligible),
        )

        for s in eligible:
            if s.health == "DEGRADING":
                weight = min(base_weight, self.max_per_strategy)
                rationale = (
                    f"DEGRADING strategy capped at {weight:.2f}"
                )
            else:
                weight = base_weight
                rationale = (
                    f"HEALTHY strategy eligible with weight {weight:.2f}"
                )

            allocations.append(
                MetaAlphaAllocation(
                    strategy_id=s.strategy_id,
                    recommended_weight=weight,
                    rationale=rationale,
                )
            )

        # Deterministic ordering
        allocations.sort(key=lambda a: a.strategy_id)

        return tuple(allocations)
