import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Any


class ExplainabilityLogger:
    """
    Writes one JSON line per trade/decision with features and signal.
    """

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_trade(self, trade_id: str, features: Mapping[str, Any], signal: str):
        entry = {
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
            "trade_id": trade_id,
            "features": dict(features),
            "signal": signal,
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry  # convenient for testing
