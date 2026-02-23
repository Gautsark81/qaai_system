# File: scripts/generate_signals.py

import os
import sys

# Add root directory to sys.path so we can import modules from project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.signal_engine import SignalEngine

engine = SignalEngine()
symbols = engine.db.fetch_watchlist()

trades_df = engine.run(symbols)

# Save signals to CSV
os.makedirs("data/signals", exist_ok=True)
trades_df.to_csv("data/signals/latest_signals.csv", index=False)

print("✅ Signals generated and saved to data/signals/latest_signals.csv")
