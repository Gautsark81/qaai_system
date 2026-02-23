import inspect

from core.institutional_memory.consolidator import build_institutional_memory_snapshot


def test_no_execution_authority_present():
    source = inspect.getsource(build_institutional_memory_snapshot).lower()

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "call(",
        "while",
        "for ",
    ]

    for word in forbidden:
        assert word not in source
