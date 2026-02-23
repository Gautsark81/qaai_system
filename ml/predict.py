"""
Simple deterministic prediction generator for Phase-3.
This is intentionally lightweight and deterministic (seeded) so tests are stable.
"""

import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from ml.save_predictions import save_predictions_df
from typing import List


DEFAULT_MODEL_VERSION = "phase3-v0.1"


def generate_time_index(
    start: str, end: str, timeframe_minutes: int = 5
) -> List[datetime]:
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    times = []
    cur = start_dt
    while cur <= end_dt:
        times.append(cur)
        cur = cur + timedelta(minutes=timeframe_minutes)
    return times


def make_predictions_for_symbol(
    symbol: str, start: str, end: str, timeframe: str = "5m", seed: int = 42
):
    """
    Returns a pandas.DataFrame with columns:
    symbol, timestamp, timeframe, prediction, probability, model_version
    """
    np.random.seed(seed + abs(hash(symbol)) % 997)  # vary by symbol deterministically
    tf_minutes = int(timeframe.replace("m", ""))
    times = generate_time_index(start, end, tf_minutes)
    n = len(times)
    # generate deterministic pseudo-probabilities and threshold for predictions
    probs = np.clip(np.random.normal(loc=0.5, scale=0.15, size=n), 0.0, 1.0)
    preds = (probs > 0.55).astype(int) - (probs < 0.45).astype(int)  # -1 / 0 / 1 style
    df = pd.DataFrame(
        {
            "symbol": [symbol] * n,
            "timestamp": times,
            "timeframe": [timeframe] * n,
            "prediction": preds,
            "probability": probs,
            "model_version": [DEFAULT_MODEL_VERSION] * n,
        }
    )
    return df


def cli_main():
    parser = argparse.ArgumentParser(
        description="Generate and save predictions to SQLite (Phase-3)."
    )
    parser.add_argument(
        "--symbol", required=True, help="Symbol to generate (e.g. NIFTY)"
    )
    parser.add_argument(
        "--start",
        required=True,
        help="Start ISO datetime (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
    )
    parser.add_argument("--end", required=True, help="End ISO datetime")
    parser.add_argument(
        "--db", required=True, help="SQLite DB path to write predictions"
    )
    parser.add_argument(
        "--meta", required=False, help="Optional path to write metadata JSON"
    )
    parser.add_argument("--timeframe", default="5m", help="Timeframe string like '5m'")
    args = parser.parse_args()

    # basic input validation
    if not os.path.isdir(os.path.dirname(args.db)) and os.path.dirname(args.db) != "":
        os.makedirs(os.path.dirname(args.db), exist_ok=True)

    df = make_predictions_for_symbol(
        args.symbol, args.start, args.end, timeframe=args.timeframe
    )
    save_predictions_df(df, args.db, meta_out=args.meta)
    print(f"Wrote {len(df)} rows for {args.symbol} to {args.db}")


if __name__ == "__main__":
    cli_main()
