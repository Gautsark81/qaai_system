import pandas as pd
from modules.strategy.stream_adapter import StreamRuleAdapter
from modules.strategy.base import Signal


def test_streaming_rule_basic():
    cfg = {
        "rules_cfg": {
            "rules": {
                "r_buy": {"op": ">", "col": "price", "val": 100}
            },
            "signals": {
                "buy_sig": {"rule": "r_buy", "value": 1, "priority": 10}
            },
            "aggregation": "priority",
            "default_size": 2.0
        }
    }

    strat = StreamRuleAdapter("stream1", cfg)
    strat.prepare([])

    # tick 1 → no signal
    sigs1 = strat.generate_signals({"symbol": "FOO", "price": 90})
    assert sigs1 == []

    # tick 2 → buy signal
    sigs2 = strat.generate_signals({"symbol": "FOO", "price": 150})
    assert len(sigs2) == 1
    sig = sigs2[0]
    assert isinstance(sig, Signal)
    assert sig.side == "BUY"
    assert sig.size == 2.0


def test_streaming_priority_override():
    cfg = {
        "rules_cfg": {
            "rules": {
                "r_buy": {"op": ">", "col": "p", "val": 10},
                "r_sell": {"op": "<", "col": "p", "val": 5}
            },
            "signals": {
                "buy_sig":  {"rule": "r_buy",  "value": 1,  "priority": 1},
                "sell_sig": {"rule": "r_sell", "value": -1, "priority": 5}
            },
            "aggregation": "priority"
        }
    }

    strat = StreamRuleAdapter("stream2", cfg)
    strat.prepare([])

    # price = 3 triggers sell only (priority 5)
    s = strat.generate_signals({"symbol": "BAR", "p": 3})
    assert len(s) == 1
    assert s[0].side == "SELL"

    # price = 12 triggers buy only
    b = strat.generate_signals({"symbol": "BAR", "p": 12})
    assert len(b) == 1
    assert b[0].side == "BUY"
