# modules/qnme/genome_numba.py

"""
High-performance GENOME+ implementation.

Stability-first:
- No runtime warnings
- Deterministic entropy calculation
- Safe numerical handling
"""

from typing import Dict, Any, List
import time
import numpy as np
import logging

logger = logging.getLogger(__name__)


class GenomeNumPyEngine:
    def __init__(self, window: int = 2048):
        self.window = window
        self.ts: List[float] = []
        self.prices: List[float] = []
        self.sizes: List[float] = []
        self.sides: List[int] = []
        self.spreads: List[float] = []
        self._last_compute_ts = None

    def on_trade(self, trade: Dict[str, Any]) -> None:
        ts = float(trade.get("ts", time.time() * 1000))
        price = float(trade.get("price", 0.0))
        size = float(trade.get("size", 1.0))
        side = trade.get("side", "B")
        spread = float(trade.get("spread", 0.0))

        self.ts.append(ts)
        self.prices.append(price)
        self.sizes.append(size)
        self.sides.append(1 if side in ("B", "BUY") else -1)
        self.spreads.append(spread)

        if len(self.ts) > self.window:
            self.ts.pop(0)
            self.prices.pop(0)
            self.sizes.pop(0)
            self.sides.pop(0)
            self.spreads.pop(0)

    def compute_genome(self) -> Dict[str, Any]:
        if not self.ts:
            return {
                "genome": {
                    "entropy": 0.0,
                    "avg_dt": 0.0,
                    "volume": 0.0,
                    "imbalance": 0.0,
                }
            }

        ts_arr = np.asarray(self.ts, dtype=np.float64)
        sizes = np.asarray(self.sizes, dtype=np.float64)
        sides = np.asarray(self.sides, dtype=np.int8)
        spreads = np.asarray(self.spreads, dtype=np.float64)

        volume = float(np.sum(sizes))
        imbalance = float(np.sum(sides * sizes))

        dts = np.diff(ts_arr)
        avg_dt = float(np.mean(dts)) if dts.size > 0 else 0.0

        # ---- SAFE ENTROPY (no warnings ever) ----
        if sizes.size > 0:
            hist, _ = np.histogram(sizes, bins="auto")
            total = float(np.sum(hist))
            if total > 0:
                probs = hist / total
                probs = probs[probs > 0]  # remove zeros safely
                entropy = -float(np.sum(probs * np.log2(probs)))
            else:
                entropy = 0.0
        else:
            entropy = 0.0

        p_large = float(np.sum(sizes > 50)) / max(1, sizes.size)
        p_small = float(np.sum(sizes <= 5)) / max(1, sizes.size)
        median_spread = float(np.median(spreads)) if spreads.size > 0 else 0.0

        genome = {
            "entropy": entropy,
            "avg_dt": avg_dt,
            "volume": volume,
            "imbalance": imbalance,
            "liquidity_p_large": p_large,
            "liquidity_p_small": p_small,
            "median_spread": median_spread,
            "n_trades": int(sizes.size),
        }

        self._last_compute_ts = int(time.time() * 1000)
        return {"genome": genome, "ts": self._last_compute_ts}