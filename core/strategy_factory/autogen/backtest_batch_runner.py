# core/strategy_factory/autogen/backtest_batch_runner.py

from dataclasses import dataclass
from typing import List, Callable, Tuple, Optional
from statistics import mean, variance

from .hypothesis_models import StrategyHypothesis
from .candidate_registry import CandidateRegistry
from .candidate_models import CandidateStage


REQUIRED_MEAN_SSR = 80.0
REQUIRED_WORST_SSR = 70.0
MAX_SSR_VARIANCE = 200.0


@dataclass(frozen=True)
class BacktestMetrics:
    ssr: float
    max_drawdown: float
    capital_efficiency: float


@dataclass(frozen=True)
class RobustnessMetrics:
    mean_ssr: float
    worst_ssr: float
    ssr_variance: float
    worst_drawdown: float
    mean_capital_efficiency: float


class DeterministicBacktestBatchRunner:

    def __init__(
        self,
        registry: CandidateRegistry,
        backtest_callable: Callable,
        watchlist: List[str],
        windows: Optional[List[Tuple[str, str]]] = None,
    ):
        self.registry = registry
        self.backtest_callable = backtest_callable
        self.watchlist = sorted(watchlist)
        self.windows = sorted(windows) if windows else None

    def run(self, hypothesis: StrategyHypothesis):

        # --------------------------------------------------
        # Legacy Mode (Step 2A)
        # --------------------------------------------------
        if self.windows is None:

            results: List[BacktestMetrics] = []

            for symbol in self.watchlist:
                metrics = self.backtest_callable(hypothesis, symbol)
                results.append(metrics)

            aggregated = self._aggregate(results)

            if aggregated.ssr >= REQUIRED_MEAN_SSR:
                self.registry.update_stage(
                    hypothesis.hypothesis_id,
                    CandidateStage.BACKTESTED,
                    ssr=aggregated.ssr,
                    max_drawdown=aggregated.max_drawdown,
                )
                return aggregated

            return None

        # --------------------------------------------------
        # Robust Multi-Window Mode (Step 2B)
        # --------------------------------------------------
        window_results: List[BacktestMetrics] = []

        for window in self.windows:

            symbol_results: List[BacktestMetrics] = []

            for symbol in self.watchlist:
                metrics = self.backtest_callable(
                    hypothesis,
                    symbol,
                    window,
                )
                symbol_results.append(metrics)

            aggregated = self._aggregate(symbol_results)
            window_results.append(aggregated)

        robustness = self._aggregate_windows(window_results)

        if self._passes_robustness(robustness):

            self.registry.update_stage(
                hypothesis.hypothesis_id,
                CandidateStage.ROBUST_VALIDATED,
                ssr=robustness.mean_ssr,
                max_drawdown=robustness.worst_drawdown,
            )

            return robustness

        return None

    def _aggregate(self, results: List[BacktestMetrics]) -> BacktestMetrics:

        if not results:
            return BacktestMetrics(0.0, 0.0, 0.0)

        avg_ssr = mean(r.ssr for r in results)
        worst_dd = max(r.max_drawdown for r in results)
        avg_eff = mean(r.capital_efficiency for r in results)

        return BacktestMetrics(
            ssr=round(avg_ssr, 4),
            max_drawdown=round(worst_dd, 4),
            capital_efficiency=round(avg_eff, 6),
        )

    def _aggregate_windows(
        self, window_results: List[BacktestMetrics]
    ) -> RobustnessMetrics:

        ssrs = [r.ssr for r in window_results]

        mean_ssr = mean(ssrs)
        worst_ssr = min(ssrs)
        ssr_var = variance(ssrs) if len(ssrs) > 1 else 0.0
        worst_drawdown = max(r.max_drawdown for r in window_results)
        mean_eff = mean(r.capital_efficiency for r in window_results)

        return RobustnessMetrics(
            mean_ssr=round(mean_ssr, 4),
            worst_ssr=round(worst_ssr, 4),
            ssr_variance=round(ssr_var, 4),
            worst_drawdown=round(worst_drawdown, 4),
            mean_capital_efficiency=round(mean_eff, 6),
        )

    def _passes_robustness(self, metrics: RobustnessMetrics) -> bool:

        return (
            metrics.mean_ssr >= REQUIRED_MEAN_SSR
            and metrics.worst_ssr >= REQUIRED_WORST_SSR
            and metrics.ssr_variance <= MAX_SSR_VARIANCE
        )