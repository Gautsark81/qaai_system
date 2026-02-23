import json
from datetime import datetime
from pathlib import Path


class ExplainabilityLogger:
    """
    Minimal JSONL explainability logger.

    CONTRACT (from tests):
    - log_trade(trade_id, features, signal)
    - JSON keys MUST include:
        trade_id
        features
        signal
    """

    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path else None
        self.enabled = self.path is not None

    def log_trade(self, trade_id, features, signal):
        if not self.enabled:
            return None

        record = {
            "ts": datetime.utcnow().isoformat(),
            "trade_id": trade_id,
            "features": features,
            "signal": signal,
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return record
