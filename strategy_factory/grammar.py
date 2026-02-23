from __future__ import annotations
from typing import Dict, Any


def indicator_condition(
    name: str,
    op: str,
    value: float,
) -> Dict[str, Any]:
    return {
        "type": "indicator",
        "name": name,
        "op": op,
        "value": value,
    }


def breakout_condition(
    lookback: int,
    direction: str,
) -> Dict[str, Any]:
    return {
        "type": "breakout",
        "lookback": lookback,
        "direction": direction,
    }


def composite_and(*conditions: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "AND",
        "conditions": list(conditions),
    }


def composite_or(*conditions: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "OR",
        "conditions": list(conditions),
    }
