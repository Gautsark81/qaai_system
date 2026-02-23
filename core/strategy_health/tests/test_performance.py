from core.strategy_health.dimensions.performance import PerformanceDimensionEvaluator
from core.strategy_health.contracts.enums import DimensionVerdict


THRESHOLDS = {
    "sharpe_good": 1.5,
    "sharpe_warn": 0.5,
    "win_rate_good": 0.55,
    "drawdown_bad": 0.25,
}


def test_strong_profitable_strategy():
    returns = [0.02] * 50 + [-0.005] * 10

    evaluator = PerformanceDimensionEvaluator(
        thresholds=THRESHOLDS,
        weight=1.0,
    )

    result = evaluator.evaluate(inputs={"returns": returns})

    assert result.verdict == DimensionVerdict.PASS
    assert result.score > 0.6


def test_break_even_choppy_strategy():
    returns = [0.01, -0.01] * 30

    evaluator = PerformanceDimensionEvaluator(
        thresholds=THRESHOLDS,
        weight=1.0,
    )

    result = evaluator.evaluate(inputs={"returns": returns})

    assert result.verdict == DimensionVerdict.WARN
    assert 0.0 <= result.score <= 1.0


def test_losing_strategy_fails():
    returns = [-0.02] * 40

    evaluator = PerformanceDimensionEvaluator(
        thresholds=THRESHOLDS,
        weight=1.0,
    )

    result = evaluator.evaluate(inputs={"returns": returns})

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score < 0.3


def test_drawdown_violation_forces_fail():
    returns = [0.02] * 5 + [-0.1]

    evaluator = PerformanceDimensionEvaluator(
        thresholds=THRESHOLDS,
        weight=1.0,
    )

    result = evaluator.evaluate(inputs={"returns": returns})

    assert result.verdict == DimensionVerdict.FAIL


def test_no_trades_fails_cleanly():
    evaluator = PerformanceDimensionEvaluator(
        thresholds=THRESHOLDS,
        weight=1.0,
    )

    result = evaluator.evaluate(inputs={"returns": []})

    assert result.verdict == DimensionVerdict.FAIL
    assert result.score == 0.0
