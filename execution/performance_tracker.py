# execution/performance_tracker.py

import logging
from collections import deque
from statistics import mean


class PerformanceTracker:
    def __init__(self, max_history=50, drawdown_threshold=-10000):
        self.logger = logging.getLogger("PerformanceTracker")
        self.max_history = max_history
        self.trade_history = deque(maxlen=max_history)
        self.drawdown_threshold = drawdown_threshold

    def update(self, trade):
        if not trade:
            return

        status = trade.get("status")
        pnl = trade.get("pnl", 0.0)
        strategy_id = trade.get("strategy_id", "default")
        symbol = trade.get("symbol")
        is_win = pnl > 0

        self.trade_history.append(
            {
                "pnl": pnl,
                "status": status,
                "strategy_id": strategy_id,
                "symbol": symbol,
                "is_win": is_win,
            }
        )

        self.logger.info(f"Performance updated: {symbol} | {strategy_id} | PnL={pnl}")

    def win_rate(self):
        wins = sum(1 for t in self.trade_history if t["is_win"])
        total = len(self.trade_history)
        return round(wins / total, 2) if total else 0.0

    def sl_hit_rate(self):
        sl_hits = sum(1 for t in self.trade_history if "sl_hit" in t.get("note", ""))
        total = len(self.trade_history)
        return round(sl_hits / total, 2) if total else 0.0

    def average_pnl(self):
        if not self.trade_history:
            return 0.0
        return round(mean(t["pnl"] for t in self.trade_history), 2)

    def recent_drawdown(self):
        cum_pnl = 0.0
        min_equity = 0.0
        equity = 0.0

        for t in self.trade_history:
            equity += t["pnl"]
            if equity < min_equity:
                min_equity = equity

        return round(min_equity, 2)

    def should_pause_trading(self):
        drawdown = self.recent_drawdown()
        win_rate = self.win_rate()
        sl_rate = self.sl_hit_rate()

        if drawdown <= self.drawdown_threshold:
            self.logger.warning(
                f"🚨 Drawdown triggered: {drawdown} <= {self.drawdown_threshold}"
            )
            return True

        if win_rate < 0.3 and sl_rate > 0.7:
            self.logger.warning(
                f"⚠️ Poor performance detected. Win rate: {win_rate}, SL rate: {sl_rate}"
            )
            return True

        return False

    def get_summary(self):
        return {
            "win_rate": self.win_rate(),
            "average_pnl": self.average_pnl(),
            "drawdown": self.recent_drawdown(),
            "sl_hit_rate": self.sl_hit_rate(),
            "trades_tracked": len(self.trade_history),
            "paused": self.should_pause_trading(),
        }
