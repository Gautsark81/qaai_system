# modules/strategies/intent_validator.py

from modules.strategies.intent import StrategyIntent


def validate_intent(obj) -> StrategyIntent | None:
    if obj is None:
        return None

    if not isinstance(obj, StrategyIntent):
        raise TypeError(
            f"Strategy output must be StrategyIntent or None, got {type(obj)}"
        )

    if obj.side not in ("BUY", "SELL"):
        raise ValueError("Invalid intent side")

    if not (0.0 <= obj.confidence <= 1.0):
        raise ValueError("Confidence must be between 0 and 1")

    return obj
