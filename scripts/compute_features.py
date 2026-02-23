# scripts/compute_features.py
import json
import pandas as pd
from pathlib import Path
from analytics.feature_engine import compute_rolling_features

paths = list(Path("data/trades").glob("paper_trades_*.jsonl"))
rows = []
for p in paths:
    with open(p, "r", encoding="utf8") as fh:
        for line in fh:
            rows.append(json.loads(line))
df = pd.DataFrame(rows)
features = compute_rolling_features(df)
print("Features rows:", len(features))
print(features.head())
features.to_csv("data/features/rolling_features_latest.csv", index=False)
print("Saved data/features/rolling_features_latest.csv")
