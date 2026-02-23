import inspect
from core.strategy_aging.snapshot import build_strategy_lifecycle_snapshot


def test_no_execution_authority_present():
    source = inspect.getsource(build_strategy_lifecycle_snapshot).lower()

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for word in forbidden:
        assert word not in source
