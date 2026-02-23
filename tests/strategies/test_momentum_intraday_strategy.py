from strategies.momentum_intraday import MomentumIntradayStrategy


def test_momentum_intraday_basic_buy_sell_logic():
    s = MomentumIntradayStrategy(
        config={
            "min_score": 0.5,
            "base_size": 1.0,
            "max_size": 5.0,
            "inv_vol_target": 0.0,  # disable vol-scaling for this test
            "tag": "TEST_MOM",
        }
    )

    bar = {"open": 100.0, "close": 101.0}

    # BUY: score >= min_score, positive
    features_buy = {"screen_score": 0.6}
    order_buy = s.on_bar("NIFTY", bar, features_buy)
    assert order_buy is not None
    assert order_buy["symbol"] == "NIFTY"
    assert order_buy["side"] == "BUY"
    assert order_buy["qty"] == 1.0
    assert order_buy["meta"]["strategy"] == "TEST_MOM"
    assert order_buy["meta"]["screen_score"] == 0.6

    # SELL: negative score with abs(score) >= min_score
    features_sell = {"screen_score": -1.0}
    order_sell = s.on_bar("NIFTY", bar, features_sell)
    assert order_sell is not None
    assert order_sell["side"] == "SELL"

    # No trade: score below threshold
    features_small = {"screen_score": 0.1}
    order_none = s.on_bar("NIFTY", bar, features_small)
    assert order_none is None


def test_momentum_intraday_inverse_vol_sizing():
    s = MomentumIntradayStrategy(
        config={
            "min_score": 0.0,
            "base_size": 5.0,
            "max_size": 10.0,
            "inv_vol_target": 4.0,  #  size <= 4 / atr
        }
    )

    bar = {"open": 100.0, "close": 101.0}

    # atr=2 => size <= 2.0, but base_size=5 => final size should be 2
    features = {"screen_score": 1.0, "atr": 2.0}
    order = s.on_bar("NIFTY", bar, features)
    assert order is not None
    assert abs(order["qty"] - 2.0) < 1e-9

    # atr=0 (or missing) => no vol adjustment, stays at base_size
    features_no_vol = {"screen_score": 1.0, "atr": 0.0}
    order2 = s.on_bar("NIFTY", bar, features_no_vol)
    assert order2 is not None
    assert abs(order2["qty"] - 5.0) < 1e-9
