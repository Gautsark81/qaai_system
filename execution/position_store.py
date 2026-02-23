import json
import os
from datetime import datetime
from typing import Dict, Any, List


class JSONLPositionStore:
    """
    Simple JSONL-based persistent position store.
    Each line = one position snapshot (symbol, qty, avg_cost, realized_pnl).
    """

    def __init__(self, path: str = "positions.jsonl"):
        self.path = path
        self.positions: Dict[str, Dict[str, Any]] = {}

        if os.path.exists(self.path):
            self.load_positions()

    def load_positions(self) -> Dict[str, Dict[str, Any]]:
        """Load last known state of positions from JSONL file."""
        self.positions = {}
        if not os.path.exists(self.path):
            return self.positions

        with open(self.path, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line.strip())
                    sym = rec["symbol"]
                    self.positions[sym] = rec
                except Exception:
                    continue
        return self.positions

    def save_positions(self) -> None:
        """Persist positions by appending snapshot of current state."""
        with open(self.path, "a") as f:
            ts = datetime.utcnow().isoformat()
            for sym, rec in self.positions.items():
                rec_copy = rec.copy()
                rec_copy["timestamp"] = ts
                f.write(json.dumps(rec_copy) + "\n")

    def update_position(
        self, symbol: str, qty: float, avg_cost: float, realized_pnl: float
    ) -> None:
        """Update in-memory store and persist."""
        self.positions[symbol] = {
            "symbol": symbol,
            "qty": qty,
            "avg_cost": avg_cost,
            "realized_pnl": realized_pnl,
        }
        self.save_positions()

    def all_positions(self) -> List[Dict[str, Any]]:
        """Return list of all stored positions."""
        return list(self.positions.values())
