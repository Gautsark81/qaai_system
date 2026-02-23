import inspect
from core.capital.allocator import CapitalAllocator


def test_allocator_contains_no_policy_logic():
    source = inspect.getsource(CapitalAllocator)

    forbidden_keywords = [
        "lifecycle",
        "risk",
        "modifier",
        "scale",
        "if ",
        "for ",
        "while ",
        "*",
        "/",
        "+",
        "-",
    ]

    for keyword in forbidden_keywords:
        assert keyword not in source, f"Allocator must not contain '{keyword}'"
