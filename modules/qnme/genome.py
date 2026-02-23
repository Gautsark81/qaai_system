# modules/qnme/genome.py
from typing import Dict, Any, List, Deque
from collections import deque, Counter
import math
import statistics
import time

class GenomeEngine:
    """
    Layer 0: Market Genome Engine (GENOME+)
    - Accepts trades / snapshots
    - Produces a 'genome' vector (dict) per time window
    - Lightweight, pure-Python implementation; vectorize later for speed
    """

    def __init__(self, window: int = 256):
        self.window = window
        self.trade_buf: Deque[Dict[str, Any]] = deque(maxlen=window)
        self.book_buf: Deque[Dict[str, Any]] = deque(maxlen=window)  # optional
        self.last_genome_ts = None

    def on_trade(self, trade: Dict[str, Any]) -> None:
        """Append incoming trade. trade keys: ts, size, price, side"""
        if "ts" not in trade:
            trade = dict(trade, ts=int(time.time() * 1000))
        self.trade_buf.append(trade)

    def on_book(self, book_snapshot: Dict[str, Any]) -> None:
        """Append book snapshot; optional"""
        if "ts" not in book_snapshot:
            book_snapshot = dict(book_snapshot, ts=int(time.time() * 1000))
        self.book_buf.append(book_snapshot)

    def _entropy(self, counts: List[int]) -> float:
        total = sum(counts) or 1
        ent = -sum((c / total) * math.log2((c / total) + 1e-12) for c in counts)
        return float(ent)

    def _liquidity_molecule(self) -> Dict[str, float]:
        """
        Example: bucket trade sizes into small/med/large and return proportions
        """
        sizes = [max(1, int(t.get("size", 1))) for t in self.trade_buf]
        hist = Counter(min(100, s) for s in sizes)
        total = sum(hist.values()) or 1
        return {
            "bucket_count": len(hist),
            "p_large": sum(v for k, v in hist.items() if k > 50) / total,
            "p_small": sum(v for k, v in hist.items() if k <= 5) / total,
        }

    def compute_genome(self) -> Dict[str, Any]:
        """
        Compute a small genome vector summarizing recent microstructure.
        Returns a dictionary with keys used by downstream layers.
        """
        trades = list(self.trade_buf)
        if not trades:
            return {"genome": {"entropy": 0.0, "avg_dt": 0.0, "volume": 0.0, "imbalance": 0.0}}

        # entropy of trade-size distribution
        sizes = [max(1, int(t.get("size", 1))) for t in trades]
        cnt = Counter(sizes)
        entropy = self._entropy(list(cnt.values()))

        # inter-trade time statistics (ms)
        deltas = []
        prev = None
        for t in trades:
            if prev is not None:
                deltas.append(max(0, t["ts"] - prev))
            prev = t["ts"]
        avg_dt = float(statistics.mean(deltas)) if deltas else 0.0

        volume = float(sum(t.get("size", 0) for t in trades))
        imbalance = float(sum(1 if t.get("side", "B") == "B" else -1 for t in trades))

        liquidity = self._liquidity_molecule()

        fingerprint = {
            "entropy": entropy,
            "avg_dt": avg_dt,
            "volume": volume,
            "imbalance": imbalance,
            "liquidity_p_large": liquidity["p_large"],
            "liquidity_p_small": liquidity["p_small"],
            "bucket_count": liquidity["bucket_count"],
        }
        self.last_genome_ts = int(time.time() * 1000)
        return {"genome": fingerprint, "ts": self.last_genome_ts}
