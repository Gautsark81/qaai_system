import yaml
from modules.strategy.stream_adapter import StreamRuleAdapter

def test_yaml_loading_example():
    yaml_text = """
aggregation: priority
rules:
  r1:
    op: ">"
    col: "x"
    val: 5
signals:
  buy:
    rule: "r1"
    value: 1
    priority: 10
"""
    cfg = yaml.safe_load(yaml_text)
    strat = StreamRuleAdapter("yaml_test", {"rules_cfg": cfg})
    strat.prepare([])

    # should trigger buy
    sigs = strat.generate_signals({"symbol": "FOO", "x": 10})
    assert len(sigs) == 1
    assert sigs[0].side == "BUY"
