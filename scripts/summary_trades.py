# scripts/summary_trades.py
import json
from pathlib import Path
import pandas as pd

paths = sorted(Path("data/trades").glob("paper_trades_*.jsonl"))
rows = []
for p in paths:
    with open(p, "r", encoding="utf8") as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
df = pd.DataFrame(rows)
if df.empty:
    print("No trades found.")
else:
    print("Total trades:", len(df))
    print(df.groupby("strategy_id")["pnl"].agg(["count","sum","mean","std"]).sort_values("count", ascending=False))
    df.to_csv("data/trades/trades_summary.csv", index=False)
    print("Saved summary to data/trades/trades_summary.csv")
