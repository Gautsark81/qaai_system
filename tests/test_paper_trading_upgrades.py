import numpy as np
import pandas as pd
import pytest

from qaai_system.paper_trading.sizing import PositionSizer
from qaai_system.paper_trading.scaling import ScaleManager
from qaai_system.paper_trading.feedback import FeedbackLoop
from qaai_system.paper_trading.broker import PaperBroker


def test_position_sizer_basic():
    sizer = PositionSizer(
        risk_pct=0.01, atr_mult=2.0, max_leverage=1.0, min_stop_pct=0.0025
    )
    row = pd.Series({"close": 100.0, "ATR": 2.0})  # stop_distance = max(2,0.25)*2 = 4
    size = sizer.compute_from_row(row, equity=100_000.0)
    assert size == 250  # 1% of 100k = 1000; 1000/4 = 250


def test_scale_manager_monotonic():
    sm = ScaleManager(min_scale=0.5, max_scale=2.0)
    assert sm.multiplier(0.0) == 0.5
    assert sm.multiplier(1.0) == 2.0
    assert sm.multiplier(0.5) == pytest.approx(1.25, rel=1e-6)
    assert sm.multiplier(10.0) == 2.0  # clamped
    assert sm.multiplier(-5.0) == 0.5  # clamped


def test_feedback_loop_updates():
    fb = FeedbackLoop(alpha=0.1)
    start = fb.get("SYM")
    # +1% trade outcome on 10k notional -> small positive nudge
    new = fb.update_after_trade("SYM", realized_pnl=100.0, notional=10_000.0)
    assert new > start
    # -1% trade outcome -> goes down
    new2 = fb.update_after_trade("SYM", realized_pnl=-100.0, notional=10_000.0)
    assert new2 < new


def test_paper_broker_roundtrip_profit_no_noise():
    # Deterministic: disable spread/slippage for this test
    br = PaperBroker(starting_cash=10_000.0, slippage_bps=0, spread_bps=0)
    # buy 50 @ 100 mid
    tr_buy = br.market_buy("SYM", mid_price=100.0, qty=50)
    assert tr_buy.fill_price == 100.0
    # sell 50 @ 102 mid
    tr_sell = br.market_sell("SYM", mid_price=102.0, qty=50)
    assert tr_sell.fill_price == 102.0
    assert tr_sell.realized_pnl == 2.0 * 50
    assert br.realized_pnl == 100.0
    assert br.position("SYM").qty == 0
    assert br.cash == pytest.approx(10_000.0 + 100.0, rel=1e-9)


def test_paper_broker_with_noise_cash_and_equity():
    np.random.seed(0)  # make fill noise reproducible
    br = PaperBroker(starting_cash=5_000.0, slippage_bps=5, spread_bps=10)
    br.market_buy("ABC", mid_price=50.0, qty=50)
    assert br.position("ABC").qty == 50
    # equity must be cash + mtm
    eq = br.equity({"ABC": 50.0})
    assert eq > 0.0
