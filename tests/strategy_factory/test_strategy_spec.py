from qaai_system.strategy_factory.spec import StrategySpec


def test_strategy_spec_creation():
    s = StrategySpec()
    d = s.to_dict()
    assert d["strategy_id"]
    assert d["targets"]["min_win_rate"] == 0.80
