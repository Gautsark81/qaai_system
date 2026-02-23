from __future__ import annotations


REGIME_PROFILES = {
    "trend": {
        "rsi_entry": [55, 60, 65],
        "adx_min": [20, 25],
        "ema_fast": [9, 13],
        "ema_slow": [21, 34],
    },
    "range": {
        "rsi_entry": [30, 35, 40],
        "rsi_exit": [60, 65, 70],
        "atr_stop": [1.5, 2.0],
    },
    "breakout": {
        "lookback": [20, 50],
        "atr_filter": [1.2, 1.5],
    },
}
