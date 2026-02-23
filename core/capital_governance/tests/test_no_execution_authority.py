import inspect

from core.capital_governance.correlation import build_correlation_warnings
from core.capital_governance.concentration import build_concentration_warnings


def test_no_execution_authority_present():
    sources = (
        inspect.getsource(build_correlation_warnings).lower()
        + inspect.getsource(build_concentration_warnings).lower()
    )

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
        assert word not in sources
