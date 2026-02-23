# analytics/pnl_feedback.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from infra.logging import get_logger

logger = get_logger("analytics.pnl_feedback")


@dataclass
class TradeRecord:
    symbol: str
    pnl: float       # realized PnL in rupees or R-units
    ts_ns: int       # timestamp (ns) or epoch ms/seconds


class PnLFeedbackSource:
    """
    Aggregates recent PnL per symbol into a bounded feedback score in [-1, +1].

    Intended to be fed with recent trades from your OrderManager / Broker
    layer, and queried by AdvancedScreeningEngine.
    """

    def __init__(
        self,
        lookback_trades: int = 200,
        max_abs_score: float = 1.0,
    ) -> None:
        self._lookback_trades = lookback_trades
        self._max_abs_score = max_abs_score
        self._trades: List[TradeRecord] = []

    def ingest_trades(self, trades: Iterable[TradeRecord]) -> None:
        self._trades.extend(trades)
        # Trim to last N trades for memory control
        if len(self._trades) > 5_000:
            self._trades = self._trades[-5_000:]

    def get_symbol_pnl_score(self, symbol: str) -> float:
        """
        Compute a simple feedback score based on the last `lookback_trades`
        trades for the given symbol.

        Example heuristic:
          - Compute mean PnL over last N trades.
          - Scale by a robust denominator to map into [-1, +1].
        """
        sym_trades = [t for t in self._trades if t.symbol == symbol]
        if not sym_trades:
            return 0.0

        recent = sym_trades[-self._lookback_trades :]
        pnl_values = [t.pnl for t in recent]
        mean_pnl = sum(pnl_values) / max(len(pnl_values), 1)

        # Robust scaling: dividing by (|pnl| + 1) to keep within [-1,1]
        denom = abs(mean_pnl) + 1.0
        raw_score = mean_pnl / denom

        # Clamp to [-max_abs_score, +max_abs_score]
        if raw_score > self._max_abs_score:
            return self._max_abs_score
        if raw_score < -self._max_abs_score:
            return -self._max_abs_score
        return raw_score
