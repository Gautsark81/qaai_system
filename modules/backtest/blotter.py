# backtest/blotter.py
import csv
from pathlib import Path
from typing import Dict, Any, Optional, List
import time


class Blotter:
    """
    Simple CSV blotter for recording orders and fills.
    Columns: timestamp, symbol, side, quantity, price, order_id, fill_status, fill_ts
    """

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or "data/blotter.csv")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "symbol",
                        "side",
                        "quantity",
                        "price",
                        "order_id",
                        "fill_status",
                        "fill_ts",
                    ]
                )

    def record_order(self, order: Dict[str, Any], order_id: Optional[str] = None):
        row = [
            time.time(),
            order.get("symbol"),
            order.get("side"),
            order.get("quantity"),
            order.get("price"),
            order_id or order.get("order_id") or "",
            "SUBMITTED",
            "",
        ]
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def record_fill(self, order: Dict[str, Any], fill: Dict[str, Any]):
        # append a fill row (and mark previous submitted rows as filled is optional)
        row = [
            time.time(),
            order.get("symbol"),
            order.get("side"),
            order.get("quantity"),
            order.get("price"),
            fill.get("order_id") or "",
            fill.get("status") or "filled",
            time.time(),
        ]
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def read(self) -> List[Dict[str, Any]]:
        out = []
        with self.path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                out.append(dict(r))
        return out
