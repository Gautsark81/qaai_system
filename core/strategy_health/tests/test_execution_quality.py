from core.strategy_health.dimensions.execution_quality import (
    ExecutionQualityDimensionEvaluator,
)
from core.strategy_health.contracts.enums import DimensionVerdict


THRESHOLDS = {
    "avg_slippage_warn": 0.002,
    "avg_slippage_bad": 0.005,
    "tail_slippage_bad": 0.01,
    "tail_n": 5,
    "avg_latency_bad": 800,
    "max_latency_bad": 2000,
    "latency_volatility_warn": 400,
    "reject_rate_warn": 0.02,
    "reject_rate_bad": 0.05,
    "partial_rate_bad": 0.10,
    "fail_score_cap": 0.25,
}


def test_clean_execution_passes():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "expected_price": [100] * 20,
            "fill_price": [100.001] * 20,
            "latency_ms": [200] * 20,
            "rejected_orders": 0,
            "total_orders": 20,
            "partial_fills": 0,
        }
    )

    assert result.verdict == DimensionVerdict.PASS
    assert result.score > 0.6


def test_slippage_warns():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "expected_price": [100] * 20,
            "fill_price": [100.004] * 20,
            "latency_ms": [200] * 20,
            "rejected_orders": 0,
            "total_orders": 20,
            "partial_fills": 0,
        }
    )

    assert result.verdict == DimensionVerdict.WARN


def test_tail_slippage_fails():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "expected_price": [100] * 20,
            "fill_price": [100.02] * 5 + [100.001] * 15,
            "latency_ms": [300] * 20,
            "rejected_orders": 0,
            "total_orders": 20,
            "partial_fills": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score <= 0.25


def test_reject_rate_fails():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "expected_price": [100] * 20,
            "fill_price": [100.001] * 20,
            "latency_ms": [300] * 20,
            "rejected_orders": 2,
            "total_orders": 20,
            "partial_fills": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL


def test_latency_spike_fails():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(
        inputs={
            "expected_price": [100] * 20,
            "fill_price": [100.001] * 20,
            "latency_ms": [100] * 19 + [2500],
            "rejected_orders": 0,
            "total_orders": 20,
            "partial_fills": 0,
        }
    )

    assert result.verdict == DimensionVerdict.FAIL


def test_no_execution_data_fails():
    evaluator = ExecutionQualityDimensionEvaluator(thresholds=THRESHOLDS)

    result = evaluator.evaluate(inputs={})

    assert result.verdict == DimensionVerdict.FAIL
