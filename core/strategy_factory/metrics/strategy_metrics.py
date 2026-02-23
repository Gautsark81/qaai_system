from __future__ import annotations

from typing import Iterable, Dict


def compute_strategy_ssr(trades: Iterable[Dict]) -> float:
    """
    Compute Strategy Success Ratio (SSR).

    SSR = number of winning trades / total trades

    Rules:
    - pnl > 0 → win
    - pnl <= 0 → loss
    - Deterministic
    - Pure function
    """

    trades = list(trades)

    if not trades:
        return 0.0

    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    total = len(trades)

    return wins / total
