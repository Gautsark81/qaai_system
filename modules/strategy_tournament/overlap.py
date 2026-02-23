# modules/strategy_tournament/overlap.py

from typing import List, Set
from modules.strategy_tournament.result_schema import TradeResult


def trade_overlap_ratio(
    trades_a: List[TradeResult],
    trades_b: List[TradeResult],
) -> float:
    def key(t: TradeResult):
        return (t.symbol, t.entry_time, t.exit_time)

    set_a: Set = {key(t) for t in trades_a}
    set_b: Set = {key(t) for t in trades_b}

    if not set_a or not set_b:
        return 0.0

    overlap = len(set_a & set_b)
    union = len(set_a | set_b)

    return overlap / union
