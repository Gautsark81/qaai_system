from dataclasses import dataclass
from typing import Dict
from .models import AllocationResult
from .snapshot import EnsembleSnapshot


@dataclass(frozen=True)
class PortfolioTelemetry:
    total_capital: float
    deployed_capital: float
    deployment_ratio: float
    suspended_capital: float
    suspended_ratio: float
    governance_shrink_total: float
    max_concentration_ratio: float
    active_strategy_count: int
    suspended_strategy_count: int


class PortfolioTelemetryCalculator:

    @staticmethod
    def calculate(
        snapshot: EnsembleSnapshot,
        result: AllocationResult,
    ) -> PortfolioTelemetry:

        total_capital = snapshot.available_capital
        deployed_capital = sum(result.allocations.values())

        deployment_ratio = (
            deployed_capital / total_capital if total_capital > 0 else 0.0
        )

        suspended_capital = total_capital - deployed_capital
        suspended_ratio = (
            suspended_capital / total_capital if total_capital > 0 else 0.0
        )

        governance_shrink_total = sum(result.governance_adjustments.values())

        if deployed_capital > 0:
            max_concentration_ratio = max(
                allocation / deployed_capital
                for allocation in result.allocations.values()
                if allocation > 0
            )
        else:
            max_concentration_ratio = 0.0

        active_strategy_count = sum(
            1 for v in result.allocations.values() if v > 0
        )

        suspended_strategy_count = len(result.suspensions)

        return PortfolioTelemetry(
            total_capital=total_capital,
            deployed_capital=deployed_capital,
            deployment_ratio=deployment_ratio,
            suspended_capital=suspended_capital,
            suspended_ratio=suspended_ratio,
            governance_shrink_total=governance_shrink_total,
            max_concentration_ratio=max_concentration_ratio,
            active_strategy_count=active_strategy_count,
            suspended_strategy_count=suspended_strategy_count,
        )