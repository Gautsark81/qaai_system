from __future__ import annotations

from collections import defaultdict
from typing import Dict

from core.v2.paper_trading.pnl.ledger import PnLEntry


class PnLAttribution:
    """
    Aggregates PnL entries by strategy and symbol.
    """

    def by_strategy(self, entries: list[PnLEntry]) -> Dict[str, float]:
        totals: Dict[str, float] = defaultdict(float)
        for e in entries:
            totals[e.strategy_id] += e.delta
        return dict(totals)

    def by_symbol(self, entries: list[PnLEntry]) -> Dict[str, float]:
        totals: Dict[str, float] = defaultdict(float)
        for e in entries:
            totals[e.symbol] += e.delta
        return dict(totals)
