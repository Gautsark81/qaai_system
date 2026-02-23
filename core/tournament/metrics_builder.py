# core/tournament/metrics_builder.py

from typing import Iterable, Dict, List
from core.tournament.metrics_contract import StrategyMetrics


def compute_ssr(win_trades: int, total_trades: int) -> float:
    if total_trades == 0:
        return 0.0
    return win_trades / total_trades


def compute_expectancy(
    win_trades: int,
    loss_trades: int,
    avg_win: float,
    avg_loss: float,
) -> float:
    total = win_trades + loss_trades
    if total == 0:
        return 0.0

    win_rate = win_trades / total
    loss_rate = loss_trades / total
    return (win_rate * avg_win) - (loss_rate * abs(avg_loss))


def build_strategy_metrics(
    *,
    strategy_id: str,
    trades: Iterable,
    equity_curve: List[float],
    symbol_count: int,
    avg_trade_duration: float,
    time_in_market_pct: float,
    avg_win: float,
    avg_loss: float,
    avg_rr: float,
    max_single_loss_pct: float,
    volatility_sensitivity: Dict[str, float] | None = None,
    metrics_version: str = "v1",
) -> StrategyMetrics:

    trades = list(trades)
    total_trades = len(trades)

    win_trades = sum(1 for t in trades if t.pnl > 0)
    loss_trades = sum(1 for t in trades if t.pnl <= 0)

    # max drawdown
    peak = equity_curve[0] if equity_curve else 0.0
    max_dd = 0.0
    for v in equity_curve:
        peak = max(peak, v)
        dd = (peak - v) / peak if peak else 0.0
        max_dd = max(max_dd, dd)

    ssr = compute_ssr(win_trades, total_trades)
    expectancy = compute_expectancy(win_trades, loss_trades, avg_win, avg_loss)

    return StrategyMetrics(
        strategy_id=strategy_id,
        metrics_version=metrics_version,
        computed_at=StrategyMetrics.now_utc(),

        total_trades=total_trades,
        win_trades=win_trades,
        loss_trades=loss_trades,
        ssr=ssr,

        max_drawdown_pct=max_dd * 100.0,
        max_single_loss_pct=max_single_loss_pct,

        avg_rr=avg_rr,
        expectancy=expectancy,

        time_in_market_pct=time_in_market_pct,
        avg_trade_duration=avg_trade_duration,

        volatility_sensitivity=volatility_sensitivity or {},
        symbol_count=symbol_count,
        notes=[],
    )
