# backtester/benchmark.py
"""
Compatibility shim and benchmark driver.

This file restores the public API expected by older tests:
  - gen_ticks(...)
  - naive_sma_signals(...)
  - vectorized_sma_last(...)

Now returns a float when input ticks only belong to a single symbol (backwards compatible).
"""
from __future__ import annotations
import os
import sys
import time
import random
from typing import List, Dict, Any

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from .benchmark_supercharged import gen_ticks_multi, naive_multi_last, vectorized_multi_last  # type: ignore
except Exception:
    gen_ticks_multi = None
    naive_multi_last = None
    vectorized_multi_last = None


def gen_ticks(*args, **kwargs):
    # (unchanged) - previous compatibility implementation
    if len(args) >= 1 and isinstance(args[0], str):
        symbol = args[0]
        start_ts = kwargs.get("start_ts") if "start_ts" in kwargs else (args[1] if len(args) > 1 else time.time())
        num_ticks = kwargs.get("num_ticks") if "num_ticks" in kwargs else (args[2] if len(args) > 2 else 100)
        step_s = kwargs.get("step_s", args[3] if len(args) > 3 else 1.0)

        ticks = []
        price = 100.0
        ts = float(start_ts)
        import random as _rand
        for _ in range(int(num_ticks)):
            price += (_rand.random() - 0.5) * 0.2
            ticks.append({"symbol": symbol, "timestamp": ts, "price": price, "size": 1})
            ts += float(step_s)
        return ticks

    if len(args) >= 1:
        num_seconds = int(args[0])
        ticks_per_sec = int(args[1]) if len(args) > 1 else 1
        num_symbols = int(args[2]) if len(args) > 2 else 1
    else:
        num_seconds = int(kwargs.get("num_seconds", 3600))
        ticks_per_sec = int(kwargs.get("ticks_per_sec", 1))
        num_symbols = int(kwargs.get("num_symbols", 1))

    if gen_ticks_multi is not None:
        start_ts = time.time()
        per_sym = int(num_seconds * ticks_per_sec)
        return gen_ticks_multi(num_symbols, start_ts, per_sym, step_s=1.0 / max(1, ticks_per_sec))

    ticks = []
    per_sym = int(num_seconds * ticks_per_sec)
    for s_idx in range(num_symbols):
        sym = f"SYM{s_idx:03d}"
        price = 100.0 + s_idx * 0.1
        ts = time.time()
        for i in range(per_sym):
            price += (random.random() - 0.5) * 0.2
            ticks.append({"symbol": sym, "timestamp": ts, "price": price, "size": 1})
            ts += 1.0 / max(1, ticks_per_sec)
    return ticks


def naive_sma_signals(ticks: List[Dict[str, Any]], window: int = 50):
    """
    Naive per-symbol SMA last-value.
    Returns:
      - float when input ticks contain only one symbol
      - dict(symbol -> float) when multiple symbols present
    """
    # Delegation if available
    if naive_multi_last is not None:
        res = naive_multi_last(ticks, window)
        # if single symbol, convert to float
        if isinstance(res, dict) and len(res) == 1:
            return next(iter(res.values()))
        return res

    from collections import defaultdict, deque
    s_map = defaultdict(lambda: deque())
    sum_map = defaultdict(float)
    last_sma = {}
    for t in ticks:
        sym = t["symbol"]
        p = t["price"]
        dq = s_map[sym]
        dq.append(p)
        sum_map[sym] += p
        if len(dq) > window:
            sum_map[sym] -= dq.popleft()
        if len(dq) > 0:
            last_sma[sym] = sum_map[sym] / len(dq)

    if len(last_sma) == 0:
        return 0.0
    if len(last_sma) == 1:
        return next(iter(last_sma.values()))
    return last_sma


def vectorized_sma_last(ticks: List[Dict[str, Any]], window: int = 50):
    """
    Vectorized wrapper. Returns float for single symbol, dict for multiple symbols.
    """
    if vectorized_multi_last is not None:
        res = vectorized_multi_last(ticks, window)
        if isinstance(res, dict) and len(res) == 1:
            return next(iter(res.values()))
        return res
    return naive_sma_signals(ticks, window)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("num_seconds", type=int, nargs="?", default=3600)
    parser.add_argument("ticks_per_sec", type=int, nargs="?", default=1)
    parser.add_argument("sma_window", type=int, nargs="?", default=50)
    parser.add_argument("num_symbols", type=int, nargs="?", default=50)
    args = parser.parse_args()

    ticks = gen_ticks(args.num_seconds, args.ticks_per_sec, args.num_symbols)
    t0 = time.perf_counter()
    naive = naive_sma_signals(ticks, args.sma_window)
    t1 = time.perf_counter()
    vec = vectorized_sma_last(ticks, args.sma_window)
    t2 = time.perf_counter()

    naive_time = t1 - t0
    vec_time = t2 - t1
    speedup = naive_time / vec_time if vec_time > 0 else float("inf")
    print(f"Naive time: {naive_time:.4f}s, Vectorized time: {vec_time:.4f}s, speedup: {speedup:.2f}x")
