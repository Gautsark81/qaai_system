# screening/quality_control.py
from __future__ import annotations
import pandas as pd
from typing import Dict, Tuple


def evaluate_signal_quality(
    df: pd.DataFrame, label_col: str = "actual", pred_col: str = "predicted"
) -> Dict[str, float]:
    """
    Evaluate classification metrics for trading signals.
    - If `label_col` is missing, derive it from `pnl`: (pnl > 0) → 1, else 0
    - If `pred_col` is missing, fill with zeros
    Returns precision/recall/f1 and avg confidence.
    """
    df = df.copy()

    # Derive labels if missing
    if label_col not in df.columns:
        if "pnl" in df.columns:
            df[label_col] = (df["pnl"] > 0).astype(int)
        else:
            df[label_col] = 0

    if pred_col not in df.columns:
        df[pred_col] = 0

    y_true = df[label_col].fillna(0).astype(int)
    y_pred = df[pred_col].fillna(0).astype(int)

    # directional correctness
    true_dir = (y_true != 0).astype(int)
    pred_dir = (y_pred != 0).astype(int)

    tp = int(((true_dir == 1) & (pred_dir == 1)).sum())
    fp = int(((true_dir == 0) & (pred_dir == 1)).sum())
    fn = int(((true_dir == 1) & (pred_dir == 0)).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        (2 * precision * recall / (precision + recall))
        if (precision + recall) > 0
        else 0.0
    )

    avg_confidence = (
        float(df["confidence"].mean()) if "confidence" in df.columns else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "avg_confidence": avg_confidence,
    }


def rolling_quality(
    df: pd.DataFrame,
    window: int = 100,
    label_col: str = "actual",
    pred_col: str = "predicted",
) -> pd.DataFrame:
    """Compute rolling evaluation metrics with a sliding window."""
    rows = []
    for i in range(len(df)):
        start = max(0, i - window + 1)
        sub = df.iloc[start : i + 1]
        m = evaluate_signal_quality(sub, label_col=label_col, pred_col=pred_col)
        rows.append(m)
    return pd.DataFrame(rows)


def auto_tune_thresholds(
    metrics: Dict[str, float],
    current_buy: float,
    current_sell: float,
    step: float = 0.02,
    min_buy: float = 0.55,
    max_buy: float = 0.95,
    min_sell: float = 0.05,
    max_sell: float = 0.45,
) -> Tuple[float, float]:
    """
    Auto-tuner for buy/sell thresholds based on recent metrics.
    Adjusts thresholds conservatively based on precision and recall.
    """
    precision = metrics.get("precision", 0.0)
    recall = metrics.get("recall", 0.0)

    buy = current_buy
    sell = current_sell

    if precision < 0.4:
        buy = min(buy + step, max_buy)
        sell = max(sell - step, min_sell)
    elif recall < 0.4:
        buy = max(buy - step, min_buy)
        sell = min(sell + step, max_sell)
    else:
        buy = buy - (step * 0.1)
        sell = sell + (step * 0.1)

    buy = float(min(max(buy, min_buy), max_buy))
    sell = float(min(max(sell, min_sell), max_sell))

    if buy <= sell:
        buy = max(sell + 0.01, buy + 0.01)
        buy = min(buy, max_buy)

    return buy, sell
