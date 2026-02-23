from core.strategy_factory.registry import StrategyRecord
from core.strategy_factory.exceptions import IllegalLifecycleTransition


_ALLOWED = {
    "GENERATED": {"BACKTESTED"},
    "BACKTESTED": {"PAPER"},
    "PAPER": {"LIVE"},
    "LIVE": set(),
}


def promote(record: StrategyRecord, target_state: str):
    current = record.state

    if target_state not in _ALLOWED.get(current, set()):
        raise IllegalLifecycleTransition(
            f"Illegal transition: {current} → {target_state}"
        )

    record.history.append(
        {"from": current, "to": target_state}
    )
    record.state = target_state
