# tests/test_backtester_equivalence.py
import time
from backtester.supercharged_backtester import SuperchargedBacktester
from backtester.benchmark import gen_ticks, naive_sma_signals, vectorized_sma_last

def test_naive_vs_vectorized_small():
    now = time.time()
    ticks = gen_ticks("TST", start_ts=now, num_ticks=500, step_s=1.0)
    sma_window = 20
    naive = naive_sma_signals(ticks, sma_window)
    vector = vectorized_sma_last(ticks, sma_window)
    # allow tiny float diffs
    assert abs((naive or 0.0) - (vector or 0.0)) < 1e-8
