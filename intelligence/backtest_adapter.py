from datetime import datetime
from pathlib import Path

from intelligence.snapshots.snapshot_writer import SnapshotWriter
from intelligence.snapshots.json_storage import JsonLineStorage
from intelligence.ssr.ssr_calculator import SSRCalculator


class BacktestIntelligenceAdapter:
    """
    Phase-19 Backtest Intelligence Adapter
    """

    def __init__(self):
        self.writer = SnapshotWriter(
            JsonLineStorage(Path("intelligence/snapshots/data"))
        )

    # --------------------------------------------------
    def process_backtest(
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

        # 🔑 Symbol identity (TEST_STRATEGY → TEST)
        symbol = strategy_id.split("_")[0]

        symbol_metrics = {
            symbol: {
                "total_trades": ssr.total_trades,
                "successful_trades": ssr.successful_trades,
                "ssr": ssr.ssr,
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
            stage="BACKTEST",
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
