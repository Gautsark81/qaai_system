# core/tournament/metrics_schema.py

from typing import TypedDict, Dict, List


class StrategyMetricsSchema(TypedDict):
    strategy_id: str
    metrics_version: str
    computed_at: str

    total_trades: int
    win_trades: int
    loss_trades: int
    ssr: float

    max_drawdown_pct: float
    max_single_loss_pct: float

    avg_rr: float
    expectancy: float

    time_in_market_pct: float
    avg_trade_duration: float

    volatility_sensitivity: Dict[str, float]
    symbol_count: int
    notes: List[str]
