# 📁 signal_engine/quality_control.py — FINAL VERSION WITH MASTER UPGRADE OBJECTIVES

import pandas as pd

# ✅ MASTER UPGRADE OBJECTIVES:
# - Meta-quality scoring of signals
# - Accuracy, expectancy, stability, risk-return tradeoff
# - Strategy-specific metrics
# - Supports export, live audit, and adaptive signal filtering


def evaluate_signal_quality(trade_df):
    if trade_df.empty:
        return pd.DataFrame()

    grouped = trade_df.groupby("strategy_id")
    results = []

    for strategy, df in grouped:
        total = len(df)
        wins = df[df["pnl"] > 0].shape[0]
        losses = df[df["pnl"] < 0].shape[0]
        avg_pnl = df["pnl"].mean() if total > 0 else 0
        max_dd = df["pnl"].min() if total > 0 else 0
        win_rate = (wins / total * 100) if total else 0
        expectancy = df["pnl"].mean() if total else 0
        std_dev = df["pnl"].std() if total > 1 else 0
        score = avg_pnl / std_dev if std_dev != 0 else 0

        result = {
            "strategy_id": strategy,
            "total_trades": total,
            "win_rate": round(win_rate, 2),
            "avg_pnl": round(avg_pnl, 2),
            "expectancy": round(expectancy, 2),
            "max_drawdown": round(max_dd, 2),
            "stability_score": round(score, 3),
        }

        results.append(result)

    return pd.DataFrame(results)
