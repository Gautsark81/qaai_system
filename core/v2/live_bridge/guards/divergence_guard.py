from __future__ import annotations

from datetime import datetime
from typing import List

from core.v2.live_bridge.contracts import LiveGateDecision
from core.v2.live_bridge.shadow.drift_snapshot import DriftSnapshot


class DivergenceGuard:
    """
    Detects divergence between paper and live trading.
    """

    def __init__(
        self,
        *,
        max_pnl_diff: float,
        max_trade_diff: int,
    ):
        self._max_pnl_diff = max_pnl_diff
        self._max_trade_diff = max_trade_diff

    def evaluate(
        self,
        *,
        snapshot: DriftSnapshot,
        now: datetime,
    ) -> LiveGateDecision:
        reasons: List[str] = []

        pnl_diff = abs(snapshot.paper_pnl - snapshot.live_pnl)
        trade_diff = abs(snapshot.paper_trades - snapshot.live_trades)

        if pnl_diff > self._max_pnl_diff:
            reasons.append("pnl_divergence")

        if trade_diff > self._max_trade_diff:
            reasons.append("trade_count_divergence")

        return LiveGateDecision(
            strategy_id=snapshot.strategy_id,
            allowed=len(reasons) == 0,
            reasons=reasons,
            evaluated_at=now,
        )
