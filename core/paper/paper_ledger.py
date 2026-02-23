import json
from pathlib import Path


class PaperLedger:
    """
    Deterministic paper ledger.
    """

    def __init__(self, base_path="data/paper"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.trades = []

    def record(self, trade: dict):
        self.trades.append(trade)

    def flush(self, run_id: str):
        path = self.base_path / f"paper_trades_{run_id}.json"
        path.write_text(json.dumps(self.trades, indent=2, sort_keys=True))
        return path
