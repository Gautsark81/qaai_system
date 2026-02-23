# File: scripts/run_auto_watchlist_now.py

from watchlist.auto_watchlist_builder import AutoWatchlistBuilder

if __name__ == "__main__":
    print("🚀 Running Auto-Adaptive Watchlist Builder...")
    builder = AutoWatchlistBuilder()
    builder.update_watchlist()
    print("✅ Done updating watchlist.")
