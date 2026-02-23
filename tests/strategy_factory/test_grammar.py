from qaai_system.strategy_factory.grammar import indicator_condition, composite_and


def test_indicator_condition():
    c = indicator_condition("RSI", ">", 60)
    assert c["type"] == "indicator"


def test_composite_and():
    a = indicator_condition("RSI", ">", 60)
    b = indicator_condition("ADX", ">", 20)
    node = composite_and(a, b)
    assert node["type"] == "AND"
    assert len(node["conditions"]) == 2
