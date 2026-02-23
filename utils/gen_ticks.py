# utils/gen_ticks.py  (or data/utils.py — ensure you patch the correct file)
import time
from typing import List, Dict

def gen_ticks(symbol: str, start: float = None, start_ts: float = None, num_ticks: int = 100, step_s: float = 1.0):
    """
    Generate synthetic tick dicts.

    Accepts both `start` and `start_ts` for backwards compatibility.
    """
    if start_ts is not None and start is None:
        start = start_ts
    if start is None:
        start = time.time()

    ticks = []
    ts = float(start)
    for i in range(num_ticks):
        ticks.append({
            "symbol": symbol,
            "ts": ts,
            "price": 100.0 + (i % 10) * 0.1,
            "size": 1
        })
        ts += step_s
    return ticks
