# tests/phase_h/test_main_is_pure_bootstrap.py

import inspect
import main


def test_main_contains_no_logic():
    src = inspect.getsource(main).lower()
    forbidden = ("order", "broker", "strategy", "risk", "execute")
    for word in forbidden:
        assert word not in src
