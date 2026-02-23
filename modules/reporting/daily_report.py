def daily_trading_report(*, trades, allocations):
    """
    End-of-day operational report.
    """
    return {
        "total_trades": len(trades),
        "gross_pnl": sum(t.pnl for t in trades),
        "max_drawdown": min(t.equity_dd for t in trades),
        "active_strategies": len(allocations),
        "blocked_strategies": [
            sid for sid, w in allocations.items() if w == 0.0
        ],
    }
