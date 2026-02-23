"""
Benchmark naive vs pandas vectorized vs optional Numba path for multi-symbol data.

Usage:
  python backtester/benchmark_supercharged.py [num_seconds] [ticks_per_sec] [sma_window] [num_symbols] [--mode MODE] [--workers N]

Modes:
  - naive    : pure Python rolling per-symbol
  - vector   : uses SuperchargedBacktester (pandas vectorized path)
  - numba    : attempts to use the numba accelerated aggregation path (falls back if unavailable)
  - all      : run all three and compare (default)

Example:
  python backtester/benchmark_supercharged.py 3600 1 50 50 --mode all --workers 4
"""
from __future__ import annotations
import time
import argparse
import random
from collections import deque, defaultdict
from typing import List, Dict, Any
import os
import importlib.machinery, importlib.util
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SCB_PATH = os.path.join(THIS_DIR, "supercharged_backtester.py")


def load_local(path):
    loader = importlib.machinery.SourceFileLoader("scb_local", path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


# try to import your repo's SuperchargedBacktester if exists
try:
    scb_mod = load_local(SCB_PATH)
    SuperchargedBacktester = getattr(scb_mod, "SuperchargedBacktester", None)
except Exception:
    SuperchargedBacktester = None

# fast numpy grouping fallback (if present in repo)
from backtester.fast_ohlcv import ohlcv_from_ticks_fast  # type: ignore


def gen_ticks_multi(symbol_count: int, start_ts: float, num_ticks_per_sym: int, step_s: float = 1.0):
    ticks = []
    for s_idx in range(symbol_count):
        sym = f"SYM{s_idx:03d}"
        price = 100.0 + s_idx * 0.1
        ts = start_ts
        for i in range(num_ticks_per_sym):
            price += (random.random() - 0.5) * 0.2
            ticks.append({"symbol": sym, "timestamp": ts, "price": price, "size": 1})
            ts += step_s
    random.shuffle(ticks)
    return ticks


def naive_multi_last(ticks, sma_window):
    s_map = defaultdict(deque)
    sum_map = defaultdict(float)
    last = {}
    for t in ticks:
        sym = t["symbol"]
        p = t["price"]
        dq = s_map[sym]
        dq.append(p)
        sum_map[sym] += p
        if len(dq) > sma_window:
            sum_map[sym] -= dq.popleft()
        if len(dq) > 0:
            last[sym] = sum_map[sym] / len(dq)
    return last


def vectorized_multi_last(ticks, sma_window, mode="auto"):
    if SuperchargedBacktester is None:
        raise RuntimeError("SuperchargedBacktester not found")
    bt = SuperchargedBacktester()
    bt.ingest_ticks(ticks)
    results = {}
    for sym in list(bt._symbol_ticks.keys()):
        bars = bt._ohlcv_from_ticks(sym, 1, mode=mode)
        if getattr(bars, "empty", False):
            results[sym] = None
            continue
        sma = SuperchargedBacktester.sma(bars["close"], sma_window)
        results[sym] = float(sma.iloc[-1])
    return results


def fast_numpy_last(ticks, sma_window):
    by_sym = {}
    for t in ticks:
        by_sym.setdefault(t["symbol"], []).append(t)
    out = {}
    import pandas as pd
    for sym, tks in by_sym.items():
        bars = ohlcv_from_ticks_fast(tks, timeframe_seconds=1)
        if bars.empty:
            out[sym] = None
            continue
        closes = bars["close"]
        if len(closes) < 1:
            out[sym] = None
            continue
        sma = closes.rolling(window=sma_window, min_periods=1).mean()
        out[sym] = float(sma.iloc[-1])
    return out


def _run_mode(mode, ticks, sma_window, workers=1):
    """
    Wrap a mode execution so the benchmark harness can call it uniformly.
    modes:
      - naive
      - vector (vectorized MultiLast)
      - numba  (vectorized with numba mode preference; falls back to vectorized)
      - fast   (fast_numpy_last using fast_ohlcv)
    """
    if mode == "naive":
        return naive_multi_last(ticks, sma_window)
    if mode == "vector":
        return vectorized_multi_last(ticks, sma_window, mode="pandas")
    if mode == "numba":
        # request numba path in the vectorized impl; if not available it will raise and be caught by caller
        return vectorized_multi_last(ticks, sma_window, mode="numba")
    if mode == "fast":
        # allows multiprocessing inside if desired
        if workers > 1:
            # split symbols into chunks and compute in parallel using workers processes
            by_sym = {}
            for t in ticks:
                by_sym.setdefault(t["symbol"], []).append(t)
            items = list(by_sym.items())

            # prepare chunks
            chunk_size = max(1, len(items) // workers)
            chunks = []
            for i in range(0, len(items), chunk_size):
                chunk_items = items[i:i + chunk_size]
                chunk_ticks = []
                for sym, tks in chunk_items:
                    chunk_ticks.extend(tks)
                chunks.append(chunk_ticks)

            out = {}
            with ProcessPoolExecutor(max_workers=workers) as exe:
                futures = [exe.submit(fast_numpy_last, chunk, sma_window) for chunk in chunks]
                for f in as_completed(futures):
                    res = f.result()
                    out.update(res)
            return out
        else:
            return fast_numpy_last(ticks, sma_window)

    raise RuntimeError(f"unknown mode {mode}")


def run_benchmark(num_seconds: int, ticks_per_sec: int, sma_window: int, num_symbols: int, mode: str = "all", workers: int = 1):
    per_sym = int(num_seconds * ticks_per_sec)
    total = num_symbols * per_sym
    print(f"Generating {total} ticks ({num_symbols} symbols × {per_sym} ticks)")
    ticks = gen_ticks_multi(num_symbols, start_ts=time.time(), num_ticks_per_sym=per_sym, step_s=1.0 / ticks_per_sec)

    modes_to_run = []
    if mode == "all":
        modes_to_run = ["naive", "vector", "numba", "fast"]
    else:
        modes_to_run = [mode]

    results = {}
    times = {}

    for m in modes_to_run:
        try:
            t0 = time.perf_counter()
            res = _run_mode(m, ticks, sma_window, workers=workers)
            t1 = time.perf_counter()
            times[m] = t1 - t0
            results[m] = res
            print(f"{m:6s}: {times[m]:.4f}s (results: {len(res)} symbols)")
        except Exception as e:
            times[m] = None
            results[m] = None
            print(f"{m:6s} failed: {e}")

    # Show concise summary
    naive_t = times.get("naive")
    vec_t = times.get("vector")
    numba_t = times.get("numba")
    fast_t = times.get("fast")
    print()
    print("Summary:")
    print(f" Naive   : {naive_t}")
    print(f" Vector  : {vec_t}")
    print(f" Numba   : {numba_t}")
    print(f" Fast    : {fast_t}")
    if naive_t and vec_t:
        try:
            print(f" Speedup (naive/vector): {naive_t / vec_t:.3f}x")
        except Exception:
            pass
    if naive_t and numba_t:
        try:
            print(f" Speedup (naive/numba) : {naive_t / numba_t:.3f}x")
        except Exception:
            pass
    if naive_t and fast_t:
        try:
            print(f" Speedup (naive/fast)  : {naive_t / fast_t:.3f}x")
        except Exception:
            pass

    return {"times": times, "results": results}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("num_seconds", nargs="?", type=int, default=3600)
    p.add_argument("ticks_per_sec", nargs="?", type=int, default=1)
    p.add_argument("sma_window", nargs="?", type=int, default=50)
    p.add_argument("num_symbols", nargs="?", type=int, default=50)
    p.add_argument("--mode", choices=["naive", "vector", "numba", "fast", "all"], default="all")
    p.add_argument("--workers", type=int, default=1, help="Number of worker processes for fast mode")
    args = p.parse_args()
    run_benchmark(args.num_seconds, args.ticks_per_sec, args.sma_window, args.num_symbols, mode=args.mode, workers=args.workers)
