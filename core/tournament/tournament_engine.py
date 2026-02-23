# core/tournament/tournament_engine.py

from typing import Dict, List
from core.tournament.tournament_metrics import TournamentMetrics


class TournamentEngine:
    """
    Runs backtests and computes metrics.
    Strategy-agnostic.
    """

    def run_backtest(
        self,
        strategy,
        symbols: List[str],
    ) -> TournamentMetrics:
        total = 0
        wins = 0
        losses = 0

        for symbol in symbols:
            trades = strategy.backtest(symbol)

            for t in trades:
                total += 1
                if t["pnl"] > 0:
                    wins += 1
                else:
                    losses += 1

        return TournamentMetrics(
            total_trades=total,
            winning_trades=wins,
            losing_trades=losses,
        )
