#!/usr/bin/env python3
"""
CLI demo runner for YAML rule strategies.

Usage:
    python scripts/run_rule_demo.py examples/strategy_rule_example.yaml
"""

import argparse
import os
import sys
import pandas as pd
import yaml

# ---- Add project root to PYTHONPATH ----
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules.strategy.stream_adapter import StreamRuleAdapter

def load_yaml_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Run rule-based strategy YAML demo.")
    parser.add_argument("yaml_path", type=str, help="Path to YAML strategy config")
    args = parser.parse_args()

    cfg = load_yaml_config(args.yaml_path)

    # initialize streaming adapter with YAML config
    strat = StreamRuleAdapter("yaml_demo", {"rules_cfg": cfg})

    # Optional: sample synthetic data for demonstration
    df = pd.DataFrame([
        {"symbol": "TCS", "close_z": 0.5, "volume": 90000},
        {"symbol": "TCS", "close_z": 1.2, "volume": 80000},  # BUY
        {"symbol": "TCS", "close_z": 2.0, "volume": 200000}, # no signal
    ])

    strat.prepare([])

    print("Running YAML strategy:")
    print("-----------------------")
    for row in df.to_dict(orient="records"):
        signals = strat.generate_signals(row)
        print(f"Input: {row} -> Signals: {signals}")


if __name__ == "__main__":
    main()
