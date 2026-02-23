# tests/guardrails/test_main_is_safe.py

import inspect
import main


def test_main_contains_no_trading_logic():
    src = inspect.getsource(main)
    forbidden = ("order", "trade", "broker", "strategy")
    for word in forbidden:
        assert word not in src.lower()
