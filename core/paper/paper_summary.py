# core/paper/paper_summary.py

import json
from pathlib import Path


class PaperSummary:
    """
    Aggregates paper trading results.
    """

    def __init__(self, base_path: str = "data/paper"):
        self.base = Path(base_path)

    def generate(self):
        trades = self.base / "trades.jsonl"
        summary = {
            "total_trades": 0,
            "total_slippage": 0.0,
        }

        if trades.exists():
            for line in trades.read_text().splitlines():
                record = json.loads(line)
                summary["total_trades"] += 1
                summary["total_slippage"] += record["slippage"]

        (self.base / "summary.json").write_text(
            json.dumps(summary, indent=2)
        )
