from dataclasses import dataclass
from typing import Dict

from .snapshot import EnsembleSnapshot
from .shadow_ml import ShadowMLComparator
from .ml_guardrail import MLDriftGuardrail


@dataclass(frozen=True)
class ShadowPerformanceResult:
    baseline_return: float
    ml_return: float
    return_delta: float
    baseline_drawdown_proxy: float
    ml_drawdown_proxy: float
    drawdown_delta: float


class ShadowPerformanceComparator:

    @staticmethod
    def compare(
        snapshot: EnsembleSnapshot,
        strategy_returns: Dict[str, float],
    ) -> ShadowPerformanceResult:
        """
        strategy_returns: deterministic mapping of strategy_id -> return %
        """

        # ----------------------------
        # Get baseline & ML allocations
        # ----------------------------
        comparison = ShadowMLComparator.compare(snapshot)

        baseline_alloc = comparison.baseline_allocations

        # Guardrail-safe ML allocation
        ml_alloc = MLDriftGuardrail.safe_allocate(snapshot).allocations

        total_capital = snapshot.available_capital

        def portfolio_return(allocations: Dict[str, float]) -> float:
            total = 0.0
            for sid, allocation in allocations.items():
                weight = allocation / total_capital if total_capital > 0 else 0.0
                strat_ret = strategy_returns.get(sid, 0.0)
                total += weight * strat_ret
            return total

        baseline_ret = portfolio_return(baseline_alloc)
        ml_ret = portfolio_return(ml_alloc)

        # Simple deterministic drawdown proxy:
        # Weighted negative returns magnitude
        def drawdown_proxy(allocations: Dict[str, float]) -> float:
            total = 0.0
            for sid, allocation in allocations.items():
                strat_ret = strategy_returns.get(sid, 0.0)
                if strat_ret < 0:
                    weight = allocation / total_capital if total_capital > 0 else 0.0
                    total += abs(strat_ret) * weight
            return total

        baseline_dd = drawdown_proxy(baseline_alloc)
        ml_dd = drawdown_proxy(ml_alloc)

        return ShadowPerformanceResult(
            baseline_return=baseline_ret,
            ml_return=ml_ret,
            return_delta=ml_ret - baseline_ret,
            baseline_drawdown_proxy=baseline_dd,
            ml_drawdown_proxy=ml_dd,
            drawdown_delta=ml_dd - baseline_dd,
        )