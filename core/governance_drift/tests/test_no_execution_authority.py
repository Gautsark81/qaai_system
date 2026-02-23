import inspect
from core.governance_drift.drift_detector import detect_governance_drift


def test_no_execution_authority_present():
    source = inspect.getsource(detect_governance_drift).lower()

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
