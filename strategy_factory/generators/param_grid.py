from __future__ import annotations
from typing import Dict, List
from itertools import product

from qaai_system.strategy_factory.spec import StrategySpec
from qaai_system.strategy_factory.grammar import (
    indicator_condition,
    breakout_condition,
    composite_and,
)


def generate_param_grid(
    *,
    family: str,
    timeframe: str,
    regime: str,
    params: Dict[str, List],
) -> List[StrategySpec]:
    """
    Deterministically generate StrategySpecs
    from a parameter grid.
    """
    keys = list(params.keys())
    values = list(params.values())

    strategies: List[StrategySpec] = []

    for combo in product(*values):
        p = dict(zip(keys, combo))

        # ENTRY LOGIC
        if regime == "trend":
            entry = composite_and(
                indicator_condition("RSI", ">", p["rsi_entry"]),
                indicator_condition("ADX", ">", p["adx_min"]),
            )

            exit = indicator_condition("RSI", "<", 45)

        elif regime == "breakout":
            entry = breakout_condition(
                lookback=p["lookback"],
                direction="up",
            )
            exit = indicator_condition("ATR", "<", p["atr_filter"])

        else:
            continue

        spec = StrategySpec(
            family=family,
            timeframe=timeframe,
            indicators={"params": p},
            entry=entry,
            exit=exit,
            lineage={
                "generator": "param_grid",
                "regime": regime,
                "params": p,
            },
        )

        strategies.append(spec)

    return strategies
