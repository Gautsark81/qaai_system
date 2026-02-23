import pytest

from core.dashboard_read.failure_classifier import (
    classify_failure,
    classify_all_failures,
    FailureClassification,
    SEVERITY_INFO,
    SEVERITY_WARN,
    SEVERITY_ERROR,
    SEVERITY_FATAL,
)


def test_classify_import_error_warn():
    f = classify_failure(
        "system_health",
        "ImportError: missing module",
    )

    assert f.severity == SEVERITY_WARN
    assert f.error_type == "ImportError"
    assert f.component == "system_health"


def test_classify_runtime_error_error():
    f = classify_failure(
        "execution_state",
        "RuntimeError: execution failed",
    )

    assert f.severity == SEVERITY_ERROR
    assert f.error_type == "RuntimeError"


def test_classify_value_error_error():
    f = classify_failure(
        "pipeline_state",
        "ValueError: bad config",
    )

    assert f.severity == SEVERITY_ERROR


def test_classify_snapshot_build_error_fatal():
    f = classify_failure(
        "snapshot",
        "SnapshotBuildError: atomicity violated",
    )

    assert f.severity == SEVERITY_FATAL


def test_classify_unknown_error_defaults_to_error():
    f = classify_failure(
        "mystery_component",
        "WeirdFailure happened",
    )

    assert f.severity == SEVERITY_ERROR
    assert f.error_type == "UnknownError"


def test_classify_all_failures_bulk():
    failures = {
        "market_state": "RuntimeError: provider down",
        "execution_state": "ImportError: metrics missing",
    }

    classified = classify_all_failures(failures)

    assert set(classified.keys()) == {"market_state", "execution_state"}
    assert classified["market_state"].severity == SEVERITY_ERROR
    assert classified["execution_state"].severity == SEVERITY_WARN
    assert isinstance(classified["market_state"], FailureClassification)
