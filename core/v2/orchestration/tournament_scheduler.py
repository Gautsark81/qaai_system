# core/v2/orchestration/tournament_scheduler.py
from typing import List
from core.v2.intelligence.strategy_scoring import StrategyAlphaScorer
from .contracts import (
    StrategyCandidate,
    BacktestResult,
    TournamentResult,
)


class TournamentScheduler:
    """
    Orchestrates generation → backtest → scoring → ranking
    """

    def __init__(self):
        self._scorer = StrategyAlphaScorer()

    def run(
        self,
        *,
        candidates: List[StrategyCandidate],
        backtest_results: List[BacktestResult],
    ) -> List[TournamentResult]:

        bt_map = {r.strategy_id: r for r in backtest_results}
        results: List[TournamentResult] = []

        for c in candidates:
            bt = bt_map.get(c.strategy_id)
            if not bt:
                continue

            alpha = self._scorer.score(
                strategy_id=c.strategy_id,
                ssr=bt.ssr,
                health=0.8,
                regime_fit=0.7,
                stability=0.5,
            )

            results.append(
                TournamentResult(
                    strategy_id=c.strategy_id,
                    alpha_score=alpha.score,
                    verdict=alpha.verdict,
                )
            )

        return sorted(
            results,
            key=lambda r: r.alpha_score,
            reverse=True,
        )
