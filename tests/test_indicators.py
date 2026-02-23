# tests/test_indicators.py
from data.indicators import sma, ema, rsi, atr, true_range, build_features_from_ohlcv


def test_sma_basic():
    s = [1, 2, 3, 4, 5]
    res = sma(s, 3)
    assert (
        res[0] is None
        and res[1] is None
        and abs(res[2] - 2.0) < 1e-9
        and abs(res[4] - 4.0) < 1e-9
    )


def test_ema_basic():
    s = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    res = ema(s, 3)
    # ensure that later values exist and increase
    assert res[2] is not None and res[-1] is not None
    assert res[-1] > res[2]


def test_rsi_shifted():
    s = [1.0] * 20 + [2.0] * 20
    r = rsi(s, 14)
    # after the shift, RSI should be > 50 (strong gains)
    # find a point after shift where r is available
    val = None
    for x in r:
        if x is not None:
            val = x
    assert val is not None and val > 50


def test_atr_and_tr():
    highs = [10, 11, 12, 13, 14]
    lows = [9, 9, 10, 11, 12]
    closes = [9.5, 10.5, 11.5, 12.5, 13.5]
    tr = true_range(highs, lows, closes)
    assert tr[0] == 1.0
    a = atr(highs, lows, closes, 3)
    # ATR smoothing yields non-none values later
    assert a[2] is not None


def test_build_features_simple():
    ohlcv = [
        {"open": 1, "high": 2, "low": 1, "close": 1.5, "volume": 10},
        {"open": 1.5, "high": 2.5, "low": 1.4, "close": 2.0, "volume": 12},
        {"open": 2.0, "high": 2.3, "low": 1.9, "close": 2.1, "volume": 8},
        {"open": 2.1, "high": 2.5, "low": 2.0, "close": 2.4, "volume": 6},
    ]
    feats = build_features_from_ohlcv(
        ohlcv, ema_periods=[2], rsi_period=2, atr_period=2
    )
    assert "ema_2" in feats and "rsi" in feats and "atr" in feats
    assert len(feats["ema_2"]) == len(ohlcv)
