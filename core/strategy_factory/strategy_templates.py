# core/strategy_factory/strategy_templates.py

STRATEGY_ARCHETYPES = {
    "MEAN_REVERSION": {
        "indicators": ["rsi", "zscore"],
        "timeframes": ["5m", "15m"],
    },
    "TREND_FOLLOWING": {
        "indicators": ["ema_fast", "ema_slow", "adx"],
        "timeframes": ["15m", "1h"],
    },
    "BREAKOUT": {
        "indicators": ["donchian", "atr"],
        "timeframes": ["15m", "1h"],
    },
}
