# analytics/execution_stats.py

import time
from collections import defaultdict


class ExecutionStatsTracker:
    def __init__(self):
        self.stats = defaultdict(list)
        self.summary = defaultdict(float)

    def record_fill(self, trade_id, order, fill_result, strategy_id):
        now = time.time()
        entry_time = order.get("entry_time")
        latency = now - entry_time if entry_time else 0

        fill_price = fill_result.get("fill_price")
        entry_price = order.get("entry_price")
        slippage = fill_price - entry_price if fill_price and entry_price else 0

        pnl = fill_result.get("pnl", 0)
        status = order.get("status", "unknown")

        self.stats[strategy_id].append(
            {
                "trade_id": trade_id,
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "entry_price": entry_price,
                "fill_price": fill_price,
                "pnl": pnl,
                "latency": latency,
                "slippage": slippage,
                "status": status,
                "timestamp": now,
            }
        )

        self._update_summary(strategy_id, pnl, slippage, latency, status)

    def _update_summary(self, strategy_id, pnl, slippage, latency, status):
        s = self.summary[strategy_id]
        self.summary[strategy_id] = {
            "total_pnl": s.get("total_pnl", 0) + pnl,
            "total_trades": s.get("total_trades", 0) + 1,
            "win_count": s.get("win_count", 0) + (1 if pnl > 0 else 0),
            "slippage_total": s.get("slippage_total", 0) + slippage,
            "latency_total": s.get("latency_total", 0) + latency,
        }

    def get_strategy_report(self, strategy_id):
        s = self.summary[strategy_id]
        total_trades = s.get("total_trades", 0)
        win_rate = s.get("win_count", 0) / total_trades if total_trades else 0
        avg_slippage = s.get("slippage_total", 0) / total_trades if total_trades else 0
        avg_latency = s.get("latency_total", 0) / total_trades if total_trades else 0

        return {
            "strategy_id": strategy_id,
            "total_trades": total_trades,
            "total_pnl": s.get("total_pnl", 0),
            "win_rate": round(win_rate * 100, 2),
            "avg_slippage": round(avg_slippage, 4),
            "avg_latency_sec": round(avg_latency, 4),
        }

    def export_all(self):
        return {"summaries": dict(self.summary), "trades": dict(self.stats)}
