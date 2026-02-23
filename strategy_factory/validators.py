from __future__ import annotations
from typing import Dict, Any, List


class StrategyValidationError(RuntimeError):
    pass


def validate_strategy_spec(spec: Dict[str, Any]) -> None:
    required = [
        "strategy_id",
        "family",
        "timeframe",
        "indicators",
        "entry",
        "exit",
        "risk",
    ]

    for key in required:
        if key not in spec:
            raise StrategyValidationError(f"Missing required field: {key}")

    if not isinstance(spec["entry"], dict):
        raise StrategyValidationError("Entry logic must be dict")

    if not isinstance(spec["exit"], dict):
        raise StrategyValidationError("Exit logic must be dict")

    _validate_logic_tree(spec["entry"])
    _validate_logic_tree(spec["exit"])


def _validate_logic_tree(node: Dict[str, Any]) -> None:
    if "type" not in node:
        raise StrategyValidationError("Logic node missing type")

    t = node["type"]

    if t in ("AND", "OR"):
        conds = node.get("conditions")
        if not conds or not isinstance(conds, list):
            raise StrategyValidationError(f"{t} requires conditions list")
        for c in conds:
            _validate_logic_tree(c)

    elif t == "indicator":
        for k in ("name", "op", "value"):
            if k not in node:
                raise StrategyValidationError(f"Indicator missing {k}")

    elif t == "breakout":
        for k in ("lookback", "direction"):
            if k not in node:
                raise StrategyValidationError(f"Breakout missing {k}")

    else:
        raise StrategyValidationError(f"Unknown logic type: {t}")
