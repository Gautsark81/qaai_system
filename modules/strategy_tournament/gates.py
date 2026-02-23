# modules/strategy_tournament/gates.py

from typing import List
from modules.strategy_tournament.metrics import SymbolMetrics
from modules.strategy_tournament.aggregations import StrategyMetrics
from modules.strategy_tournament.ssr import compute_ssr
from modules.strategy_tournament.gate_decision import GateDecision


class HardGateEvaluator:
    """
    Enforces non-negotiable strategy quality constraints.
    """

    def __init__(
        self,
        min_trades: int,
        min_ssr: float,
        max_drawdown: float,
    ):
        self.min_trades = min_trades
        self.min_ssr = min_ssr
        self.max_drawdown = max_drawdown

    def evaluate(
        self,
        strategy_metrics: StrategyMetrics,
        symbol_metrics: List[SymbolMetrics],
    ) -> GateDecision:
        failed = []

        # 1️⃣ Minimum trade count (evidence gate)
        if strategy_metrics.total_trades < self.min_trades:
            failed.append(
                f"total_trades<{self.min_trades}"
            )

        # 2️⃣ Strategy Success Ratio (robustness gate)
        ssr = compute_ssr(
            symbol_metrics,
            max_dd_threshold=self.max_drawdown,
        )
        if ssr < self.min_ssr:
            failed.append(
                f"SSR<{self.min_ssr}"
            )

        # 3️⃣ Max drawdown (capital safety gate)
        if strategy_metrics.max_drawdown > self.max_drawdown:
            failed.append(
                f"max_drawdown>{self.max_drawdown}"
            )

        return GateDecision(
            strategy_id=strategy_metrics.strategy_id,
            passed=len(failed) == 0,
            failed_reasons=failed,
        )
