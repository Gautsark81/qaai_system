from qaai_system.strategy_factory.validators import validate_strategy_spec
from qaai_system.strategy_factory.grammar import indicator_condition


def test_valid_strategy_passes():
    spec = {
        "strategy_id": "x",
        "family": "test",
        "timeframe": "5m",
        "indicators": {},
        "entry": indicator_condition("RSI", ">", 60),
        "exit": indicator_condition("RSI", "<", 40),
        "risk": {},
    }

    validate_strategy_spec(spec)
