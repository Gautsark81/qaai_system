### 📁 FILE: signal/model_auto_selector.py

import pandas as pd
import numpy as np
from typing import List, Dict


def select_best_model(models_log: pd.DataFrame, metric: str = "adjusted_score") -> str:
    if metric not in models_log.columns:
        raise ValueError(f"'{metric}' not found in models_log")

    latest_models = models_log.sort_values(
        "timestamp", ascending=False
    ).drop_duplicates("model_id")
    best_model = latest_models.loc[latest_models[metric].idxmax()]
    return best_model["model_id"]


def evaluate_models(models: List[str], metrics: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(metrics)
    df["model_id"] = models

    df["adjusted_score"] = (
        0.4 * df["win_rate"]
        + 0.3 * df["tp_hit"]
        - 0.2 * df["sl_hit"]
        + 0.1 * np.tanh(df["avg_pnl"] / 100)
    ).round(4)

    df["timestamp"] = pd.Timestamp.now()
    return df[
        [
            "model_id",
            "adjusted_score",
            "win_rate",
            "tp_hit",
            "sl_hit",
            "avg_pnl",
            "timestamp",
        ]
    ]


# Example use:
# models = ["XGBOOST", "LSTM", "STACKED"]
# metrics = [
#     {"win_rate": 0.65, "tp_hit": 0.6, "sl_hit": 0.2, "avg_pnl": 110},
#     {"win_rate": 0.55, "tp_hit": 0.4, "sl_hit": 0.35, "avg_pnl": 80},
#     {"win_rate": 0.6, "tp_hit": 0.5, "sl_hit": 0.25, "avg_pnl": 95}
# ]
# df_scores = evaluate_models(models, metrics)
# best_model_id = select_best_model(df_scores)
