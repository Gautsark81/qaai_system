# tests/test_signal_priority.py
import pandas as pd
from modules.strategy.strategy_factory import StrategyFactory

def test_priority_wins_over_lower_priority():
    df = pd.DataFrame({"x": [10, 2], "y": [0, 0]})
    cfg = {
        "rules": {
            "r_high": {"op": ">", "col": "x", "val": 5},
            "r_low": {"op": ">", "col": "y", "val": -1}
        },
        "signals": {
            # low priority buy (value=1, priority=0)
            "low_buy": {"rule": "r_low", "value": 1, "priority": 0},
            # high priority sell (value=-1, priority=10)
            "high_sell": {"rule": "r_high", "value": -1, "priority": 10}
        },
        # explicit aggregation mode (optional, default is priority)
        "aggregation": "priority"
    }

    sf = StrategyFactory(cfg)
    out = sf.generate_signals(df)
    # Row 0: x>5 True -> high_priority sell should override low_buy -> signal = -1
    assert out.loc[0, "signal"] == -1
    # Row 1: x>5 False, y>-1 True -> only low_buy active -> signal = 1
    assert out.loc[1, "signal"] == 1

def test_priority_tie_sums_then_clips():
    df = pd.DataFrame({"a": [1, 1], "b": [1, 1]})
    cfg = {
        "rules": {
            "r1": {"op": "==", "col": "a", "val": 1},
            "r2": {"op": "==", "col": "b", "val": 1}
        },
        "signals": {
            "sig1": {"rule": "r1", "value": 1, "priority": 5},
            "sig2": {"rule": "r2", "value": 1, "priority": 5}
        },
        "aggregation": "priority"
    }
    sf = StrategyFactory(cfg)
    out = sf.generate_signals(df)
    # Both signals active with equal priority -> summed (1+1) then clipped -> 1
    assert out.loc[0, "signal"] == 1
    assert out.loc[1, "signal"] == 1
