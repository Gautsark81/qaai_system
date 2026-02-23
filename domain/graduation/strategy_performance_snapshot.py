from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyPerformanceSnapshot:
    strategy_id: str
    ssr: float
    max_drawdown_pct: float
    live_days: int
    total_trades: int
