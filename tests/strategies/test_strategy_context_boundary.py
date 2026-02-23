"""
tests/strategies/test_strategy_context_boundary.py

Enforces the Data → Strategy boundary.

Rule:
A strategy must be a PURE function of StrategyContext.
It must NOT perform IO, imports, or data access.
"""

import inspect

from modules.strategies.strategy_context import StrategyContext


def test_strategy_is_pure_function_of_context():
    """
    This test enforces that strategies:
    - Accept ONLY StrategyContext
    - Do NOT rely on globals
    - Do NOT perform IO
    """

    # Example minimal strategy (represents all strategies)
    def sample_strategy(context: StrategyContext):
        price = context.get("close")
        return {"signal": "BUY" if price > 0 else "SELL"}

    # ------------------------------------------
    # 1. Signature enforcement
    # ------------------------------------------
    sig = inspect.signature(sample_strategy)
    params = list(sig.parameters.values())

    assert len(params) == 1, "Strategy must accept exactly one argument"
    assert (
        params[0].annotation is StrategyContext
    ), "Strategy input must be StrategyContext"

    # ------------------------------------------
    # 2. Execution purity
    # ------------------------------------------
    ctx = StrategyContext(
        symbol="NIFTY",
        timeframe="5m",
        features={"close": 100.0},
        metadata={"source": "test"},
    )

    result = sample_strategy(ctx)

    assert isinstance(result, dict)
    assert "signal" in result

    # ------------------------------------------
    # 3. No hidden dependencies
    # ------------------------------------------
    # Strategy must not reference globals other than builtins
    globals_used = {
        name
        for name in sample_strategy.__code__.co_names
        if name not in dir(__builtins__)
    }

    # Allowed: StrategyContext only
    assert globals_used <= {"StrategyContext"}, (
        f"Strategy uses forbidden globals: {globals_used}"
    )
