# modules/strategy_tournament/ssr.py

from typing import List
from modules.strategy_tournament.metrics import SymbolMetrics


def compute_ssr(
    symbol_metrics: List[SymbolMetrics],
    max_dd_threshold: float,
) -> float:
    if not symbol_metrics:
        return 0.0

    successes = 0

    for m in symbol_metrics:
        if m.total_pnl > 0 and m.max_drawdown <= max_dd_threshold:
            successes += 1

    return successes / len(symbol_metrics)
