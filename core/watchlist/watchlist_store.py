import json
from pathlib import Path
from datetime import date, datetime


class WatchlistStore:
    """
    Persists daily watchlists in JSON form.
    Handles serialization hygiene explicitly.
    """

    def __init__(self, base_path: str = "data/watchlists"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _json_safe(self, obj):
        """
        Convert non-JSON-safe objects explicitly.
        """
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return {k: self._json_safe(v) for k, v in obj.__dict__.items()}
        if isinstance(obj, dict):
            return {k: self._json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._json_safe(v) for v in obj]
        return obj

    def save(self, watchlist):
        """
        Persist WatchlistManifest using its actual contract.
        """

        if hasattr(watchlist, "trading_day"):
            trading_day = watchlist.trading_day
        elif hasattr(watchlist, "date"):
            trading_day = watchlist.date
        else:
            trading_day = "unknown_date"

        payload = self._json_safe({
            "trading_day": trading_day,
            "symbols": watchlist.symbols,
            "metadata": getattr(watchlist, "metadata", {}),
        })

        filename = f"{payload['trading_day']}.json"
        daily_path = self.base_path / filename
        daily_path.write_text(json.dumps(payload, indent=2))

    def persist(self, watchlist):
        """
        STEP-7 canonical persistence entrypoint.
        """
        return self.save(watchlist)
