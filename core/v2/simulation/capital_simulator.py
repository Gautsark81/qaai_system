from __future__ import annotations
from typing import Iterable, List
from .contracts import CapitalSnapshot


class CapitalSimulator:
    """
    Deterministic capital replay engine.
    NO randomness. NO execution.
    """

    def replay(
        self,
        *,
        starting_capital: float,
        pnl_series: Iterable[float],
    ) -> CapitalSnapshot:
        capital = starting_capital
        peak = starting_capital
        max_dd = 0.0

        for pnl in pnl_series:
            capital += pnl
            peak = max(peak, capital)
            drawdown = (peak - capital) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)

        return CapitalSnapshot(
            starting_capital=starting_capital,
            ending_capital=capital,
            max_drawdown=round(max_dd, 4),
            pnl=capital - starting_capital,
        )
