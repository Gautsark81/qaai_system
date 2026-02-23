from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class TradeResult:
    symbol: str
    entry_time: str
    exit_time: str
    side: str
    qty: int
    entry_price: float
    exit_price: float
    pnl: float
    reason: str


@dataclass(frozen=True)
class StrategyRunResult:
    strategy_id: str
    symbol: str
    trades: List[TradeResult]
    total_pnl: float
    max_drawdown: float
    trade_count: int
