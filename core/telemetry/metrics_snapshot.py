from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional


MetricSource = Literal["backtest", "paper", "live"]


@dataclass(frozen=True)
class MetricsSnapshot:
    """
    Immutable snapshot of strategy metrics at a point in time.
    Append-only by design.
    """

    strategy_id: str
    source: MetricSource
    ssr: float
    total_trades: int
    max_drawdown: Optional[float]
    avg_rr: Optional[float]
    latency_ms: Optional[float]
    slippage_pct: Optional[float]
    recorded_at: datetime
    version: str = "metrics_v1"

    @staticmethod
    def now(
        *,
        strategy_id: str,
        source: MetricSource,
        ssr: float,
        total_trades: int,
        max_drawdown: Optional[float] = None,
        avg_rr: Optional[float] = None,
        latency_ms: Optional[float] = None,
        slippage_pct: Optional[float] = None,
    ) -> "MetricsSnapshot":
        return MetricsSnapshot(
            strategy_id=strategy_id,
            source=source,
            ssr=ssr,
            total_trades=total_trades,
            max_drawdown=max_drawdown,
            avg_rr=avg_rr,
            latency_ms=latency_ms,
            slippage_pct=slippage_pct,
            recorded_at=datetime.now(timezone.utc),
        )
