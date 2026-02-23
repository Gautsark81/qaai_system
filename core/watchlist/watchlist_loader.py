# core/watchlist/watchlist_loader.py

from pathlib import Path
import json


class WatchlistLoader:
    """
    Loads the most recent generated watchlist.
    """

    def __init__(self, base_path: str = "data/watchlists"):
        self.base_path = Path(base_path)

    def load(self):
        if not self.base_path.exists():
            raise RuntimeError("Watchlist directory does not exist")

        files = sorted(self.base_path.glob("*.json"))
        if not files:
            raise RuntimeError("Watchlist not generated")

        latest = files[-1]
        payload = json.loads(latest.read_text())

        return payload
