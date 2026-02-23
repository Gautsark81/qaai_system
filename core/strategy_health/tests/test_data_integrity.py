from core.strategy_health.dimensions.data_integrity import (
    DataIntegrityDimensionEvaluator,
)
from core.strategy_health.contracts.enums import DimensionVerdict


THRESHOLDS = {
    "missing_warn": 0.02,
    "missing_bad": 0.10,
    "stale_warn": 0.01,
    "stale_bad": 0.05,
    "outlier_warn": 0.02,
    "outlier_bad": 0.08,
    "clock_skew_warn_ms": 500,
    "clock_skew_bad_ms": 2000,
    "provider_errors_bad": 3,
    "fail_score_cap": 0.25,
}


def test_clean_data_passes():
    evaluator = DataIntegrityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "missing_ratio": 0.0,
            "stale_ratio": 0.0,
            "outlier_ratio": 0.0,
            "clock_skew_ms": 50,
            "provider_errors": 0,
        }
    )

    assert result.verdict == DimensionVerdict.PASS
    assert result.score > 0.7


def test_partial_degradation_warns():
    evaluator = DataIntegrityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "missing_ratio": 0.03,
            "stale_ratio": 0.0,
            "outlier_ratio": 0.01,
            "clock_skew_ms": 200,
            "provider_errors": 0,
        }
    )

    assert result.verdict == DimensionVerdict.WARN


def test_missing_data_fails():
    evaluator = DataIntegrityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "missing_ratio": 0.20,
            "stale_ratio": 0.0,
            "outlier_ratio": 0.0,
            "clock_skew_ms": 100,
            "provider_errors": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score <= 0.25


def test_clock_skew_fails():
    evaluator = DataIntegrityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "missing_ratio": 0.0,
            "stale_ratio": 0.0,
            "outlier_ratio": 0.0,
            "clock_skew_ms": 3000,
            "provider_errors": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL


def test_provider_errors_fail():
    evaluator = DataIntegrityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "missing_ratio": 0.0,
            "stale_ratio": 0.0,
            "outlier_ratio": 0.0,
            "clock_skew_ms": 0,
            "provider_errors": 5,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
