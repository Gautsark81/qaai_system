# tests/test_supercharged_backtester.py
import time
import pandas as pd
from backtester.supercharged_backtester import SuperchargedBacktester

def test_basic_backtester_sma_strategy():
    bt = SuperchargedBacktester()
    now = time.time()
    # create 120 ticks at 1-second intervals for symbol "TST"
    ticks = []
    price = 100.0
    for i in range(120):
        ticks.append({"symbol":"TST","timestamp": now + i, "price": price + (i*0.01), "size": 1})
    bt.ingest_ticks(ticks)

    # strategy: compute SMA(5) and return last SMA and last close
    def strat(sym, bars):
        # compute close series SMA 5
        sma = SuperchargedBacktester.sma(bars["close"], 5)
        return {"last_close": float(bars["close"].iloc[-1]), "last_sma5": float(sma.iloc[-1])}

    res = bt.run_strategy(strat, timeframe_seconds=1)  # 1-sec bars for test
    assert "TST" in res
    assert res["TST"]["last_close"] > 0
    assert res["TST"]["last_sma5"] > 0
