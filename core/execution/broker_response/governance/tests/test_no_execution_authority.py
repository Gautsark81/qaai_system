import inspect

from core.execution.broker_response.governance.classifier import ResponseClassifier


def test_classifier_has_no_execution_authority():
    source = inspect.getsource(ResponseClassifier).lower()

    forbidden = [
        "execute",
        "retry",
        "sleep",
        "call",
        "broker(",
    ]

    for word in forbidden:
        assert word not in source
