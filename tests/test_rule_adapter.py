# tests/test_rule_adapter.py
import pandas as pd
from modules.strategy.rule_adapter import RuleEngineAdapter
from modules.strategy.base import Signal

def test_rule_adapter_basic():
    cfg = {
        "rules_cfg": {
            "rules": {
                "r1": {"op": ">", "col": "price", "val": 100}
            },
            "signals": {
                "buy": {"rule": "r1", "value": 1}
            }
        }
    }
    strat = RuleEngineAdapter("rule1", cfg)
    strat.prepare([{"symbol": "FOO", "price": 90}, {"symbol": "FOO", "price": 95}])
    sigs = strat.generate_signals({"symbol": "FOO", "price": 150})
    assert isinstance(sigs, list)
    assert all(isinstance(s, Signal) for s in sigs)
    assert sigs[0].side == "BUY"
