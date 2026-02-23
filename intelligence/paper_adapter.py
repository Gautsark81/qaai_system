from datetime import datetime

from intelligence.snapshots.snapshot_writer import SnapshotWriter
from intelligence.ssr.ssr_calculator import SSRCalculator


class PaperTradingIntelligenceAdapter:
    def __init__(self):
        self.writer = SnapshotWriter()

    # --------------------------------------------------
    def process_paper_trades(
        self,
        *,
        strategy_id: str,
        strategy_version: str,
        trades: list,
        risk_events,
        execution_stats,
        window_start: datetime,
        window_end: datetime,
    ):
        ssr = SSRCalculator.compute(trades)

        symbol_metrics = {
            "PAPER": {
                "total_trades": ssr.total_trades,
                "successful_trades": ssr.successful_trades,
                "ssr": ssr.ssr,
                "valid": ssr.valid,
            }
        }

        regime_metrics = {
            "NORMAL": {
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
            }
        }

        payload = dict(
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            stage="PAPER",
            window_type="ROLLING",
            window_start=window_start,
            window_end=window_end,
            ssr=ssr.ssr,
            total_trades=ssr.total_trades,
            successful_trades=ssr.successful_trades,
            win_rate=(
                ssr.successful_trades / ssr.total_trades
                if ssr.total_trades > 0
                else 0.0
            ),
            symbol_metrics=symbol_metrics,
            regime_metrics=regime_metrics,
            risk_events=risk_events,
        )

        snapshot = self.writer.write(payload)
        return snapshot, symbol_metrics, regime_metrics
