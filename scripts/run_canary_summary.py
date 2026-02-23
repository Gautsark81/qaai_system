"""
STEP-11.2 — Run end-of-day Canary Summary
"""

from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analytics.canary_daily_summary import CanaryDailySummary


if __name__ == "__main__":
    summary_engine = CanaryDailySummary()
    path, summary = summary_engine.generate()

    print("\n📊 CANARY DAILY SUMMARY GENERATED")
    print(f"File: {path}")
    print("\nKEY RESULTS:")
    for k, v in summary.items():
        print(f"{k}: {v}")
